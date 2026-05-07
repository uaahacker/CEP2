# Security Assumptions

This document describes the security design decisions for the Cloud Cost Management Panel project.

---

## Scope

This is an **academic demo project**. The security measures below are appropriate for a course assignment. For a real production application, additional hardening would be required.

---

## 1. Authentication

### What is used
- Simple **email + password** login/signup
- Passwords are hashed with **bcrypt** before storage
- User records are stored in a local **SQLite** database (`users.db`)
- Session state is managed by Streamlit `st.session_state`

### What is NOT used (but recommended for production)
- **AWS Cognito** – managed identity service with MFA, federated login, and token management
- **OAuth 2.0 / OpenID Connect** – for enterprise SSO
- **Session expiry / JWT tokens** – for stateless authentication

### Security properties of the demo auth
- Passwords are **never stored in plain text** — bcrypt hash is stored
- Duplicate email signup is prevented by SQLite UNIQUE constraint
- Password minimum length of 6 characters is enforced
- Empty email/password submission is rejected

---

## 2. AWS Credentials

- AWS credentials are stored in **environment variables only** (`.env` file)
- The `.env` file is listed in `.gitignore` and must **never be committed to GitHub**
- The `.env.example` file (committed to GitHub) contains only placeholder values
- The app falls back to Demo Mode automatically when credentials are absent

### IAM Principle of Least Privilege

Only the minimum IAM permission needed is granted:

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

- Do **not** use root AWS account credentials
- Create a dedicated IAM user with only `ce:GetCostAndUsage`
- Consider using an **IAM role** attached to the EC2 instance instead of access keys

---

## 3. Network Access

The app is served over plain HTTP on port 8501 for this academic demo deployment. There is no domain name and no TLS certificate configured.

For a production deployment, HTTPS would be added using a load balancer with an AWS ACM certificate, or Nginx with Let's Encrypt once a domain is available.

---

## 4. Network Security (EC2 Security Group)

| Port | Access | Reason |
|---|---|---|
| 22 (SSH) | Your IP only | Prevents brute-force SSH attacks |
| 8501 (Streamlit) | 0.0.0.0/0 | Public access to the app |

---

## 5. Data Privacy

- The app displays **demo/synthetic data** by default — no real AWS billing data is exposed publicly
- Real AWS cost data is only loaded when valid credentials are configured
- The app does not collect, store, or transmit user personal data beyond the email/password login

---

## 6. Docker Security

- The Docker container runs the application in an isolated environment
- The container does not run as root (Python slim image default)
- `.env` file is passed via `env_file` in docker-compose — not baked into the image

---

## 7. What Would Change in Production

| Area | Demo | Production |
|---|---|---|
| Authentication | SQLite + bcrypt | AWS Cognito / Auth0 |
| Secrets management | `.env` file | AWS Secrets Manager |
| Database | SQLite | Amazon RDS or DynamoDB |
| HTTPS | Not configured (demo) | AWS ACM + ALB |
| Logging | Docker logs | AWS CloudWatch |
| IAM | Access keys | IAM Role on EC2 |
| Input validation | Basic | Comprehensive (OWASP) |
