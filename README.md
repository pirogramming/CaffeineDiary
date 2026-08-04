# ☕ Caffeine Diary

> **건강한 각성을 위한 나만의 카페인 기록장**
> "당신의 커피 마감시간을 알려드립니다"

개인별 카페인 섭취량과 컨디션을 기록해, **지금 커피를 마셔도 되는지**를 알려주는 웹 서비스입니다.

<br>

## 📌 왜 만들었나

> "카페인은 6시간 전까지만" — 이 조언은 **모든 사람에게 똑같이 적용되지 않습니다.**

같은 200mg을 마셔도 어떤 사람은 멀쩡히 자고, 어떤 사람은 새벽까지 뒤척입니다. 실제 연구에서도 **개인별 카페인 반응 차이가 극단적으로 크다**는 점이 확인되었고, 개인화 모델이 집단 평균 모델보다 유의미하게 정확한 예측을 보였습니다.

Caffeine Diary는 사용자의 **섭취 기록 + 다음날 수면 피드백**을 누적해, 그 사람만의 카페인 임계치를 추정합니다. 쓰면 쓸수록 정확해지는 마감시간을 제공하는 것이 목표입니다.

<br>

## ✨ 핵심 기능

| 기능 | 설명 |
|---|---|
| **📖 카페인 다이어리** | 버튼 한 번으로 섭취 기록. 음료 종류별 카페인량 자동 계산 |
| **⏰ 오늘의 커피 마감시간** | 목표 취침시각 기준, 언제까지 마셔도 되는지 실시간 계산 |
| **🌙 밤샘모드** | 목표 시각까지 각성을 유지하기 위한 카페인 섭취 스케줄 추천 |

### 동작 원리

**1단계 — 집단 평균 PK 모델**

1구획 약동학 모델로 혈중 카페인 농도를 예측합니다.

```
C(t) = D · exp(-kₑ·t)
```

여러 잔을 마신 경우 선형 중첩(superposition)으로 합산합니다.

**2단계 — 개인화**

기록이 쌓일수록 집단 평균 임계치에서 개인 추정치 쪽으로 가중치가 이동합니다.

```
w = n / (n + n₀)
```

기록 수 `n`이 늘어날수록 개인 추정치의 비중이 커지는 구조입니다.

> ⚠️ 위 가중치 식은 Liu et al. (2017)의 확장 칼만 필터 기반 베이지안 축소추정 개념을 **단순화한 근사**이며, 논문에서 직접 인용한 수식이 아닙니다.
> 마감시각 역산 로직 또한 논문의 약동학 곡선을 **본 프로젝트에서 응용·확장**한 것입니다.

<br>

## 📚 참고 문헌

- Ramakrishnan, S. et al. (2014). *Dose-dependent model of caffeine effects on human vigilance during total sleep deprivation.* **J Theor Biol, 358:11–24.** [🔗](https://apps.dtic.mil/sti/pdfs/ADA604238.pdf)
- Liu, J. et al. (2017). *Real-time individualization of the unified model of performance.* **J Sleep Res, 26:820–831.** [🔗](https://bhsai.org/pubs/Liu_2017_Real_Time_Individualization.pdf)
- Vital-Lopez, F. G. et al. (2018). **J Sleep Research, 27:e12711.**
- 2B-Alert App 검증 연구 (2023)

<br>

## 🛠 기술 스택

| 구분 | 사용 기술 |
|---|---|
| **Backend** | Django, Django REST Framework |
| **Frontend** | HTML, CSS, Vanilla JavaScript, Chart.js |
| **Database** | MySQL |
| **Infra** | AWS EC2, Docker, Nginx, Gunicorn |
| **CI/CD** | GitHub Actions |
| **Auth** | Django Session Authentication |

> 프론트·백엔드가 동일 도메인에서 서빙되는 구조이므로 JWT 대신 **세션 인증**을 채택했습니다.

<br>

## 🗂 데이터 모델

| 모델 | 역할 |
|---|---|
| `Drink` | 음료 마스터 테이블 (종류별 기본 카페인량) |
| `UserProfile` | 사용자 상수 + 개인화 파라미터 (목표 취침시각, 추정 임계치 등) |
| `CaffeineLog` | 섭취 이벤트 단위 기록 |
| `DailyLog` | 하루 단위 수면 설문 결과 |
| `AllNightSession` | 밤샘모드 세션 상태 |

**설계 원칙**
- 섭취 단위 데이터(`CaffeineLog`)와 하루 단위 데이터(`DailyLog`)는 **별도 모델**로 분리
- 하루 경계는 **05:00 기준** (새벽 시간대 섭취를 전날 기록으로 처리)
- 밤샘한 날은 수면 설문을 건너뜀
- 밤샘모드 스케줄은 화면 표시용으로만 계산, DB에 저장하지 않음

<br>

## 🚀 시작하기

### 요구사항
- Python 3.x
- MySQL
- Docker (선택)

### 로컬 실행

```bash
# 1. 클론
git clone https://github.com/{ORG}/{REPO}.git
cd {REPO}

# 2. 가상환경
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env          # 값 채우기

# 5. 마이그레이션
python manage.py migrate

# 6. 실행
python manage.py runserver
```

### Docker로 실행

```bash
docker compose up -d --build
```

<br>

---

# 🤝 개발 컨벤션

## 브랜치 전략

```
main        ← 배포 가능한 안정 버전
 ↑
develop     ← 개발 통합 브랜치 (기본 작업 대상)
 ↑
feature/*   ← 기능 단위 작업 브랜치
```

- 모든 기능 브랜치는 **`develop`에서 분기**하고 **`develop`으로 머지**합니다
- 배포 시점에만 `develop` → `main` 으로 머지합니다
- `main`, `develop`에는 **직접 push 금지**. 반드시 PR을 거칩니다

### 브랜치 네이밍

```
{타입}/{이슈번호}-{작업내용}
```

```bash
feature/12-cutoff-api
fix/15-timezone-bug
refactor/20-pk-model
docs/23-readme
```

<br>

## 작업 흐름

```
① Issue 생성 → ② Branch 생성 → ③ Commit → ④ Push
                                              ↓
        ⑦ Merge ← ⑥ Code Review ← ⑤ PR 생성
```

**① Issue 생성**
템플릿에 맞춰 작성하고 Label·Assignee를 지정합니다. 자동 부여된 번호(`#12`)를 이후 단계에서 계속 사용합니다.

**② Branch 생성**
```bash
git switch develop
git pull origin develop
git switch -c feature/12-cutoff-api
```
> GitHub 이슈 페이지 우측 **Development → Create a branch** 를 쓰면 이슈와 자동으로 연결됩니다.

**③ Commit**
```bash
git commit -m "feat: 혈중 카페인 농도 계산 함수 추가 (#12)"
```

**④ Push**
```bash
git push origin feature/12-cutoff-api
```

**⑤ PR 생성**
- base: `develop` / compare: 작업 브랜치
- PR 본문에 **`Closes #12`** 를 반드시 포함 (머지 시 이슈 자동 종료)

**⑥ Code Review**
- 최소 **1명 이상 Approve** 후 머지
- 리뷰어는 24시간 내 확인을 원칙으로 합니다

**⑦ Merge**
- 머지 후 원격 브랜치 삭제
- 로컬 정리:
  ```bash
  git switch develop
  git pull origin develop
  git branch -d feature/12-cutoff-api
  ```

<br>

## 커밋 메시지 컨벤션

```
{타입}: {변경 내용} (#{이슈번호})
```

```bash
feat: 커피 마감시간 계산 API 구현 (#12)
fix: 자정 넘어간 취침시각 계산 오류 수정 (#15)
refactor: PK 모델 계산 로직 함수 분리 (#20)
```

| 타입 | 사용 시점 |
|---|---|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 기능 변경 없는 코드 개선 |
| `style` | 코드 포맷, 세미콜론 등 (로직 변경 없음) |
| `docs` | 문서 수정 |
| `test` | 테스트 코드 추가·수정 |
| `chore` | 빌드, 설정, 패키지 등 기타 |

**작성 규칙**
- 제목은 **50자 이내**, 마침표 없이
- 본문이 필요하면 제목과 한 줄 띄우고 작성
- **한 커밋에는 하나의 논리적 변경**만 담습니다

<br>

## 이슈 라벨

**작업 종류**
`feature` · `bug` · `refactor` · `docs` · `setup` · `test`

**담당 영역**
`backend` · `frontend` · `infra`

**우선순위**
`P0-critical` · `P1-high` · `P2-low`

**상태**
`blocked` · `discussion`

> 이슈 하나에 `feature` + `backend` + `P1-high` 처럼 여러 라벨을 함께 붙입니다.

<br>

## 이슈 작성 가이드

**브랜치 하나 = PR 하나로 끝날 크기**로 쪼갭니다.

| ❌ 너무 큼 | ✅ 적정 |
|---|---|
| 다이어리 기능 구현 | `CaffeineLog` 모델 작성 |
| | 섭취 기록 생성 API |
| | 섭취 기록 목록 조회 API |

<br>

## 📁 디렉토리 구조

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── feature.md
│   │   ├── bug.md
│   │   └── refactor.md
│   ├── pull_request_template.md
│   └── workflows/
├── config/              # Django 프로젝트 설정
├── apps/                # 도메인별 앱
├── static/
├── templates/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

<br>

## 👥 팀

| 이름 | 역할 | GitHub |
|---|---|---|
| 정현민 | 기획 / BE | [@hyunnminn](https://github.com/hyunnminn) |
| 이아린 | BE | [@ethan0587](https://github.com/ethan0587) |
| 이환희 | FE | [@bigdevlight](https://github.com/bigdevlight) |
| 정다희 | FE | [@jdheeee](https://github.com/jdheeee) |

<br>

---

<div align="center">
  <sub>25기 · Caffeine Diary</sub>
</div>