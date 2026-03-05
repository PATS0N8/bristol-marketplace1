FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Disable autoreload inside Docker (more stable on macOS)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]