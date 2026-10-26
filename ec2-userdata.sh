#!/bin/bash
# ================================================
# EC2 User Data Script — TaskFlow App
# Runs automatically when EC2 instance launches
# ================================================

set -e  # Exit on any error
exec > /var/log/userdata.log 2>&1  # Log all output

echo "=== [1/6] System Update ==="
yum update -y

echo "=== [2/6] Install Docker ==="
yum install -y docker git
systemctl start docker
systemctl enable docker

echo "=== [3/6] Install Docker Compose ==="
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "=== [4/6] Add ec2-user to docker group ==="
usermod -aG docker ec2-user

echo "=== [5/6] Clone / Create App Files ==="
mkdir -p /opt/taskflow
cd /opt/taskflow

# Create app.py
cat > app.py << 'PYEOF'
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://taskuser:taskpass@db:5432/taskdb')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    if title:
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'healthy', 'db': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
PYEOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
SQLAlchemy==2.0.31
gunicorn==22.0.0
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY app.py .
COPY templates/ templates/
COPY static/ static/
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    container_name: taskflow_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: taskdb
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: taskpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - taskflow_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskdb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
  web:
    build: .
    container_name: taskflow_web
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://taskuser:taskpass@db:5432/taskdb
    depends_on:
      db:
        condition: service_healthy
    networks:
      - taskflow_net
volumes:
  postgres_data:
    driver: local
networks:
  taskflow_net:
    driver: bridge
EOF

# Create templates and static directories
mkdir -p templates static

# Download/create template and CSS from inline content
# (In a real scenario these would be pulled from S3 or git)
# For this script, they're embedded — see full files in project

echo "=== [6/6] Start Application ==="
cd /opt/taskflow
docker-compose up -d --build

echo "=== DONE! App running at http://localhost:5000 ==="
