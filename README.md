# ⚡ TaskFlow — Containerized Web Application on AWS

> **Course:** DevOps for Cloud Computing (CSC418)  
> **Institution:** COMSATS University Islamabad, Lahore Campus  
> **Program:** BS Software Engineering (BS-SE) — 7th Semester  
> **Topic:** Lab Mid Examination: EC2 Deployment, Docker Compose, Auto Scaling, Load Balancing & Selenium WebDriver  

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Section A: Practical Implementation Tasks](#section-a-practical-implementation-tasks)
   - [Task 1: Linux Administration & Permissions](#task-1-linux-administration--permissions)
   - [Task 2: Docker Installation & Custom Images](#task-2-docker-installation--custom-images)
   - [Task 3: Docker Named Volumes & Persistence](#task-3-docker-named-volumes--persistence)
   - [Task 4: Multi-Container Setup with Docker Compose](#task-4-multi-container-setup-with-docker-compose)
   - [Task 5: AWS Load Balancer & Auto Scaling Group](#task-5-aws-load-balancer--auto-scaling-group)
   - [Task 6: Automated Selenium Testing](#task-6-automated-selenium-testing)
6. [Section B: Viva Voce Preparation & Concepts](#section-b-viva-voce-preparation--concepts)
7. [Local Setup & Testing](#local-setup--testing)

---

## 🚀 Project Overview

**TaskFlow** is a modern, responsive, production-grade task management web application designed and deployed following enterprise DevOps practices. 

The application is containerized using **Docker** and orchestrated using **Docker Compose** across two isolated services:
1. **Web App Tier:** Python Flask running on high-performance **Gunicorn WSGI server** with custom health check endpoints.
2. **Database Tier:** **PostgreSQL 15** utilizing **Docker Named Volumes** for persistent relational storage.

The infrastructure is deployed on **Amazon Web Services (AWS)** behind an **Application Load Balancer (ALB)** and managed dynamically via an **Auto Scaling Group (ASG)** across multiple Availability Zones. Automated end-to-end integration testing is validated via a **Selenium WebDriver** test suite.

---

## 🏛️ Architecture Diagram

```
                        ┌────────────────────────────────────────────────────────┐
                        │             End User / Selenium Test Suite             │
                        └───────────────────────────┬────────────────────────────┘
                                                    │ HTTP (Port 80)
                                                    ▼
                        ┌────────────────────────────────────────────────────────┐
                        │        AWS Application Load Balancer (ALB)            │
                        │                 taskflow-alb                           │
                        └───────────────────────────┬────────────────────────────┘
                                                    │
                           ┌────────────────────────┴────────────────────────┐
                           │ Target Group: taskflow-tg (HTTP: 5000 /health) │
                           └───────────────┬─────────────────┬───────────────┘
                                           │                 │
                   ┌───────────────────────▼──────┐   ┌──────▼───────────────────────┐
                   │  AWS EC2 Instance 1 (us-east-1a)│   │  AWS EC2 Instance 2 (us-east-1b)│
                   │    [Managed by AWS ASG]      │   │    [Managed by AWS ASG]      │
                   ├──────────────────────────────┤   ├──────────────────────────────┤
                   │  Docker Engine               │   │  Docker Engine               │
                   │  ┌────────────────────────┐  │   │  ┌────────────────────────┐  │
                   │  │ taskflow_web (Flask)   │  │   │  │ taskflow_web (Flask)   │  │
                   │  │ Gunicorn :5000         │  │   │  │ Gunicorn :5000         │  │
                   │  └───────────┬────────────┘  │   │  └───────────┬────────────┘  │
                   │              │ taskflow_net  │   │              │ taskflow_net  │
                   │  ┌───────────▼────────────┐  │   │  ┌───────────▼────────────┐  │
                   │  │ taskflow_db (Postgres) │  │   │  │ taskflow_db (Postgres) │  │
                   │  └───────────┬────────────┘  │   │  └───────────┬────────────┘  │
                   │              │               │   │              │               │
                   │  ┌───────────▼────────────┐  │   │  ┌───────────▼────────────┐  │
                   │  │ Volume: postgres_data  │  │   │  │ Volume: postgres_data  │  │
                   │  └────────────────────────┘  │   │  └────────────────────────┘  │
                   └──────────────────────────────┘   └──────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript | Modern Dark-mode glassmorphism design, Google Inter typography |
| **Backend** | Python 3.11, Flask 3.0 | RESTful routing, SQLAlchemy ORM, health endpoint `/health` |
| **WSGI Server**| Gunicorn 22.0 | Multi-worker concurrent HTTP application server |
| **Database** | PostgreSQL 15 Alpine | Relational database with automated migrations |
| **Container** | Docker & Docker Compose v2 | Multi-stage build, non-root user, named volumes |
| **Cloud (AWS)**| EC2, ALB, ASG, AMI | Amazon Linux / Ubuntu 26.04, Launch Template, Target Groups |
| **Testing** | Selenium WebDriver, Chrome | Automated browser UI, functional, and health verification |

---

## 📂 Project Structure

```
Midterm/
├── app.py                     # Flask web app & health check endpoints
├── requirements.txt           # Python application dependencies
├── Dockerfile                 # Production multi-stage Docker build
├── docker-compose.yml         # Multi-container orchestration (web + db)
├── ec2-userdata.sh            # Automated EC2 launch boot script
├── test_app.py                # 8-phase automated Selenium test suite
├── templates/
│   └── index.html             # UI template with stats counters & task list
├── static/
│   └── style.css              # Glassmorphic dark theme stylesheet
└── README.md                  # Comprehensive project documentation
```

---

## 📝 Section A: Practical Implementation Tasks

### Task 1: Linux Administration & Permissions (1 Mark)
Demonstrated user management, directory isolation, and Linux permissions on the EC2 host:
```bash
# Directory creation and navigation
sudo mkdir -p /opt/taskflow
cd /opt/taskflow

# File permissions demonstration
sudo touch test_permission.txt
sudo chmod 755 test_permission.txt
ls -l test_permission.txt
# Output: -rwxr-xr-x 1 root root 0 test_permission.txt

# User and ownership management
sudo useradd -m devopsuser
sudo chown -R devopsuser:devopsuser /opt/taskflow
ls -ld /opt/taskflow
# Output: drwxr-xr-x 2 devopsuser devopsuser 4096 /opt/taskflow
```

---

### Task 2: Docker Installation & Custom Images (2 Marks)
* Installed Docker Engine and Docker Compose on AWS EC2.
* Authored an optimized **multi-stage `Dockerfile`** to minimize attack surface and reduce production image footprint:
  - **Stage 1 (Builder):** Installs build-time packages (`gcc`, `libpq-dev`) and installs Python wheels into `/install`.
  - **Stage 2 (Runtime):** Copies only compiled wheels, executes as non-root `appuser (UID 1000)`, and configures native health checks.

```bash
# Build custom image
docker build -t taskflow:latest .

# Verify image in registry
docker images
# Output: taskflow:latest (Content size: ~59.2 MB)
```

---

### Task 3: Docker Named Volumes & Persistence (1 Mark)
Demonstrated persistent storage across container lifecycles:
```bash
# 1. Create a named volume
docker volume create test_volume

# 2. Write data using a temporary container
docker run --rm -v test_volume:/data alpine sh -c \
  "echo 'Docker Persistence Verified on AWS EC2' > /data/proof.txt"

# 3. Read data from a completely NEW container instance
docker run --rm -v test_volume:/data alpine cat /data/proof.txt
# Output: Docker Persistence Verified on AWS EC2
```
*In the application stack, the `postgres_data` named volume is mounted to `/var/lib/postgresql/data` ensuring no database loss upon container restarts or redeployments.*

---

### Task 4: Multi-Container Setup with Docker Compose (2 Marks)
Orchestrated `taskflow_web` and `taskflow_db` using `docker-compose.yml`:
* **Health Checks & Startup Order:** Web service uses `depends_on: db: condition: service_healthy` to guarantee PostgreSQL is actively responding before starting Gunicorn.
* **Network Isolation:** Isolated bridge network `taskflow_net`.
* **Execution:**
```bash
docker compose up -d
docker compose ps
```
**Verification:**
```bash
curl http://localhost:5000/health
# Response: {"db":"connected","status":"healthy"}
```

---

### Task 5: AWS Load Balancer & Auto Scaling Group (2 Marks)
Deployed high-availability infrastructure on AWS:
1. **Golden AMI:** Created `taskflow-ami` from configured instance.
2. **Launch Template:** Created `taskflow-template` specifying instance configuration and automated boot script:
   ```bash
   #!/bin/bash
   cd /opt/taskflow
   docker compose up -d
   ```
3. **Target Group (`taskflow-tg`):**
   - Protocol: `HTTP: 5000`
   - Health check path: `/health` (HTTP 200 response required)
4. **Application Load Balancer (`taskflow-alb`):**
   - Public Internet-facing ALB listening on `HTTP: 80`.
   - Distributes incoming traffic across Availability Zones (`us-east-1a`, `us-east-1b`).
   - Forwarding target: `taskflow-tg`.
5. **Auto Scaling Group (`taskflow-asg`):**
   - Maintains **2 Desired**, **1 Minimum**, and **3 Maximum** EC2 instances.
   - Automatically checks instance health via ELB and replaces unhealthy instances.

---

### Task 6: Automated Selenium Testing (2 Marks)
Created and executed an automated end-to-end Python Selenium WebDriver test suite (`test_app.py`) directly targeting the AWS Load Balancer URL:

```bash
python3 test_app.py http://taskflow-alb-1102056613.us-east-1.elb.amazonaws.com
```

**Test Execution Results:**
```
══════════════════════════════════════════════════
  TaskFlow Selenium Test Suite
  Target URL: http://taskflow-alb-1102056613.us-east-1.elb.amazonaws.com
══════════════════════════════════════════════════

──────────────────────────────────────────────────
  Test 1 – Health Check Endpoint
──────────────────────────────────────────────────
  ✓ PASS  GET /health returns 200 with status=healthy

──────────────────────────────────────────────────
  Test 2 – Homepage Load
──────────────────────────────────────────────────
  ✓ PASS  Page title contains 'TaskFlow' (got: 'TaskFlow – DevOps Midterm')

──────────────────────────────────────────────────
  Test 3 – UI Elements
──────────────────────────────────────────────────
  ✓ PASS  h1 heading found: 'TaskFlow'
  ✓ PASS  Task title input field found (#taskTitle)
  ✓ PASS  Task description textarea found (#taskDesc)
  ✓ PASS  Add Task button found (#addBtn)

──────────────────────────────────────────────────
  Test 4 – Add New Task
──────────────────────────────────────────────────
  ✓ PASS  Form submitted successfully

──────────────────────────────────────────────────
  Test 5 – Task Appears in List
──────────────────────────────────────────────────
  ✓ PASS  Task visible in task list
  ✓ PASS  Task description visible in task list

──────────────────────────────────────────────────
  Test 6 – Toggle Task Completion
──────────────────────────────────────────────────
  ✓ PASS  Task toggled (checkbox clicked)
  ✓ PASS  Task item shows 'completed' CSS class

──────────────────────────────────────────────────
  Test 7 – Delete Task
──────────────────────────────────────────────────
  ✓ PASS  Delete button clicked and confirmation accepted

──────────────────────────────────────────────────
  Test 8 – Stats Cards
──────────────────────────────────────────────────
  ✓ PASS  Stats cards found: Total=2, Done=1, Pending=1

══════════════════════════════════════════════════
  RESULTS: 13 passed  |  0 failed  |  13 total
══════════════════════════════════════════════════
  All tests passed! ✓
```

---

## 🎯 Section B: Viva Voce Preparation & Concepts (15 Marks)

### 1. AWS EC2, Load Balancing & Auto Scaling
* **What is the difference between an Application Load Balancer (ALB) and a Network Load Balancer (NLB)?**
  * ALB operates at **Layer 7 (Application Layer)** and routes traffic based on HTTP/HTTPS headers, paths (e.g. `/health`), and hostnames. NLB operates at **Layer 4 (Transport Layer)** with ultra-low latency for TCP/UDP traffic.
* **Why do we need a Target Group?**
  * Target groups act as logical targets for the Load Balancer to route traffic to, performing active health checks against registered instances.
* **How does the Auto Scaling Group know when to scale out?**
  * ASG monitors CloudWatch metrics (e.g., Average CPU Utilization > 50%) or ELB target response times to trigger scaling policies and launch new instances from the Launch Template.

### 2. Linux Administration
* **What does `chmod 755` mean?**
  * Binary `111 101 101`: Owner gets Read, Write, Execute (7); Group gets Read, Execute (5); Others get Read, Execute (5).
* **What is the purpose of `newgrp docker`?**
  * It activates the new group membership immediately in the current shell session without needing to log out and log back in.

### 3. Docker & Containerization
* **Why use a multi-stage Docker build?**
  * It drastically reduces image size and enhances security. Heavy compilers (`gcc`, headers) used to build C extensions are kept in the build stage and excluded from the final production runtime image.
* **Why should containers run as a non-root user?**
  * Running as a non-root user (`USER appuser`) mitigates container escape vulnerabilities and limits damage if the web process is compromised.

### 4. Docker Volumes & Networking
* **How do Docker Volumes differ from Bind Mounts?**
  * Volumes are managed entirely by Docker (`/var/lib/docker/volumes/`), are filesystem-agnostic, and are isolated from the host directory structure, making them safer and more portable than bind mounts.
* **How do multi-containers communicate in Docker Compose?**
  * Docker Compose creates a default user-defined bridge network. It provides automatic **DNS resolution**, allowing containers to resolve each other simply by service name (e.g., `postgresql://user:pass@db:5432/taskdb`).

### 5. Selenium Testing
* **Why automate testing with Selenium in a DevOps pipeline?**
  * Selenium WebDriver validates that the deployment is not merely returning HTTP 200, but is functionally rendering DOM elements, processing JavaScript, handling forms, and interacting with the database correctly from an end-user perspective.

---

## 💻 Local Setup & Testing

### Prerequisites
* Docker & Docker Compose installed
* Python 3.10+ (for running Selenium tests locally)

### Steps
```bash
# 1. Clone repository
git clone <repo-url>
cd Midterm

# 2. Start services locally
docker compose up -d --build

# 3. Access web application
open http://localhost:5000

# 4. Run automated test suite
python3 test_app.py http://localhost:5000
```
