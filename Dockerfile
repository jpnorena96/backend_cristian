FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for potential mysql, pillow etc)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libmariadb-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
