FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static directory and copy static files
COPY static/ /app/static/
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"] 