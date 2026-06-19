FROM python:3.12-slim

WORKDIR /app

ENV FLAGS_use_onednn=0 \
    FLAGS_use_mkldnn=0 \
    PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True \
    YOLO_CONFIG_DIR=/tmp/Ultralytics

RUN apt-get update \
    && apt-get install -y libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY fastapi-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fastapi-server/vendor /tmp/predictive-vendor
RUN set -eu; \
    wheel="$(find /tmp/predictive-vendor -maxdepth 1 -type f -name '*.whl' -print -quit)"; \
    if [ -n "$wheel" ]; then pip install --no-cache-dir "$wheel"; fi; \
    rm -rf /tmp/predictive-vendor

COPY predictive_ml/src /app/predictive_ml/src
ENV PYTHONPATH=/app/predictive_ml/src

COPY fastapi-server/app ./app
COPY fastapi-server/samples ./samples

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
