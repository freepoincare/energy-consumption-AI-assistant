# raw data 업데이트 할 때
  
`energy_raw.csv`(원시 30분 데이터)를 새로 업데이트했을 때, `daily_energy.csv` 갱신, 통계 요약(Summary Statistics) 갱신, 그리고 Google Cloud Firestore 반영이 어떻게 이루어지는지 구조와 실질적인 작업 방법을 정리.

### 1. 현재 시스템의 데이터 갱신 구조
1. `daily_energy.csv` (가공 데이터):
    * `data_service.py`:35-43의 `_ensure_initial_dataset_loaded()`는 서버 구동 시 `data/processed/daily_energy.csv`가 존재하지 않을 때만 `process_raw_file()`을 호출합니다.
    * 따라서 `energy_raw.csv` 파일만 교체했다고 해서 기존의 `daily_energy.csv`가 자동으로 덮어써지지는 않습니다.
2. 요약 통계 (Summary Statistics):
    * `data_service.py`:220-224는 고정된 캐시를 읽는 것이 아니라, 호출되는 시점에 `repository.get_all()`을 통해 현재 저장소에 있는 모든 레코드를 동적으로 읽어 즉시 재계산합니다.
    * 따라서 저장소(`Firestore` 또는 `_mock_store`)의 일별 데이터가 갱신되면 요약 통계는 별도 작업 없이 자동으로 최신 상태로 반영됩니다.
3. Google Cloud Firestore:
    * `Firestore`는 `POST /api/data`나 `PUT /api/data/{id}` 같은 REST API를 호출할 때 실시간으로 기록됩니다.
    * 대용량 원시 CSV를 바꿨을 때는 이 레코드들을 Firestore에 배치(Batch)로 업로드해 주는 파이프라인이 필요합니다.

### 2. energy_raw.csv를 변경했을 때 확실하게 업데이트하는 방법

가장 안전하고 확실한 방법은 전처리 및 Firestore 동기화 스크립트를 실행하는 것입니다.

#### 단계 1: `daily_energy.csv` 재생성 (전처리 실행)

`energy_raw.csv`를 교체한 후 아래 파이썬 한 줄을 실행하면 30분 단위 데이터 검증 및 일별 합산이 다시 수행되어 `daily_energy.csv`가 즉시 갱신됩니다:

```bash
python -c "from app.analysis.preprocessor import process_raw_file; df, report = process_raw_file(); print('Updated daily rows:', len(df))"
```

#### 단계 2: `Google Cloud Firestore` 및 서버 반영

새롭게 생성된 `daily_energy.csv`의 레코드들을 Firestore의 data 컬렉션에 업로드/동기화합니다:

```
python -c "
import pandas as pd
from app.database.firestore import get_firestore_db

db = get_firestore_db()
if db:
    df = pd.read_csv('data/processed/daily_energy.csv')
    batch = db.batch()
    count = 0
    for _, row in df.iterrows():
        doc_id = str(row['date'])
        doc_ref = db.collection('data').document(doc_id)
        data = {
            'id': doc_id,
            'date': doc_id,
            'value': float(row['daily_consumption_kwh']),
            'unit': 'kWh',
            'memo': None,
            'estimated_cost_pence': float(row['estimated_cost_pence']) if pd.notna(row.get('estimated_cost_pence')) else None,
            'estimated_cost_pounds': float(row['estimated_cost_pounds']) if pd.notna(row.get('estimated_cost_pounds')) else None,
            'standing_charge_pence': float(row['standing_charge_pence']) if pd.notna(row.get('standing_charge_pence')) else None,
            'updated_at': None
        }
        batch.set(doc_ref, data, merge=True)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f'Successfully synced {count} records to Firestore!')
else:
    print('Running in local mock mode - records loaded from daily_energy.csv on next server start.')
"
```

#### 단계 3: 백엔드 서버 재시작 (또는 Render 재배포)

* 로컬 환경: 서버(`uvicorn`)를 재시작하면 메모리 저장소(`_mock_store`)가 갱신된 `daily_energy.csv`를 읽어들입니다.
* Render 배포 환경: 변경된 `energy_raw.csv`와 `daily_energy.csv`를 깃에 커밋/푸시하면 배포 과정에서 최신 데이터가 반영됩니다.

### 3. 요약 통계와 AI 어시스턴트의 동작

* 위 과정으로 데이터가 동기화된 후 사용자가 대시보드를 새로고침하거나 AI에게 질문하면:
* `GET /api/data/summary`가 호출되면서 새로운 데이터 기간, 총 소비량, 일평균, 극값(최고/최저일) 등이 실시간으로 다시 계산됩니다.
* AI 어시스턴트 역시 이 최신 요약 JSON을 동적으로 프롬프트에 주입(Context Injection)받아 답변하므로 별도의 프롬프트 수정 없이도 새로운 데이터에 맞춰 즉시 일관된 답변을 제공합니다.

---

### 🔍 Why you only see 2026-09-01 and 2026-09-02 in Firestore

The application uses a hybrid baseline + cloud sync pattern:

1. Historical Baseline (2026-03-01 ~ 2026-08-31):
    * Stored locally in the repository as `daily_energy.csv` (generated from `energy_raw.csv`).
    * When the backend starts up, `data_service.py`:25-65 loads these 184 days into an in-memory baseline store (`self._mock_store`) without uploading all 184 records to Firestore.
2. User-Entered Records (2026-09-01, 2026-09-02, etc.):
    * Whenever you create or edit records via the UI (`POST /api/data`), `data_service.py`:98-126 writes them directly to the Firestore data collection (`db.collection("data").document(record_id).set(...)`).
3. Hybrid Data Merging:
    * When your web app or the AI chatbot queries the data via `data_service.py`:66-81, it takes the in-memory baseline (March–August) and merges any Firestore documents (September 1st & 2nd) on top of it.
    * This ensures the UI and AI have access to the complete timeline (March to September) without incurring 184 unnecessary document writes upon deployment.

### 💡 Should the historical data be uploaded to Firestore?

• Current behavior (Default): Not required. The API and frontend already see all dates seamlessly because of the merge logic in data_service.py:66-81.
• If you prefer all 184 records directly in Firestore: We can run a one-time seeding script to batch write the entire 2026-03-01 to 2026-08-31 dataset into your
Firestore data collection.
