FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000 \
    HKM_DEPLOYMENT_MODE=hosted \
    HKM_HOST=0.0.0.0 \
    HKM_RUNTIME_DIR=/tmp/hkm-runtime

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . .
RUN python scripts/build_site.py \
    && useradd --create-home --uid 10001 hkm \
    && mkdir -p /tmp/hkm-runtime \
    && chown -R hkm:hkm /tmp/hkm-runtime

USER hkm
EXPOSE 10000

CMD ["python", "-m", "harness.server"]
