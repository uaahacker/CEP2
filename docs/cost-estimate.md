# Cost Estimate

Approximate monthly AWS cost for running this academic demo project. Actual costs depend on region, usage, and AWS pricing changes.

---

## Assumptions

- Region: **us-east-1** (N. Virginia)
- Instance: **t3.micro** (Free Tier eligible for new accounts, 12 months)
- Storage: **20 GB gp3** EBS
- Traffic: Low (academic demo — a few GB outbound per month)
- Running: **24/7** for one month

---

## Monthly Cost Breakdown

| Service | Config | Estimated Monthly Cost |
|---|---|---|
| EC2 t3.micro | 730 hours/month | ~$8.50 (or $0 if Free Tier) |
| EBS gp3 20 GB | 20 GB × $0.08/GB | ~$1.60 |
| Data Transfer Out | ~5 GB | ~$0.45 |
| Elastic IP (if used) | 1 EIP while running | ~$0.00 |
| AWS Cost Explorer | API calls | ~$0.01 (fractions of a cent) |
| **Total (estimated)** | | **~$10.50 / month** |

---

## Free Tier Note

If your AWS account is **less than 12 months old**:

- EC2 t2.micro or t3.micro: **750 hours/month FREE**
- EBS: **30 GB FREE**
- Data Transfer: **15 GB outbound FREE**

Under Free Tier, this project costs approximately **$0/month**.

---

## Cost Reduction Tips

- **Stop the EC2 instance** when not in use (e.g. after demo presentation)  
  A stopped instance does not incur compute charges, only EBS storage costs (~$1.60/month)
- **Terminate the instance** when the project is completely finished
- Use **t3.micro** instead of larger instance types
- Set a **AWS Budget alert** at $5 to get notified before costs exceed expectations

---

## Important Notes

- AWS Cost Explorer API calls are very cheap (~$0.01/month for low usage)
- The app uses Demo Mode by default — real AWS API calls only happen when credentials are configured
- Data transfer costs are negligible for a demo with a few users
- Actual cost may vary; always check the [AWS Pricing Calculator](https://calculator.aws/)
