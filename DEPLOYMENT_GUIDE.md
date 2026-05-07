# AWS EC2 Deployment Guide

Step-by-step instructions to deploy the Cloud Cost Management Panel on AWS EC2 using Docker.

---

## Prerequisites

- An AWS account
- An EC2 instance running Ubuntu 22.04 LTS
- Your GitHub repository accessible from the server

---

## Step 1 – Launch EC2 Instance

1. Go to EC2 → Launch Instance
2. Choose Ubuntu Server 22.04 LTS (64-bit x86)
3. Instance type: t3.micro (Free Tier eligible)
4. Key pair: create or select an existing .pem key

### Security Group Inbound Rules

| Type | Port | Source |
|---|---|---|
| SSH | 22 | Your IP only |
| Custom TCP | 8501 | 0.0.0.0/0 |

5. Storage: 8 GB gp3 (default) is sufficient
6. Launch the instance

---

## Step 2 – Connect via SSH

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 3 – Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    docker.io \
    docker-compose \
    git \
    curl

# Start and enable Docker
sudo systemctl enable docker
sudo systemctl start docker

# Allow ubuntu user to run Docker without sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

---

## Step 4 – Clone the Repository

```bash
cd ~
git clone https://github.com/uaahacker/CEP2.git
cd CEP2
```

---

## Step 5 – Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Edit the values:

```env
# AWS credentials (optional – leave blank for Demo Mode)
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_DEFAULT_REGION=us-east-1

AUTH_DB_PATH=/app/data/users.db
STREAMLIT_SERVER_PORT=8501
```

Save with `Ctrl+O`, exit with `Ctrl+X`.

---

## Step 6 – Build and Start the Container

```bash
mkdir -p data
docker-compose up -d --build
```

Verify the container is running:

```bash
docker-compose ps
```

Test the health endpoint:

```bash
curl http://localhost:8501/_stcore/health
```

You should see `ok`.

---

## Step 7 – Access the App

Open a browser and go to:

```
http://YOUR_EC2_PUBLIC_IP:8501
```

You should see the login page. Use the Sign Up tab to create an account.

---

## Maintenance Commands

### View container logs

```bash
docker-compose logs cloud-cost-panel
docker-compose logs -f cloud-cost-panel   # follow live
```

### Stop the app

```bash
cd ~/CEP2
docker-compose down
```

### Update after pushing new code

```bash
cd ~/CEP2
git pull
docker-compose up -d --build
```

### Restart

```bash
docker-compose restart
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `docker: permission denied` | Run `newgrp docker` or re-login |
| Cannot connect on port 8501 | Check EC2 security group has inbound rule for port 8501 |
| SQLite error on startup | Ensure `./data` directory exists and `AUTH_DB_PATH=/app/data/users.db` is set in .env |
| App shows error on data load | AWS credentials may be wrong – app falls back to Demo Mode automatically |

---

## Security Notes

- SSH access is restricted to your IP only
- Port 8501 is open to the internet for demo purposes
- Do not commit `.env` to GitHub
- Stop or terminate the EC2 instance after the demo to avoid ongoing charges
