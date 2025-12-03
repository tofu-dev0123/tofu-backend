FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["python", "start.py"]
