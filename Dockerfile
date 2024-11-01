FROM python:3.12

WORKDIR /app

COPY requirements.txt *.py .env /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "main:app"]
