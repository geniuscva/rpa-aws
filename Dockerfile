FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ROBOT_OPS_HOST=0.0.0.0
ENV ROBOT_OPS_PORT=8000

# Create volume for data directory
VOLUME ["/app/data"]

EXPOSE 8000

CMD ["python", "-m", "robot_ops"]
