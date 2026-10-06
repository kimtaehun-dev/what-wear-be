# PostgreSQL 기본 구조 정리

날씨옷! 프로젝트를 진행하면서 PostgreSQL 화면과 구조가 낯설 수 있으니, 지금 단계에서 꼭 필요한 내용만 간단히 정리한다.

## 1. PostgreSQL의 기본 계층

PostgreSQL은 보통 아래 순서로 구조를 이해하면 된다.

```text
Server
  -> Database
    -> Schema
      -> Table
        -> Row / Column
```

각 계층의 의미는 다음과 같다.

| 계층 | 의미 |
| --- | --- |
| Server | PostgreSQL 프로그램이 실행되는 전체 공간 |
| Database | 하나의 서비스나 프로젝트 데이터를 담는 큰 단위 |
| Schema | Database 안에서 테이블들을 분류하는 논리적 공간 |
| Table | 실제 데이터를 저장하는 표 |
| Row | 테이블에 저장된 한 줄의 데이터 |
| Column | 테이블의 각 항목, 필드 |

## 2. 날씨옷! 프로젝트 예시

현재 프로젝트에서는 대략 이렇게 보면 된다.

```text
Docker PostgreSQL 17
  -> what_to_wear
    -> public
      -> clothes
        -> id
        -> name
        -> min_temperature
        -> max_temperature
```

즉, Docker로 PostgreSQL 17 서버를 실행하고, 그 안에 `what_to_wear` 데이터베이스를 만들고, 기본 schema인 `public` 안에 `clothes` 테이블을 두는 구조다.

## 3. MySQL/MariaDB와 PostgreSQL의 차이

MySQL이나 MariaDB를 먼저 접했다면 PostgreSQL의 `Schema`가 조금 헷갈릴 수 있다.

MySQL/MariaDB에서는 보통 `Database`와 `Schema`를 거의 같은 의미로 사용한다.

```text
MySQL / MariaDB

Server
  -> Database (= Schema)
    -> Table
```

예를 들면 다음과 같다.

```text
MySQL Server
  -> what_to_wear
    -> clothes
```

하지만 PostgreSQL에서는 `Database` 안에 `Schema`가 실제로 한 단계 더 존재한다.

```text
PostgreSQL

Server
  -> Database
    -> Schema
      -> Table
```

예를 들면 다음과 같다.

```text
PostgreSQL Server
  -> what_to_wear
    -> public
      -> clothes
```

그래서 PostgreSQL에서는 나중에 필요하다면 아래처럼 schema를 나누어 관리할 수도 있다.

```text
what_to_wear
  -> public
    -> clothes
  -> auth
    -> users
  -> weather
    -> forecasts
```

다만 지금 단계에서는 schema를 복잡하게 나누기보다 기본값인 `public`을 사용해도 충분하다.

## 4. `public` schema란?

`public`은 PostgreSQL에서 기본으로 제공되는 schema다.

아래처럼 schema 이름 없이 테이블을 만들면:

```sql
CREATE TABLE clothes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
```

PostgreSQL은 보통 이 테이블을 `public` schema 안에 만든다.

즉, 실제 위치는 다음과 같다.

```text
what_to_wear.public.clothes
```

## 5. Schema-qualified table 이름

PostgreSQL에서는 테이블 이름을 schema까지 포함해서 정확히 쓸 수 있다.

```sql
SELECT * FROM public.clothes;
```

여기서:

- `public`은 schema 이름
- `clothes`는 table 이름

즉, `public.clothes`는 "`public` schema 안에 있는 `clothes` 테이블"이라는 뜻이다.

보통은 기본 schema가 `public`이기 때문에 아래처럼 써도 동작한다.

```sql
SELECT * FROM clothes;
```

하지만 나중에 schema가 많아지면 `public.clothes`처럼 정확히 적는 방식이 더 명확할 수 있다.

## 6. DBeaver에서 보이는 구조

DBeaver에서는 PostgreSQL 구조가 대략 다음처럼 보일 수 있다.

```text
PostgreSQL
  -> Databases
    -> what_to_wear
      -> Schemas
        -> public
          -> Tables
            -> clothes
          -> Views
          -> Functions
  -> Roles
  -> Extensions
```

처음에는 많은 항목이 보여서 복잡해 보일 수 있지만, 지금은 아래 흐름만 기억하면 된다.

```text
Databases
  -> what_to_wear
    -> Schemas
      -> public
        -> Tables
          -> clothes
```

## 7. Roles와 Extensions는 지금은 가볍게만

DBeaver나 PostgreSQL 관리 화면에서 `Roles`, `Extensions` 같은 항목도 보일 수 있다.

지금 단계에서는 간단히 이렇게만 이해하면 된다.

| 항목 | 간단한 의미 |
| --- | --- |
| Roles | 사용자, 권한과 관련된 설정 |
| Extensions | PostgreSQL에 추가 기능을 붙이는 기능 |

프로젝트 초반에는 테이블 구조와 기본 SQL에 익숙해지는 것이 더 중요하므로, Roles와 Extensions는 나중에 필요할 때 다시 자세히 보면 된다.

## 8. 지금 꼭 기억할 것

PostgreSQL의 핵심 구조:

```text
Server -> Database -> Schema -> Table -> Row / Column
```

날씨옷! 프로젝트 현재 구조:

```text
Docker PostgreSQL 17 -> what_to_wear -> public -> clothes
```

MySQL/MariaDB와 다른 점:

```text
MySQL/MariaDB: Database와 Schema를 거의 같은 의미로 사용
PostgreSQL: Database 안에 Schema가 한 단계 더 있음
```

테이블을 정확히 부르는 이름:

```text
public.clothes
```

처음에는 이것만 익숙해져도 PostgreSQL 화면을 훨씬 덜 낯설게 볼 수 있다.
