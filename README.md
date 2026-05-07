# Cloud Cost Management Panel

Cloud Computing Assignment – Final Submission

An AWS FinOps dashboard with user authentication, AWS Cost Explorer integration, and Demo Mode fallback, deployed on AWS EC2.

---

## Deliverables

| Item | Link |
|---|---|
| Live App | http://44.204.153.21:8501 |
| GitHub Repository | https://github.com/uaahacker/CEP2 |

---

## Features

| Feature | Description |
|---|---|
| Login / Sign Up | Email and bcrypt-hashed password, SQLite storage |
| Date Range Filter | Pick any start/end date; defaults to last 30 days |
| Granularity | Daily or Monthly aggregation |
| Cost Metric | Unblended Cost or Amortized Cost |
| Group By | Slice by Service, Region, or Linked Account |
| Top-N Filter | Show top 3–15 groups |
| Cost Reduction Slider | Simulate 0–30% cost reduction in real time |
| Time-Series Chart | Actual vs Projected cost |
| Bar Chart | Top-N groups ranked by total spend |
| Donut Chart | Cost distribution |
| FinOps Insights | Total spend, period-over-period change, top-3 concentration, anomaly detection, projected savings |
| Data Table | Raw data + group summary |
| Demo Mode | Automatic fallback with synthetic data when AWS credentials are not present |
| Deployed | AWS EC2, Docker, direct port access |

---

## Tech Stack

| Component | Technology |
|---|---|
| Web framework | Python 3.11, Streamlit |
| Cloud SDK | boto3 (AWS Cost Explorer) |
| Data | pandas, numpy |
| Charts | Plotly |
| Authentication | SQLite + bcrypt |
| Container | Docker, docker-compose |
| Hosting | AWS EC2 t3.micro, Ubuntu 22.04 |

---

## Project Structure

```
CEP2/
├── app.py               Main Streamlit application
├── auth.py              Login, signup, session management
├── cost_data.py         AWS Cost Explorer and Demo Mode data
├── insights.py          FinOps metric calculations
├── charts.py            Plotly chart builders
├── requirements.txt     Python dependencies
├── Dockerfile           Container definition
├── docker-compose.yml   Docker Compose config
├── .env.example         Environment variable template
├── README.md            This file
├── DEPLOYMENT_GUIDE.md  EC2 deployment steps
└── docs/
    ├── aws-services-used.md
    ├── cost-estimate.md
    ├── security-assumptions.md
    ├── shutdown-budget-controls.md
    └── video-script.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/uaahacker/CEP2.git
cd CEP2
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

## Run Without Docker

```bash
streamlit run app.py
```

Opens at http://localhost:8501

---

## Run With Docker

```bash
cp .env.example .env
# Add real AWS credentials to .env (optional)

docker-compose up -d --build
```

Opens at http://localhost:8501

Stop:
```bash
docker-compose down
```

---

## Authentication

The app uses a simple email/password system suitable for an academic demo:

- New users register on the Sign Up tab
- Passwords are hashed with bcrypt before storage — never stored in plain text
- User data is kept in a SQLite database
- Sessions are managed through Streamlit's session state
- A logout button is available in the sidebar

For a production system, this would be replaced with AWS Cognito or another managed identity provider.

---

## AWS Cost Explorer

When valid AWS credentials are present, the app calls `GetCostAndUsage` from AWS Cost Explorer.

Required IAM permission:

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

Do not use root account credentials. Create a dedicated IAM user with only this permission.

---

## Demo Mode

If credentials are absent or invalid, the app switches automatically to Demo Mode. A yellow badge appears at the top of the dashboard. The synthetic data covers EC2, S3, RDS, Lambda, CloudFront, DynamoDB, VPC, and EKS, and includes a built-in cost spike to demonstrate anomaly detection. All filters and charts work identically.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
AUTH_DB_PATH=/app/data/users.db
STREAMLIT_SERVER_PORT=8501
```

Do not commit `.env` to Git. It is already in `.gitignore`.

---

## Deployment

The app runs on AWS EC2 (t3.micro, Ubuntu 22.04) inside Docker. Port 8501 is exposed directly via an EC2 security group rule.

Full setup instructions: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

```
GitHub Repo
    ↓  git clone
EC2 Instance (Ubuntu 22.04)
    ↓  docker-compose up -d --build
Docker Container (Streamlit :8501)
    ↓  EC2 Security Group (port 8501 open)
Public URL: http://44.204.153.21:8501
```

---

## Assignment Requirements

- [x] GitHub version control with README and project structure
- [x] Public-facing Streamlit web app
- [x] Login and signup before dashboard access (bcrypt + SQLite)
- [x] AWS EC2 deployment with Docker
- [x] Secure environment variable handling (no secrets in Git)
- [x] AWS Cost Explorer integration via boto3
- [x] Automatic Demo Mode fallback
- [x] FinOps insights (total spend, MoM change, top-3 concentration, anomaly detection, savings projection)
- [x] Time-series, bar, and donut charts
- [x] Data table with raw and summary views
- [x] Dockerfile and docker-compose
- [x] docs/ folder with AWS services, cost estimate, security assumptions, and shutdown/budget controls

---

## License

Submitted for educational purposes.

