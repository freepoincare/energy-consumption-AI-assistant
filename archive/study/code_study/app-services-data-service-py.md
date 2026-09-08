# app/services/data_service.py

이 코드는 우리 앱의 **'비즈니스 로직(Business Logic)'**과 **'데이터 관리(Data Management)'**를 담당하는 가장 핵심적인 엔진룸입니다. 

라우터(`data.py`)가 "데이터 좀 가져와!"라고 명령하면, 실제로 창고에서 데이터를 꺼내고 가공하는 일을 여기서 다 합니다. 크게 두 부분으로 나뉘어 있어요.

---

### 1. FirestoreEnergyRepository (데이터 창고 관리자)
이 클래스는 데이터베이스(Firestore)와 직접 소통하며 데이터를 넣고 빼는 역할을 합니다.

*   **하이브리드 저장 방식 (Cloud + Local)**:
    *   `_mock_store`라는 메모리 공간을 가지고 있습니다. 
    *   앱이 시작될 때 CSV 파일에서 데이터를 읽어와서 이 메모리에 먼저 채워둡니다.
    *   **장점**: 인터넷이 끊기거나 Firestore 설정이 안 되어 있어도, 기본 데이터로 앱이 중단 없이 돌아갑니다.
*   **초기 데이터 로딩 (`_ensure_initial_dataset_loaded`)**:
    *   원시 데이터(30분 단위)를 일별 데이터로 변환해서 메모리에 올립니다. 
    *   사용자가 처음 앱을 켰을 때 텅 빈 화면이 아니라 기존 데이터가 보이게 해주는 고마운 기능입니다.
*   **CRUD의 실제 구현**:
    *   `create`, `update`, `delete` 시 Firestore와 로컬 메모리(`_mock_store`) 양쪽을 모두 업데이트하여 데이터 일관성을 유지합니다.

### 2. EnergyDataService (서비스 데스크)
라우터가 호출하는 실제 인터페이스입니다. 데이터를 사용자에게 보여주기 좋게 예쁘게 포장합니다.

*   **Pydantic 모델 변환**: 
    *   Repository에서 가져온 가공되지 않은 딕셔너리(`dict`) 데이터를 `EnergyDataResponse` 같은 규격화된 모델로 변환합니다. 
    *   이렇게 하면 데이터 형식이 틀릴 일이 없어 안전합니다.
*   **통계 요약 생성 (`get_summary`)**: 
    *   이게 아주 중요합니다! 저장된 데이터를 **Pandas DataFrame**으로 변환한 뒤, 분석 엔진(`generate_energy_summary`)에 던져서 평균, 최대값, 추세 같은 **AI용 요약본**을 만들어냅니다.

---

### 💡 이 코드의 3가지 "똑똑한 점"

1.  **방어적 프로그래밍 (Resilience)**:
    `try-except` 문이 곳곳에 배치되어 있습니다. DB 연결에 문제가 생겨도 에러를 뿜으며 죽는 게 아니라, "DB는 안 되지만 내 메모리에 있는 데이터라도 보여줄게!"라고 유연하게 대처합니다.

2.  **데이터 전처리 자동화**:
    `to_dataframe` 함수를 통해 복잡한 DB 데이터를 분석하기 좋은 표(Table) 형태로 즉시 변환합니다. 덕분에 AI가 데이터를 분석하기 매우 쉬워집니다.

3.  **관심사의 분리**:
    "데이터를 어떻게 저장할 것인가(Repository)"와 "데이터를 어떻게 서비스할 것인가(Service)"를 분리했습니다. 나중에 Firestore 대신 다른 DB(예: MySQL)로 바꾸고 싶다면 Repository 코드만 수정하면 됩니다.

---

### 🌟 비유로 이해하기
*   **Repository**: 창고 안에서 물건을 쌓고(Create), 찾고(Read), 고치고(Update), 버리는(Delete) **창고지기**입니다. 창고가 잠겨있으면 자기 주머니(Mock Store)에 있는 물건이라도 꺼내줍니다.
*   **Service**: 손님이 찾는 물건을 예쁜 상자에 담아(Pydantic Model) 건네주는 **점원**입니다. 가끔은 물건들을 모아서 "요즘 이 물건이 인기예요"라는 요약 보고서(Summary)도 써줍니다.

이제 데이터가 어떻게 흐르는지 감이 오시나요? 이 흐름의 마지막 단계인 **AI 분석 엔진(`summary.py`)**이나 **AI 챗봇 서비스(`ai_service.py`)**로 넘어가 볼까요? 😊

---

# data_service.py 행별 설명

`app/services/data_service.py` 파일의 라인별 상세 설명입니다.

**주석 및 임포트 (Imports)**

* `"""" ... """`: 이 클래스가 비즈니스 로직을 처리하는 Data Service 레이어이며, 추후 Firestore DB로 교체될 임시 인메모리 저장소임을 명시하는 독스트링(Docstring)입니다.
* `import pandas as pd`: 데이터 가공 및 분석을 위해 Pandas 라이브러리를 임포트합니다.
* `from typing import List, Optional, Dict, Any`: 파이썬 타입 힌팅을 위한 유틸리티를 임포트합니다.
* `from datetime import datetime, timezone`: 생성/수정 시각 처리를 위한 datetime 관련 모듈입니다.
* `from pathlib import Path`: 파일 경로 확인 및 처리를 위한 표준 라이브러리 모듈입니다.
* `from app.models.data_models import (...)`: 이전 단계에서 만든 Pydantic 스키마 모델들을 임포트합니다.
* `from app.analysis.summary import generate_energy_summary`: 데이터프레임을 받아 요약 통계를 생성해주는 분석 함수를 임포트합니다.
* `from app.analysis.preprocessor import process_raw_file`: 원본 파일(raw CSV)을 전처리하여 결과 파일(processed CSV)로 변환해주는 전처리 함수를 임포트합니다.

---

**1. InMemoryEnergyRepository 클래스 (임시 데이터 저장소)**

* `class InMemoryEnergyRepository:`: CSV 파일 데이터를 메모리에 올려두고 CRUD 작업을 수행하는 임시 저장소 클래스입니다.
* `def __init__(self):`: 저장소 초기화 메서드입니다.
* `self._store: Dict[str, Dict[str, Any]] = {}`: 날짜(`date_str`)를 Key로, 해당 날짜의 데이터 Dict를 Value로 저장할 딕셔너리를 선언합니다.
* `self._load_initial_data()`: 인스턴스가 생성될 때 CSV 데이터를 로드하는 메서드를 호출합니다.

**데이터 초기 로딩 로직**

* `def _load_initial_data(self):`: 초기 데이터 로드 메서드 정의입니다.
* `processed_csv = Path("data/processed/daily_energy.csv")`: 가공된 CSV 파일 경로를 설정합니다.
* `if not processed_csv.exists():`: 가공된 CSV가 존재하지 않는 경우 진입합니다.
* `raw_csv = Path("data/raw/energy_raw.csv")`: 원본 데이터 파일 경로를 지정합니다.
* `if raw_csv.exists():`: 원본 파일이 있다면,
* `process_raw_file(str(raw_csv), str(processed_csv))`: 원본을 전처리하여 `daily_energy.csv` 파일을 새로 생성합니다.
* `if processed_csv.exists():`: 가공된 CSV 파일이 존재하면 읽기를 시작합니다.
* `df = pd.read_csv(processed_csv)`: Pandas로 CSV 파일을 읽어옵니다.
* `for _, row in df.iterrows():`: 데이터프레임의 모든 행(row)을 순회합니다.
* `date_str = str(row["date"])`: 날짜 컬럼을 문자열로 추출합니다.
* `val = float(row["daily_consumption_kwh"])`: 사용량 컬럼을 실수(float) 형태로 추출합니다.
* `self._store[date_str] = { ... }`: 메모리 저장소(`_store`)에 날짜를 Key로 레코드 Dict를 생성하여 저장합니다. (`unit`은 `"kWh"`, 생성시각 기록, 수정시각은 `None`)

**저장소 CRUD 메서드**

* `def get_all(self) -> List[Dict[str, Any]]:`: 저장된 모든 데이터를 조회합니다.
* `return sorted(list(self._store.values()), key=lambda x: x["date"])`: 모든 레코드를 날짜 오름차순(시간순)으로 정렬하여 반환합니다.
* `def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:`: ID(날짜)를 기준으로 단일 레코드를 찾습니다. 없으면 `None`을 반환합니다.
* `def create(self, data: EnergyDataCreate) -> Dict[str, Any]:`: 새 데이터를 생성합니다.
* `record_id = data.date`: 날짜 문자열을 레코드 ID로 사용합니다.
* `now_str = datetime.now(timezone.utc).isoformat()`: 현재 UTC 시각을 ISO format 문자열로 가져옵니다.
* `record = { ... }`: 입력받은 `data`를 바탕으로 새 Dict 레코드를 구성하며, 사용량(`value`)은 소수점 4자리로 반올림 처리합니다.
* `self._store[record_id] = record`: 메모리에 저장하고 생성된 레코드를 반환합니다.
* `def update(self, record_id: str, data: EnergyDataUpdate) -> Optional[Dict[str, Any]]:`: 기존 데이터를 수정합니다.
* `if record_id not in self._store: return None`: 존재하지 않는 ID면 `None`을 반환합니다.
* `record = self._store[record_id]`: 기존 레코드를 참조합니다.
* `if data.value is not None:` / `if data.memo is not None:`: 전달된 값만 선택적으로 수정합니다 (PATCH 방식).
* `record["updated_at"] = datetime.now(timezone.utc).isoformat()`: 수정 시각을 현재 UTC로 갱신하고 레코드를 반환합니다.
* `def delete(self, record_id: str) -> bool:`: 데이터를 삭제합니다. 존재하면 `del`로 메모리에서 지우고 `True`, 없으면 `False`를 반환합니다.
* `def to_dataframe(self) -> pd.DataFrame:`: 저장소 데이터를 Pandas DataFrame 형태로 변환합니다 (통계 계산용).
* `if not records: return pd.DataFrame(...)`: 저장된 데이터가 없으면 지정된 컬럼을 가진 빈 DataFrame을 반환합니다.
* `df = df.rename(...)` / `df["is_complete_day"] = True`: 컬럼명을 분석용 이름(`daily_consumption_kwh`)으로 변경하고 완료 플래그를 붙여 데이터프레임을 반환합니다.

---

**2. 저장소 싱글톤 인스턴스 생성**

* `repository = InMemoryEnergyRepository()`: แอป 전체에서 공용으로 사용할 저장소 객체를 딱 하나만 생성(싱글톤 패턴)합니다.

---

**3. EnergyDataService 클래스 (비즈니스 서비스 레이어)**

* `class EnergyDataService:`: 웹 API 컨트롤러(FastAPI)와 데이터 저장소(Repository) 사이를 중계하고, 딕셔너리 데이터를 Pydantic 응답 객체로 변환하는 서비스 클래스입니다.
* `@staticmethod`: 인스턴스 생성 없이 호출할 수 있도록 정적 메서드로 선언합니다.
* `def list_energy_data()`: 전체 목록을 조회하여 Pydantic `EnergyDataListResponse` 형식으로 변환하여 반환합니다.
* `def get_energy_data_by_id(...)`: 단일 건을 조회하여 존재 시 `EnergyDataResponse`로 변환하여 반환합니다.
* `def create_energy_data(...)`: 데이터 생성 후 `EnergyDataResponse` 형태로 변환하여 반환합니다.
* `def update_energy_data(...)`: 데이터 수정 후 성공 시 `EnergyDataResponse` 형태로 변환하여 반환합니다.
* `def delete_energy_data(...)`: 삭제 성공 여부를 `bool` 형태로 반환합니다.
* `def get_summary()`: 저장소 데이터를 DataFrame으로 가져온 뒤 `generate_energy_summary` 함수를 실행하여 집계된 결과를 `SummaryResponse` Pydantic 모델로 변환하여 반환합니다.