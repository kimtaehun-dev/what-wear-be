# Docker 개념 정리

## 1. Docker란?

Docker는 **애플리케이션과 실행에 필요한 환경을 패키징하여 어디서 실행하든 최대한 동일하게 동작하도록 만드는 기술**이다.

예를 들어 PostgreSQL을 직접 설치하면 개발자마다 다음과 같은 차이가 발생할 수 있다.

- PostgreSQL 버전
- OS
- 환경변수
- 포트
- 설치된 라이브러리
- 설정 파일

Docker를 사용하면 이러한 실행 환경을 코드로 정의할 수 있다.

---

# 2. Docker의 기본 구조

Docker의 가장 기본적인 흐름은 다음과 같다.

```text
Dockerfile
    ↓ docker build
Docker Image
    ↓ docker run
Docker Container
```

## Dockerfile

**Docker Image를 어떻게 만들지 정의하는 설계도**

예:

```dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["fastapi", "run", "main.py"]
```

---

## Docker Image

애플리케이션을 실행하는 데 필요한 것을 패키징한 결과물이다.

예:

```text
python:3.12
postgres:17
redis:8
weather-api
```

Image 자체가 실행 중인 것은 아니다.

---

## Docker Container

**Image를 기반으로 실제 실행된 인스턴스**

```text
weather-api Image
       │
       ├── Container #1
       ├── Container #2
       └── Container #3
```

하나의 Image로 여러 Container를 실행할 수 있다.

따라서 표현도 다음과 같이 하는 것이 정확하다.

```text
❌ Docker Image가 실행 중이다.

⭕ Docker Container가 실행 중이다.
```

---

# 3. Docker Compose

Docker Compose는 **여러 Container의 구성과 실행 방법을 선언하고 함께 관리하는 도구**이다.

예를 들어 서비스가 다음과 같다면:

```text
FastAPI
PostgreSQL
Redis
```

각각 `docker run`을 실행하는 대신 `compose.yaml`에 선언할 수 있다.

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: what_to_wear
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:8
```

실행:

```bash
docker compose up
```

종료:

```bash
docker compose down
```

### Dockerfile과 Compose의 차이

```text
Dockerfile
→ Image 하나를 어떻게 만들 것인가?

Docker Compose
→ 우리 서비스에 필요한 Container들을
  어떻게 구성하고 함께 실행할 것인가?
```

---

# 4. Port

Docker Container는 기본적으로 격리되어 있다.

Container 내부 FastAPI가 `8000` 포트를 사용한다고 해서 Host의 `localhost:8000`과 자동으로 연결되는 것은 아니다.

```yaml
ports:
  - "8000:8000"
```

의 의미는:

```text
Host                       Container

localhost:8000  ────────→  :8000
     ↑                        ↑
Host Port               Container Port
```

즉:

> Host의 8000번 포트로 들어온 요청을 Container의 8000번 포트로 전달한다.

---

# 5. Docker Network

Network는 **Container끼리 통신할 수 있도록 연결하는 네트워크**이다.

예를 들어:

```text
FastAPI Container
        │
        │
        ▼
PostgreSQL Container
```

Docker Compose에서는 같은 Compose 환경의 서비스들이 기본적으로 네트워크를 통해 서로 통신할 수 있다.

```yaml
services:
  api:
    ...

  db:
    image: postgres:17
```

FastAPI에서 PostgreSQL에 접근할 때:

```text
db:5432
```

처럼 서비스 이름을 사용할 수 있다.

### localhost 주의

FastAPI Container 안에서:

```text
localhost:5432
```

라고 하면 PostgreSQL을 의미하지 않는다.

Container에서 `localhost`는 **자기 자신**이다.

```text
FastAPI Container
       ↑
   localhost
```

따라서 다른 Container인 PostgreSQL에는:

```text
db:5432
```

등으로 접근해야 한다.

---

# 6. Container의 데이터

Container 내부에만 데이터를 저장하면 Container가 제거될 때 데이터도 같이 사라질 수 있다.

```text
Container
├── App
├── Log
└── Data

Container 삭제
      ↓
Data도 삭제
```

따라서 영구적으로 보존해야 하는 데이터는 Container와 분리한다.

대표적인 방법이:

- Volume
- Bind Mount

이다.

---

# 7. Bind Mount

**Host의 특정 디렉터리를 Container 내부 디렉터리와 직접 연결하는 방법**

예:

```yaml
volumes:
  - /data/logs:/app/logs
```

구조:

```text
Host                        Container

/data/logs   ←──────────→   /app/logs
```

Container가:

```text
/app/logs/error.log
```

에 로그를 기록하면 Host에서도:

```text
/data/logs/error.log
```

를 통해 접근할 수 있다.

Container를 제거해도 Host의 `/data/logs`는 유지된다.

### 개념

> Bind Mount = 내가 관리하는 Host 저장공간을 Container에 연결

예전 서버에서 흔히 사용했던 **공유 디렉터리와 비슷한 느낌**으로 이해할 수 있다.

---

# 8. Docker Volume

Volume 역시 Container 외부에 데이터를 저장한다.

차이점은 저장공간을 **Docker가 관리한다는 것**이다.

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

구조:

```text
PostgreSQL Container
        │
        ▼
postgres_data
(Docker가 관리)
```

Container를 삭제해도 Volume은 유지할 수 있다.

```text
기존 PostgreSQL Container
          💥
           │
           ▼
     postgres_data
           │
           ▼
새 PostgreSQL Container
```

새 Container에 동일한 Volume을 연결하면 기존 데이터를 다시 사용할 수 있다.

### Bind Mount와 Volume 비교

```text
Bind Mount
→ 내가 관리하는 외부 저장공간 연결

Volume
→ Docker가 관리하는 외부 저장공간 연결

Container 내부 저장공간
→ Container와 생명주기를 같이하는 공간
```

---

# 9. Docker Desktop

Docker Desktop은 단순한 Docker GUI가 아니다.

특히 macOS에서는 Docker Container를 실행하기 위한 환경까지 제공한다.

Docker Container는 Linux Kernel의 기능을 기반으로 동작한다.

하지만 macOS는 Linux가 아니므로 Docker Desktop 내부에서 Linux 환경을 제공한다.

```text
macOS

Docker Desktop
      │
      ▼
Linux VM
      │
Docker Engine
      │
      ├── PostgreSQL Container
      ├── FastAPI Container
      └── Redis Container
```

Docker Desktop에는 다음과 같은 기능들이 포함된다.

```text
Docker Desktop
├── Docker 실행 환경
├── Docker Engine
├── Docker CLI
├── Docker Compose
└── GUI 관리 기능
```

Git으로 비유하면 Docker Desktop의 GUI 부분은 SourceTree와 비슷하다.

```text
Git                         Docker

Git                         Docker Engine
git CLI                     Docker CLI
SourceTree                  Docker Desktop GUI
```

다만 Docker Desktop은 SourceTree와 달리 Mac에서 Docker를 실행하기 위한 Linux 환경 등도 함께 제공한다.

---

# 10. VM과 Docker의 차이

VirtualBox 같은 VM은 **컴퓨터 자체를 가상화**한다.

```text
Hardware
   │
Host OS
   │
VirtualBox
   │
   ├── Ubuntu VM
   │     ├── Linux Kernel
   │     └── App
   │
   └── Ubuntu VM
         ├── Linux Kernel
         └── App
```

각 VM마다 독립적인 OS와 Kernel을 가진다.

Docker Container는 Host의 Linux Kernel을 공유하면서 프로세스와 파일시스템 등을 격리한다.

```text
Linux
  │
Linux Kernel
  │
Docker
  │
  ├── FastAPI Container
  ├── PostgreSQL Container
  └── Redis Container
```

따라서 개념적으로:

```text
VM
= 컴퓨터 안에 독립적인 컴퓨터를 만든다.

Container
= 같은 컴퓨터 안에서 프로세스별로
  독립된 실행 공간을 만든다.
```

Container는 일반적으로 VM보다:

- 가볍고
- 빠르게 시작할 수 있고
- 같은 서버에 더 많이 실행할 수 있다.

### VM이 사라진 것은 아니다.

실제로는 VM과 Docker를 같이 사용하는 경우가 많다.

```text
Cloud Physical Server
        │
    Hypervisor
        │
       VM
        │
      Linux
        │
      Docker
        │
   ┌────┼────┐
   ▼    ▼    ▼
  API  Redis Worker
```

---

# 11. Kubernetes

Docker가 Container 자체를 실행하는 기술이라면 Kubernetes는 **많은 Container를 여러 서버에서 안정적으로 운영하기 위한 Container Orchestration 기술**이다.

```text
Docker
→ Container를 어떻게 만들고 실행할까?

Docker Compose
→ 여러 Container를 어떻게 같이 실행할까?

Kubernetes
→ 여러 서버의 수많은 Container를
  어떻게 배포하고 유지하고 확장할까?
```

---

# 12. Kubernetes Node

Kubernetes가 Container를 실행하는 서버를 **Node**라고 한다.

```text
Kubernetes Cluster

├── Node A
├── Node B
└── Node C
```

Node는 실제 물리 서버일 수도 있고 Cloud의 VM일 수도 있다.

---

# 13. Kubernetes Pod

Kubernetes는 Container를 직접 최소 실행 단위로 관리하지 않고 **Pod**라는 단위를 사용한다.

```text
Node
 │
 ├── Pod
 │    └── FastAPI Container
 │
 ├── Pod
 │    └── FastAPI Container
 │
 └── Pod
      └── FastAPI Container
```

대부분의 경우:

```text
Pod
└── Container 하나
```

형태가 많지만 필요하다면:

```text
Pod
├── Main Container
└── Sidecar Container
```

처럼 밀접한 Container 여러 개를 묶을 수도 있다.

### Pod를 묶는 기준

단순히 같은 프로젝트라고 같은 Pod에 넣는 것이 아니다.

핵심 질문은:

> 같이 배포되고, 같이 죽고, 같이 확장되어야 하는가?

이다.

따라서 일반적으로:

```text
❌ Pod
├── FastAPI
├── PostgreSQL
└── Redis
```

보다는:

```text
FastAPI Pod
└── FastAPI

PostgreSQL Pod
└── PostgreSQL

Redis Pod
└── Redis
```

처럼 분리한다.

---

# 14. Deployment

Deployment는 **특정 Pod를 원하는 개수만큼 유지하도록 관리하는 Kubernetes 리소스**이다.

예:

```text
FastAPI Deployment

"FastAPI Pod를 3개 유지해"
        │
        ├── Pod #1
        ├── Pod #2
        └── Pod #3
```

Pod 하나가 죽으면 Kubernetes가 새로운 Pod를 만들어 원하는 상태를 복구한다.

```text
원하는 상태
FastAPI × 3

실제 상태
FastAPI #1 🟢
FastAPI #2 💀
FastAPI #3 🟢

        ↓ Kubernetes

FastAPI #1 🟢
FastAPI #3 🟢
FastAPI #4 🟢
```

---

# 15. MSA와 Pod

서비스를 MSA 형태로 분리했다면 일반적으로 서비스별로 Deployment를 분리한다.

```text
Kubernetes

Auth Deployment
├── Auth Pod
├── Auth Pod
└── Auth Pod

Weather Deployment
├── Weather Pod
└── Weather Pod

Recommendation Deployment
├── Recommendation Pod
└── Recommendation Pod
```

즉:

```text
Service
   ↓
Deployment
   ↓
Pod × N
   ↓
Container
```

구조로 이해할 수 있다.

### Pod를 분리하는 이유

서비스별로 독립적인 확장이 가능하다.

예:

```text
Auth
Pod × 2

Weather
Pod × 20

Recommendation
Pod × 5
```

날씨 조회 트래픽만 폭증했다면 Weather Service만 확장할 수 있다.

---

# 16. Kubernetes Autoscaling

Kubernetes는 설정에 따라 트래픽이나 CPU 등의 부하가 증가했을 때 Pod 개수를 자동으로 조절할 수 있다.

대표적인 기능이 **HPA(Horizontal Pod Autoscaler)**이다.

예:

```text
최소 Pod: 2
최대 Pod: 20
```

평상시:

```text
Weather Deployment
├── Pod #1
└── Pod #2
```

트래픽 증가:

```text
Traffic 증가
     ↓
CPU / Metric 증가
     ↓
HPA
     ↓
Pod 증가
```

결과:

```text
Weather Deployment
├── Pod #1
├── Pod #2
├── Pod #3
├── Pod #4
├── ...
└── Pod #10
```

트래픽이 줄어들면 Pod 수도 다시 줄일 수 있다.

---

# 17. Pod Scaling과 Node Scaling

Pod를 늘리는 것과 서버 자체를 늘리는 것은 다른 문제다.

```text
Node
├── Pod
├── Pod
├── Pod
└── 자원 부족
```

Node의 CPU/RAM이 부족하면 더 이상 Pod를 배치할 수 없다.

따라서 Cloud 환경에서는 Node 자체도 자동 확장하도록 구성할 수 있다.

```text
Traffic 증가
      ↓
HPA
      ↓
Pod 증가
      ↓
Node 자원 부족
      ↓
Node Autoscaling
      ↓
새 Node 생성
      ↓
새 Node에 Pod 배치
```

정리하면:

```text
HPA
→ Pod를 몇 개 실행할 것인가?

Node Autoscaling
→ Pod를 담을 Server를 몇 대 운영할 것인가?
```

---

# 18. Docker → Kubernetes → Cloud

전체적인 관계는 다음과 같다.

```text
Docker
│
│ 애플리케이션 Container화
▼

Docker Compose
│
│ 여러 Container 구성
▼

Kubernetes
│
│ Container 배포 / 복구 / 확장
▼

Cloud
│
│ 실제 서버 / Network / Storage / DB 제공
▼

AWS / GCP / Azure ...
```

Cloud가 제공하는 실제 인프라 위에서 Kubernetes와 Docker가 동작한다.

예:

```text
Cloud

├── Load Balancer
├── Network
├── Managed Database
├── Storage
│
└── Kubernetes Cluster
      │
      ├── Node
      │    ├── Pod
      │    └── Pod
      │
      └── Node
           ├── Pod
           └── Pod
```

---

# 19. 전체 개념 한 번에 정리

```text
Dockerfile
   │
   │ build
   ▼
Image
   │
   │ run
   ▼
Container
   │
   ├── Port
   │     외부 ↔ Container
   │
   ├── Network
   │     Container ↔ Container
   │
   ├── Volume
   │     Docker가 관리하는 영구 저장공간
   │
   └── Bind Mount
         Host 디렉터리 연결

여러 Container
      │
      ▼
Docker Compose

대규모 운영
      │
      ▼
Kubernetes
      │
      ├── Node
      │
      ├── Pod
      │
      ├── Deployment
      │
      └── Autoscaling
             │
             ▼
           Cloud
```

## 핵심 문장

> **Dockerfile** = Image 제작 설명서

> **Image** = 실행 환경이 패키징된 결과물

> **Container** = Image를 실제로 실행한 인스턴스

> **Docker Compose** = 여러 Container의 구성과 실행 방법 정의

> **Port** = Host와 Container 사이의 포트 연결

> **Network** = Container끼리 통신하기 위한 네트워크

> **Bind Mount** = 내가 관리하는 Host 저장공간을 Container에 연결

> **Volume** = Docker가 관리하는 외부 저장공간을 Container에 연결

> **Docker Desktop** = Mac/Windows에서 Docker 실행환경과 관리 기능을 제공하는 애플리케이션

> **VM** = OS/컴퓨터 단위 가상화

> **Container** = Kernel을 공유하면서 프로세스/실행환경을 격리

> **Kubernetes** = Container들을 여러 서버에서 배포·복구·확장하는 Orchestration 시스템

> **Node** = Kubernetes가 사용하는 서버

> **Pod** = Kubernetes의 최소 배포/실행 단위

> **Deployment** = Pod의 원하는 상태와 개수를 관리

> **HPA** = 부하에 따라 Pod 개수를 자동 조절

> **Cloud** = Docker/Kubernetes 등이 동작할 실제 서버·네트워크·스토리지 등의 인프라 제공