## PostgreSQL 데이터 분류 경계

PostgreSQL의 데이터 구조는 크게 다음과 같이 생각할 수 있다.

```text
PostgreSQL Server
└── Database
    └── Schema
        └── Table
            ├── Column
            └── Row
```

각 계층은 단순히 데이터를 분류하는 크기가 아니라 **서로 다른 종류의 경계**를 의미한다.

| 단위 | 기준 | 핵심 질문 |
|---|---|---|
| Column | 속성 | 기존 데이터 모델의 속성인가? |
| Table | 데이터 모델(Entity) | 별개의 데이터인가? |
| Schema | 논리적/관리 경계 | 여러 테이블을 하나의 영역으로 관리할 이유가 있는가? |
| Database | 시스템/격리 경계 | 독립적으로 운영·관리해야 하는가? |

---

### 1. Column — 데이터의 속성

하나의 Entity가 가지는 속성은 Column으로 표현한다.

예를 들어 `User`라는 하나의 데이터 모델이 있다면:

```text
users
├── id
├── email
├── nickname
└── created_at
```

TypeScript로 생각하면 다음과 비슷하다.

```ts
interface User {
  id: number;
  email: string;
  nickname: string;
  createdAt: Date;
}
```

**판단 기준**

> 기존 Entity의 속성인가?

YES → Column으로 추가하는 것을 먼저 고려한다.

---

### 2. Table — 데이터 모델(Entity)의 경계

서로 다른 종류의 데이터를 표현한다면 별도의 Table로 분리한다.

```text
public
├── users
├── user_preferences
├── clothes
├── weather_forecasts
└── clothing_rules
```

예를 들어:

```ts
interface User {}
interface Clothes {}
interface WeatherForecast {}
```

`User`, `Clothes`, `WeatherForecast`는 서로 다른 Entity이므로 각각의 Table로 표현할 수 있다.

**판단 기준**

> 이것은 기존 Entity와 별개의 데이터 모델인가?

YES → 별도의 Table을 고려한다.

Table 분리는 가장 일반적으로 사용되는 데이터 분리 단위다.

---

### 3. Schema — 논리적/관리 경계

Schema는 하나의 Database 안에서 여러 Table을 **논리적인 영역(namespace)** 으로 묶는 방법이다.

예를 들어 서비스가 커지면서 인증, 날씨, 추천 영역을 명확하게 구분해야 한다면:

```text
what_to_wear
│
├── auth
│   ├── users
│   ├── sessions
│   └── oauth_accounts
│
├── weather
│   ├── forecasts
│   ├── locations
│   └── api_logs
│
└── recommendation
    ├── clothing_rules
    └── recommendation_history
```

SQL에서도 Schema를 명시할 수 있다.

```sql
SELECT * FROM auth.users;

SELECT * FROM weather.forecasts;
```

Schema를 분리할 수 있는 이유에는 다음과 같은 것들이 있다.

- 도메인별 Table 분류
- 이름 충돌 방지
- 영역별 권한 관리
- 관리 책임 구분
- 많은 Table의 논리적인 정리

하지만 **도메인이 다르다는 이유만으로 반드시 Schema를 분리할 필요는 없다.**

작은 서비스에서는 하나의 `public` Schema에서 시작하는 것이 더 단순하다.

**판단 기준**

> 여러 Table을 별도의 논리적 영역으로 묶어야 할 실질적인 이유가 있는가?

YES → Schema 분리를 고려한다.

---

### 4. Database — 시스템/격리 경계

Database는 Schema보다 훨씬 강한 분리 단위다.

예를 들어 하나의 PostgreSQL Server에서도:

```text
PostgreSQL Server
│
├── what_to_wear
├── company_erp
└── analytics
```

처럼 서로 다른 Database를 운영할 수 있다.

Database 분리는 단순히 **"Table이 많아졌다"** 는 이유로 사용하는 것이 아니다.

다음과 같이 독립적으로 관리해야 할 이유가 있을 때 고려한다.

- 독립적인 서비스
- 별도의 데이터 소유권
- 독립적인 권한 관리
- 독립적인 백업/복구 정책
- 장애 격리
- 독립적인 배포 및 운영
- 마이크로서비스별 데이터 소유

예를 들어 마이크로서비스 구조에서는 다음과 같은 설계가 가능하다.

```text
Auth Service
    │
    └── auth_db

Weather Service
    │
    └── weather_db

Recommendation Service
    │
    └── recommendation_db
```

각 서비스가 자신의 Database를 소유하고 다른 서비스가 해당 DB의 Table을 직접 조회하지 않도록 구성할 수 있다.

**판단 기준**

> 이 데이터를 다른 영역과 독립적으로 운영하고 격리해야 하는가?

YES → 별도의 Database를 고려한다.

---

## 분리 기준 요약

새로운 데이터가 필요할 때 다음 순서로 판단할 수 있다.

```text
새로운 데이터
    │
    ▼
기존 Entity의 속성인가?
    │
    ├── YES → Column
    │
    └── NO
         │
         ▼
    별개의 Entity인가?
         │
         ├── YES → Table
         │
         ▼
    여러 Table을 별도의 영역으로
    관리할 필요가 있는가?
         │
         ├── YES → Schema
         │
         ▼
    독립적인 운영/소유/격리가
    필요한 시스템인가?
         │
         └── YES → Database
```

### 핵심

> **Column = Entity의 속성**
>
> **Table = 데이터 모델의 경계**
>
> **Schema = 논리적/관리 영역의 경계**
>
> **Database = 시스템/운영 격리의 경계**

무조건 많이 분리하는 것이 좋은 설계는 아니다.

특별한 이유가 없다면 작은 단위에서 시작하고, **실제 분리할 이유가 생겼을 때 더 강한 경계를 도입한다.**

---

## 날씨옷! 초기 구조

현재 단계에서는 Database나 Schema를 과도하게 분리하지 않고 다음과 같이 시작한다.

```text
PostgreSQL
│
└── what_to_wear                 # Database
    │
    └── public                   # Schema
        │
        ├── users                # Table
        ├── user_preferences
        ├── clothes
        ├── weather_forecasts
        └── clothing_rules
```

서비스가 성장하면서 실제 관리 경계가 필요해지면:

```text
public
   ↓
auth / weather / recommendation Schema
```

등의 분리를 검토하고,

독립적인 서비스 운영 및 데이터 소유권까지 필요해진다면:

```text
하나의 Database
   ↓
서비스별 Database
```

분리를 검토한다.