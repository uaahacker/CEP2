# 🛠️ AWS Services Used

This document lists all AWS and supporting services used in the **Cloud Cost Management Panel** project.

---

## 1. Amazon EC2 (Elastic Compute Cloud)

- **Purpose:** Hosts the Streamlit application inside a Docker container
- **Instance type:** t3.micro (Free Tier eligible) or t3.small
- **OS:** Ubuntu Server 22.04 LTS
- **Region:** e.g. us-east-1 (configurable)

---

## 2. AWS IAM (Identity and Access Management)

- **Purpose:** Provides secure, limited credentials for the app to call AWS Cost Explorer
- **Recommended setup:** Create a dedicated IAM user with only the `ce:GetCostAndUsage` permission
- **Do NOT use root credentials**

Required IAM policy:

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

---

## 3. AWS Cost Explorer

- **Purpose:** Source of real cloud spending data
- **API used:** `GetCostAndUsage`
- **Note:** Cost Explorer must be enabled in your AWS account  
  *(Billing → Cost Explorer → Enable)*
- **Fallback:** App auto-switches to Demo Mode if Cost Explorer is unavailable

---

## 4. EC2 Security Groups

- **Purpose:** Network-level firewall controlling inbound/outbound traffic to the EC2 instance
- **Inbound rules configured:**
  - Port 22 (SSH) – your IP only
  - Port 80 (HTTP) – 0.0.0.0/0 (redirected to HTTPS by Nginx)
  - Port 443 (HTTPS) – 0.0.0.0/0

---

## 5. Amazon EBS (Elastic Block Store)

- **Purpose:** Root volume storage for the EC2 instance (OS + Docker images + SQLite database)
- **Type:** gp3 (General Purpose SSD)
- **Size:** 20 GB (default 8 GB is sufficient for this project)

---

## 6. Nginx (installed on EC2)

- **Purpose:** Reverse proxy — forwards public HTTPS traffic on port 443 to the Docker container on port 8501
- **Also handles:** WebSocket upgrade headers required by Streamlit

---

## 7. Let's Encrypt / Certbot (installed on EC2)

- **Purpose:** Issues a free, trusted TLS/SSL certificate for HTTPS
- **Tool:** Certbot with the Nginx plugin
- **Certificate auto-renewal:** Managed by Certbot's cron/systemd timer

---

## 8. Optional: Amazon Route 53 (or external DNS)

- **Purpose:** Manages the domain name DNS records (A record pointing to EC2 public IP)
- **Alternative:** Use any external DNS provider (Cloudflare, GoDaddy, Namecheap, etc.)
- **Required for:** Let's Encrypt certificate issuance via domain validation

---

## Summary Table

| Service | Type | Role |
|---|---|---|
| EC2 | Compute | Runs the Docker container |
| IAM | Security | Least-privilege credentials |
| Cost Explorer | Analytics | Real AWS cost data source |
| Security Groups | Networking | Firewall rules |
| EBS | Storage | Disk for EC2 instance |
| Nginx | Proxy | HTTPS reverse proxy |
| Let's Encrypt | Certificate | Free TLS/SSL cert |
| Route 53 / DNS | DNS | Domain resolution (optional) |
