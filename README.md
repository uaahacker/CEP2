# ☁️ Cloud Cost Management Panel

> **Final Submission** – Cloud Computing Assignment  
> Interactive AWS FinOps dashboard with login/signup, real AWS Cost Explorer integration, Demo Mode, and full AWS EC2 deployment.

---

## 📋 Final Deliverables

| Deliverable | Link |
|---|---|
| **Live App URL** | *(add after deployment – e.g. https://your-domain.com)* |
| **GitHub Repo URL** | *(add after push – e.g. https://github.com/YOUR_USERNAME/cloud-cost-management-panel)* |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Login / Sign Up | Email + bcrypt-hashed password, SQLite storage |
| 📅 Date Range Filter | Pick any start/end date; defaults to last 30 days |
| 📊 Granularity | Daily or Monthly aggregation |
| 💰 Cost Metric | Unblended Cost or Amortized Cost |
| 🗂️ Group By | Slice by Service, Region, or Linked Account |
| 🏆 Top-N Filter | Show top 3–15 groups |
| ✂️ Cost Reduction Slider | Simulate 0–30% cost reduction in real time |
| 📈 Time-Series Chart | Actual vs Projected cost |
| 📊 Bar Chart | Top-N groups ranked by total spend |
| 🍩 Donut Chart | Cost distribution |
| 💡 FinOps Insights | Total spend, period-over-period change, top-3 concentration, anomaly detection, projected savings |
| 📋 Data Table | Raw data + group summary |
| 🔄 Demo Mode | Automatic fallback with synthetic data when AWS not available |
| 🚀 Deployed | AWS EC2 + Docker + Nginx + HTTPS |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Web framework | Python 3.11, Streamlit |
| Cloud SDK | boto3 (AWS Cost Explorer) |
| Data | pandas, numpy |
| Charts | Plotly |
| Authentication | SQLite + bcrypt |
| Container | Docker, docker-compose |
| Reverse proxy | Nginx |
| HTTPS | Let's Encrypt / Certbot |
| Hosting | AWS EC2 Ubuntu 22.04 |

---

## 📁 Project Structure

```
cloud-cost-management-panel/
│
├── app.py               ← Main Streamlit application (UI orchestration)
├── auth.py              ← Login / signup / session management
├── cost_data.py         ← AWS Cost Explorer + Demo Mode data
├── insights.py          ← FinOps metric calculations
├── charts.py            ← Plotly chart builders
│
├── requirements.txt     ← Python dependencies
├── Dockerfile           ← Container definition
├── docker-compose.yml   ← Docker Compose service config
├── .env.example         ← Environment variable template
├── .gitignore           ← Git ignore rules
├── README.md            ← This file
├── DEPLOYMENT_GUIDE.md  ← Step-by-step AWS EC2 deployment
│
└── docs/
    ├── aws-services-used.md
    ├── cost-estimate.md
    ├── security-assumptions.md
    ├── shutdown-budget-controls.md
    └── video-script.md
```

---

## 📦 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/cloud-cost-management-panel.git
cd cloud-cost-management-panel
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env to add your AWS credentials (optional – app works without them)
```

---

## ▶️ Run Without Docker

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## 🐳 Run With Docker

```bash
cp .env.example .env
# Add real AWS credentials to .env (optional)

docker compose up -d --build
```

Opens at **http://localhost:8501**

Stop:
```bash
docker compose down
```

---

## 🔐 Authentication

The app includes a simple **academic-demo** login/signup system:

- First page shows **Log In** and **Sign Up** tabs
- Users are stored in a local **SQLite** database (`users.db`)
- Passwords are hashed with **bcrypt** — never stored in plain text
- Session state managed by Streamlit
- Logout button in sidebar

> **Production note:** For a real production deployment, replace this with **AWS Cognito** or another managed identity service.

---

## ☁️ AWS Cost Explorer

When valid AWS credentials are present, the app calls `GetCostAndUsage` from AWS Cost Explorer.

**Required IAM permission:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ce:GetCostAndUsage"],
      "Resource": "*"
    }
  ]
}
```

> Do **not** use root account credentials. Create a limited IAM user.

---

## 🤖 Demo Mode

If AWS credentials are absent or invalid, the app automatically switches to **Demo Mode**:

- Yellow badge: **⚠️ Demo Mode – AWS credentials not detected, using synthetic data**
- Realistic synthetic data for EC2, S3, RDS, Lambda, CloudFront, DynamoDB, VPC, EKS
- Built-in cost spike to demonstrate anomaly detection
- All filters work identically in Demo Mode

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
AUTH_DB_PATH=users.db
STREAMLIT_SERVER_PORT=8501
```

**Never commit `.env` to Git.** It is already in `.gitignore`.

---

## 🚀 Deployment Summary

Full instructions: see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

```
GitHub Repo
    ↓  git clone
EC2 Instance (Ubuntu 22.04)
    ↓  docker compose up -d --build
Docker Container (Streamlit :8501)
    ↓  Nginx reverse proxy
Public HTTPS URL (Let's Encrypt)
```

---

## 📸 Screenshots

> *(Add screenshots after deployment)*

- Login page
- Dashboard – Demo Mode
- Dashboard – Real AWS Mode
- FinOps Insights panel
- Data Table

---

## 📝 Video Presentation Script

See [docs/video-script.md](docs/video-script.md) for the full script and recording checklist.

---

## ✅ Assignment Requirements Checklist

- [x] GitHub version control
- [x] Public-facing Streamlit web app
- [x] Login / signup before dashboard access (bcrypt + SQLite)
- [x] AWS EC2 deployment (Docker + Nginx + HTTPS)
- [x] Secure environment variable handling (no secrets in Git)
- [x] AWS Cost Explorer integration via boto3
- [x] Automatic Demo Mode fallback
- [x] FinOps insights (total spend, MoM, top-3 concentration, anomaly, savings)
- [x] Time-series, bar, and donut charts
- [x] Data table with raw and summary views
- [x] Dockerfile + docker-compose
- [x] docs/ folder: AWS services, cost estimate, security, shutdown/budget, video script

---

## 📄 License

Submitted for educational purposes.

