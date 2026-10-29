FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY linkextractor.py main.py ./

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "--threads", "2", "-b", "0.0.0.0:5000", "main:app"]
