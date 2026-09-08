# YAML vs. JSON

두 플랫폼은 철학과 접근 방식이 다르기 때문에 서로 다른 설정 파일 형식을 기본으로 채택하고 있습니다.
이해하신 내용을 바탕으로 두 플랫폼의 설정 방식을 비교해 드리겠습니다.

## 🏢 Render vs Vercel 설정 파일 비교

| 구분 | Render | Vercel |
|---|---|---|
| 기본 파일명 | render.yaml | vercel.json (또는 vercel.toml, vercel.ts) |
| 데이터 포맷 | YAML (가독성과 인프라 정의 중심) | JSON (웹 생태계 표준 및 프로그래밍 친화) |
| 주요 목적 | 웹 서비스, 백엔드, 데이터베이스 등 서버 인프라 전체를 코드로 관리 (IaC) | 프론트엔드(Next.js 등) 빌드 커맨드, 라우팅, 리다이렉트 및 Edge 서비스 설정 |
| 주석 지원 | 가능 (# 주석 내용 작성 가능) | 불가능 (JSON 표준 사양상 주석을 쓸 수 없음) |

---

## 🤔 왜 각각 다른 포맷을 쓸까요?

## 1. Render가 YAML을 쓰는 이유: "인프라 관리"

Render는 단순 웹서버뿐만 아니라 PostgreSQL 데이터베이스, Redis, 백그라운드 워커 등 복잡한 인프라 덩어리를 통째로 생성하고 관리(Infrastructure as Code)하는 데 특화되어 있습니다.
DevOps와 클라우드 인프라 업계(Kubernetes, Docker Compose 등)에서는 구조가 크고 복잡하며, 설명용 주석(#)을 달아야 하는 경우가 많아 가독성이 높은 YAML을 표준처럼 사용합니다.

## 2. Vercel이 JSON을 쓰는 이유: "프론트엔드 생태계"

Vercel은 자바스크립트/타입스크립트 기반의 프론트엔드 및 풀스택(Next.js 등) 프레임워크 배포에 최적화된 플랫폼입니다.
웹 개발 환경의 패키지 관리 파일인 package.json처럼 자바스크립트 진영은 모든 설정을 JSON으로 주고받는 것이 가장 직관적이고 친숙하기 때문에 vercel.json을 기본으로 채택했습니다.
(최근 Vercel은 코드로 동적 설정을 제어할 수 있는 vercel.ts 파일도 지원하기 시작했습니다).

## 💡 요약

* 백엔드와 DB 등 전체 인프라 조립이 중심인 Render ➡️ YAML (render.yaml)
* 웹 화면과 프론트엔드 라우팅이 중심인 Vercel ➡️ JSON (vercel.json)

---

# vercel.ts 파일

## 1. .ts 확장자가 뭔가요?
.ts는 타입스크립트(TypeScript) 소스 코드 파일의 확장자입니다.
웹의 기본 언어인 자바스크립트(JavaScript, .js)의 단점을 보완하기 위해 마이크로소프트(MS)가 만든 업그레이드 버전 언어라고 생각하시면 됩니다.

* 왜 쓰나요? (타입 안정성): 자바스크립트는 데이터의 종류(숫자, 문자 등)를 엄격하게 검사하지 않아 실행 중에 엉뚱한 에러가 나기 쉽습니다. 반면 타입스크립트는 코드를 실행하기 전에 데이터의 타입을 미리 지정하고 검사하여 오타나 에러를 개발 도중에 완벽하게 잡아냅니다.
* 현재 위상: 현대 웹 개발(특히 프론트엔드) 시장에서 자바스크립트를 밀어내고 사실상 표준(Standard)으로 자리 잡은 필수 언어입니다.

---

## 2. vercel.ts 파일은 뭔가요?

vercel.ts는 Vercel 플랫폼에서 제공하는 차세대 프로그래밍 방식(Programmatic) 설정 파일입니다.
기존의 vercel.json 파일이 단순히 고정된 텍스트만 적을 수 있는 정적(Static) 파일이었다면, vercel.ts는 내부에 코드를 작성해 동적(Dynamic)으로 설정을 조작할 수 있는 파일입니다.

## 💡 vercel.json(기존) vs vercel.ts(신규) 차이점 

1. 동적 로직 제어 (코드 작성 가능):
    * json은 조건문을 쓸 수 없지만, ts 파일은 내부에 자바스크립트/타입스크립트 코드를 쓸 수 있습니다.
    * 예시: 빌드할 때 외부 API에서 데이터를 긁어와서 라우팅 경로를 실시간으로 바꾸거나, 환경 변수(process.env.NODE_ENV)에 따라 서비스 주소를 다르게 지정할 수 있습니다.

2. 오타 방지 및 가이드 기능 (Type Safety):
    * json 파일에서는 속성 이름(예: buildCommand)을 한 글자만 틀려도 배포 에러가 날 때까지 알기 어렵습니다.
    * ts 파일은 코드 에디터(VS Code 등)가 "이 부분의 스펠링이 틀렸습니다"라고 실시간으로 빨간 줄을 그어주며 자동완성 기능을 제공합니다.
   
## 📝 코드 예시로 보기

Vercel 공식 패키지([@vercel/config](https://vercel.com/docs/project-configuration/vercel-ts))를 활용해 작성하는 vercel.ts 파일의 기본적인 모습입니다:

```ts
import { routes, deploymentEnv } from '@vercel/config/v1';import type { VercelConfig } from '@vercel/config/v1';
// 코드가 실행되면서 환경 설정 객체를 동적으로 내보냅니다.export const config: VercelConfig = {
  framework: 'nextjs',
  buildCommand: 'npm run build',
  
  // 타입스크립트 헬퍼 함수를 이용해 오타 없이 안전하게 라우팅 정의
  rewrites: [
    routes.rewrite('/api/(.*)', 'https://backend-server.com')
  ],
  
  redirects: [
    routes.redirect('/old-page', '/new-page', { permanent: true })
  ]
};
```

## ⚠️ 주의할 점

하나의 프로젝트에는 vercel.json 또는 vercel.ts 중 단 하나만 사용해야 하며, 두 파일을 동시에 두면 에러가 발생합니다.