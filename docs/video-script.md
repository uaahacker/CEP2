# 🎬 Video Presentation Script

> **Target length:** ~2 minutes  
> **Tone:** Simple, student-style, conversational

---

## Recording Checklist

Before hitting record:

1. [ ] Show GitHub repository (code, README, docs/)
2. [ ] Show the live URL in the browser (HTTPS)
3. [ ] Show the Login / Sign Up page
4. [ ] Create a new account (Sign Up tab)
5. [ ] Log in with the new account
6. [ ] Show the Dashboard in Demo Mode (yellow badge)
7. [ ] Change sidebar filters (date, granularity, group-by, top-N, reduction slider)
8. [ ] Show the Time Series chart updating
9. [ ] Show the Bar Chart and Donut Chart
10. [ ] Open the FinOps Insights tab and explain each card
11. [ ] Open the Data Table tab
12. [ ] Open the About / Deployment tab
13. [ ] (Optional) Show Real AWS Mode if credentials are configured
14. [ ] Mention Docker, Nginx, HTTPS deployment

---

## Video Script

---

*[Screen: GitHub repository page]*

Hello everyone. My name is [Your Name], and this is my **Cloud Cost Management Panel** project. This is the GitHub repository. You can see the project has multiple files: `app.py`, `auth.py`, `cost_data.py`, `insights.py`, `charts.py`, Docker files, a deployment guide, and a docs folder with all the required documentation.

---

*[Screen: Browser → Live HTTPS URL]*

Now let me open the live application. I deployed this on **AWS EC2** using Docker and Nginx, with a free HTTPS certificate from Let's Encrypt. You can see the URL is using HTTPS.

---

*[Screen: Login / Sign Up page]*

The first thing users see is the login page. I added authentication before the dashboard is accessible. There are two tabs — Log In and Sign Up.

Let me create a new account.

*[Type email and password in Sign Up tab, click Create Account]*

Account created. Now let me log in.

*[Log in with the same credentials]*

---

*[Screen: Dashboard]*

I am now inside the dashboard. You can see at the top it says **Demo Mode** with a yellow badge. That means AWS credentials are not configured on this server, so the app is automatically using realistic synthetic data. This is a built-in fallback so the app always works.

If I configure real AWS credentials in the `.env` file, this badge turns green and the app pulls live data from **AWS Cost Explorer** using the `GetCostAndUsage` API via boto3.

---

*[Screen: Sidebar controls]*

On the left sidebar, I have several controls. I can choose the **date range**, switch between **Daily or Monthly** granularity, pick the **cost metric** — Unblended or Amortized — and **group the data** by Service, Region, or Linked Account. There is also a **Top-N slider** and a **Cost Reduction slider** from 0 to 30 percent.

Let me change the group-by to Region and increase the reduction to 20 percent.

*[Adjust controls and let the dashboard update]*

---

*[Screen: Charts tabs]*

The dashboard has three chart types. The **Time Series** chart shows actual cost as a red line and projected cost after the reduction policy as a green dashed line. The **Bar Chart** shows the top services ranked by total spend. The **Donut Chart** shows cost distribution.

---

*[Screen: FinOps Insights tab]*

This is the **FinOps Insights** panel. It shows the **total spend**, **period-over-period percentage change**, **top-3 service concentration** — which tells you what percentage of your bill comes from just three services — **anomaly detection** using the mean plus two standard deviations rule, and **projected savings** from the cost reduction policy.

You can see there is an anomaly detected because I injected a deliberate cost spike in the demo data to make the anomaly detection feature visible.

---

*[Screen: Data Table tab]*

Here is the **raw data table** where you can see every record, and a summary by group on the right.

---

*[Screen: About / Deployment tab]*

And in the About tab, I explain the technology stack and how the app is deployed.

---

*[Screen: Show deployment briefly]*

The deployment uses:
- **Docker** to containerise the Streamlit app
- **Nginx** as a reverse proxy
- **Let's Encrypt** for free HTTPS

All the deployment steps are documented in **DEPLOYMENT_GUIDE.md** in the repository.

---

For security, I used **bcrypt** for password hashing, stored credentials only in environment variables — never in the code — and gave the AWS IAM user only the `ce:GetCostAndUsage` permission following the principle of least privilege.

---

*[Screen: Return to GitHub]*

Overall, this project shows how Python and Streamlit can be used to build a professional FinOps dashboard, deployed as a real cloud service with proper security and documentation. Thank you.

---

## Recording Tips

- Screen resolution: **1920 × 1080** at **100%** browser zoom
- Use a quiet environment
- Speak at a natural pace
- Have the live URL and GitHub URL ready to show
- Test the login flow before recording
