# syntax=docker/dockerfile:1
# CaffeineDiary — Django + gunicorn 운영 이미지

FROM python:3.13-slim

# 파이썬 런타임 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# mysqlclient 빌드에 필요한 시스템 패키지
#   - build-essential / pkg-config: C 확장 컴파일
#   - default-libmysqlclient-dev: MySQL 클라이언트 라이브러리 (빌드 + 런타임)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성만 먼저 복사해 레이어 캐시 활용 (코드만 바뀔 때 재설치 방지)
COPY requirements.txt requirements-prod.txt ./
RUN pip install -r requirements-prod.txt

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 수집 (DB 연결 불필요 — settings 폴백으로 로드).
# 실패해도 빌드가 멈추지 않도록 하지 않는다: 정적 경로 문제를 빌드 시점에 잡기 위함.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# WSGI 서버로 기동 (nginx 뒤에서 리버스 프록시).
# migrate 는 런타임에 docker-compose 커맨드/엔트리포인트에서 수행한다.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
