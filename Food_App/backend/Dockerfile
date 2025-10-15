FROM python:3.11-slim

WORKDIR /app

# 安裝系統相依（psycopg 需要）
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 先放需求檔，安裝套件（這層會被快取）
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 再放原始碼
COPY . /app

# 開發模式用 uvicorn --reload（因為我們把程式碼掛進容器了）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
