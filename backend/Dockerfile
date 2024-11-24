FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create instance directory and set permissions
RUN mkdir -p instance && \
    chmod 777 instance

EXPOSE 3333

CMD ["python", "run.py"]
