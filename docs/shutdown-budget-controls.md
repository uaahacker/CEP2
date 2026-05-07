# 🛑 Shutdown & Budget Controls

This document describes how to control costs and safely shut down the **Cloud Cost Management Panel** project after the demo.

---

## 1. Set an AWS Budget Alert (Do This First)

Before running the app on EC2, set a budget alert so you are notified if costs unexpectedly exceed a threshold.

**Steps:**
1. Go to **AWS Console → Billing → Budgets**
2. Click **Create budget**
3. Choose **Cost budget**
4. Set amount: `$10` (or any threshold you're comfortable with)
5. Set alert at **80% of budget ($8)**
6. Add your email for notifications
7. Save the budget

---

## 2. Stop the EC2 Instance After the Demo

A **stopped** EC2 instance does not incur compute charges.  
You only pay for the EBS storage (~$1.60/month for 20 GB).

**To stop:**
```
AWS Console → EC2 → Instances → Select instance → Instance State → Stop
```

Or via AWS CLI:
```bash
aws ec2 stop-instances --instance-ids i-YOURINSTANCEID
```

**To restart later:**
```
AWS Console → EC2 → Instance State → Start
```

---

## 3. Stop the Docker App Without Stopping EC2

If the EC2 instance is still running but you want to stop the app:

```bash
ssh into your EC2 instance
cd ~/cloud-cost-management-panel
docker compose down
```

---

## 4. Terminate the EC2 Instance When Project is Finished

**Warning:** Terminating an instance permanently deletes it and its local storage.

```
AWS Console → EC2 → Instances → Select instance → Instance State → Terminate
```

Or via AWS CLI:
```bash
aws ec2 terminate-instances --instance-ids i-YOURINSTANCEID
```

Make sure you have saved anything you need (e.g. the `users.db` file) before terminating.

---

## 5. Remove or Rotate AWS Access Keys After Demo

1. Go to **AWS Console → IAM → Users → Your User → Security credentials**
2. Click **Deactivate** on the access key used for this project
3. After confirming the project is complete, click **Delete**

This prevents accidental charges if the key is compromised.

---

## 6. Use Demo Mode to Avoid Real Billing Data Dependency

The app automatically uses **Demo Mode** when AWS credentials are not set.

For a classroom demo or video recording, you can:
- Simply not set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
- The app will run with synthetic data — no real AWS API calls are made
- This avoids both billing and the risk of exposing real cost data

---

## 7. Release Elastic IP (if assigned)

If you assigned an Elastic IP to the instance, release it after termination:

```
AWS Console → EC2 → Elastic IPs → Select IP → Release Elastic IP address
```

An Elastic IP not associated with a running instance incurs charges (~$0.005/hour).

---

## 8. Quick Shutdown Checklist

After the demo presentation is complete:

- [ ] Run `docker compose down` on the EC2 instance
- [ ] Stop or terminate the EC2 instance
- [ ] Deactivate and delete the IAM access key used
- [ ] Release any Elastic IP
- [ ] Confirm in AWS Billing Dashboard that no unexpected charges are running
- [ ] Disable AWS Cost Explorer if it was just enabled for this project
