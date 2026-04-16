FROM python:3.9-slim
WORKDIR /app
# Install dependensi sistem untuk MySQL
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]