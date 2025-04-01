FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app /app
COPY app/rational-autumn-455414-s6-8db1fe0914f9.json /app/rational-autumn-455414-s6-8db1fe0914f9.json

CMD ["python", "app.py"]