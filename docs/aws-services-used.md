# AWS Services Used

This document lists the AWS and supporting services used in the Cloud Cost Management Panel project.

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

- **Purpose:** Network-level firewall controlling inbound traffic to the EC2 instance
- **Inbound rules configured:**
  - Port 22 (SSH) – restricted to deployer's IP only
  - Port 8501 (Streamlit) – open to 0.0.0.0/0 for public access

---

## 5. Amazon EBS (Elastic Block Store)

- **Purpose:** Root volume storage for the EC2 instance (OS + Docker images + SQLite database)
- **Type:** gp3 (General Purpose SSD)
- **Size:** 8–20 GB

---


## Summary Table

| Service | Type | Role |
|---|---|---|
| EC2 | Compute | Runs the Docker container |
| IAM | Security | Least-privilege credentials |
| Cost Explorer | Analytics | Real AWS cost data source |
| Security Groups | Networking | Firewall rules |
| EBS | Storage | Disk for EC2 instance |
