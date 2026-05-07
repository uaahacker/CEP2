# 🚀 AWS EC2 Deployment Guide

> Complete step-by-step guide to deploy **Cloud Cost Management Panel**  
> on AWS EC2 using Docker, Nginx, and HTTPS (Let's Encrypt).

---

## Prerequisites

- An AWS account
- An EC2 instance running **Ubuntu 22.04 LTS**
- A domain name or subdomain pointing to your EC2 public IP  
  *(e.g. `cloudcost.yourdomain.com`)*
- Your GitHub repository is pushed and public (or accessible)

---

## Step 1 – Launch EC2 Instance

1. Go to **EC2 → Launch Instance**
2. Choose **Ubuntu Server 22.04 LTS (64-bit x86)**
3. Instance type: **t3.micro** (Free Tier eligible) or **t3.small** for better performance
4. Key pair: create or select an existing `.pem` key

### Security Group Inbound Rules

| Type | Port | Source |
|---|---|---|
| SSH | 22 | Your IP only (not 0.0.0.0/0) |
| HTTP | 80 | 0.0.0.0/0 |
| HTTPS | 443 | 0.0.0.0/0 |

5. Storage: **20 GB gp3** (default 8 GB is fine too)
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
    docker-compose-plugin \
    nginx \
    certbot \
    python3-certbot-nginx \
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

## Step 4 – Clone Your GitHub Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/cloud-cost-management-panel.git
cd cloud-cost-management-panel
```

---

## Step 5 – Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Edit the values:

```env
# Add your real AWS credentials here (or leave blank for Demo Mode)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1

AUTH_DB_PATH=users.db
STREAMLIT_SERVER_PORT=8501
```

Save with `Ctrl+O`, exit with `Ctrl+X`.

---

## Step 6 – Build and Start the Docker Container

```bash
docker compose up -d --build
```

Verify the container is running:

```bash
docker ps
```

Test locally on the server:

```bash
curl http://localhost:8501/_stcore/health
```

You should see `{"status":"ok"}`.

---

## Step 7 – Configure Nginx as Reverse Proxy

Create the Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/cloud-cost-panel
```

Paste this configuration (replace `YOUR_DOMAIN_OR_SUBDOMAIN`):

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_SUBDOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/cloud-cost-panel \
           /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 8 – Enable HTTPS with Certbot (Let's Encrypt)

> **Prerequisite:** Your domain's DNS A record must point to the EC2 public IP.

```bash
sudo certbot --nginx -d YOUR_DOMAIN_OR_SUBDOMAIN
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose to redirect HTTP to HTTPS (recommended)

Certbot automatically updates your Nginx config and adds the SSL certificate.

Verify HTTPS:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Open a browser: **https://YOUR_DOMAIN_OR_SUBDOMAIN**

---

## Step 9 – Test the Deployment

1. Open **https://YOUR_DOMAIN_OR_SUBDOMAIN** in a browser
2. You should see the **Login / Sign Up** page
3. Create an account and log in
4. Check the mode badge:
   - Green = Real AWS data
   - Yellow = Demo Mode (no credentials)
5. Explore the dashboard

---

## Maintenance Commands

### View container logs

```bash
docker logs cloud-cost-panel
docker logs -f cloud-cost-panel   # follow (live tail)
```

### Stop the app

```bash
cd ~/cloud-cost-management-panel
docker compose down
```

### Update after pushing new code to GitHub

```bash
cd ~/cloud-cost-management-panel
git pull
docker compose up -d --build
```

### Restart the app

```bash
docker compose restart
```

### Renew SSL certificate (auto-renews via cron, but manual test)

```bash
sudo certbot renew --dry-run
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `docker: permission denied` | Run `newgrp docker` or re-login |
| `502 Bad Gateway` | Container not running – check `docker ps` and `docker logs` |
| `curl: connection refused` on port 8501 | Container not started – `docker compose up -d` |
| Certbot fails | Check DNS A record points to EC2 IP; port 80 must be open |
| App shows error on data load | AWS credentials may be wrong – will fall back to Demo Mode |

---

## Security Checklist Before Sharing Live URL

- [ ] `.env` is **not** committed to GitHub
- [ ] EC2 Security Group SSH (port 22) restricted to your IP only
- [ ] HTTPS is enabled and HTTP redirects to HTTPS
- [ ] AWS IAM user has only `ce:GetCostAndUsage` permission
- [ ] Root AWS credentials are NOT used
- [ ] Set AWS Budget alert (see `docs/shutdown-budget-controls.md`)
