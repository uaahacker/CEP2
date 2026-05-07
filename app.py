"""
Cloud Cost Management Panel
============================
Main Streamlit application entry point.

Architecture:
    app.py        ← this file, UI orchestration only
    auth.py       ← login / signup / session management
    cost_data.py  ← AWS Cost Explorer + Demo Mode data fetching
    insights.py   ← FinOps metric calculations
    charts.py     ← Plotly chart builders

Run locally:
    streamlit run app.py

Run with Docker:
    docker compose up -d --build
"""

import streamlit as st
from datetime import timedelta, date

# ── Local modules ─────────────────────────────────────────────────────────────
from auth import require_login, logout_user
from cost_data import check_aws_credentials, get_cost_data
from insights import calculate_all_insights
from charts import create_time_series_chart, create_bar_chart, create_pie_chart

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cloud Cost Management Panel",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  – polished dark-accented theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header gradient */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #e94560;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 1px;
    }
    .main-header p {
        color: #a8b2d8;
        margin: 0.4rem 0 0 0;
        font-size: 1rem;
    }

    /* Mode badge */
    .mode-badge-demo {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: #1a1a2e;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .mode-badge-live {
        background: linear-gradient(90deg, #11998e, #38ef7d);
        color: #1a1a2e;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }

    /* Insight cards */
    .insight-card {
        background: linear-gradient(135deg, #1e3a5f, #16213e);
        border: 1px solid #0f3460;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .insight-card h4 {
        color: #e94560;
        margin: 0 0 0.4rem 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .insight-card p {
        color: #cdd6f4;
        margin: 0;
        font-size: 0.95rem;
    }

    /* Section divider */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e94560;
        border-left: 4px solid #e94560;
        padding-left: 0.7rem;
        margin: 1.2rem 0 0.8rem 0;
    }

    /* Metric card override */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e3a5f, #16213e);
        border: 1px solid #0f3460;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Entry point for the Streamlit app.

    Flow:
        1. require_login()           – shows auth UI and stops if not logged in
        2. Sidebar filters           – date, granularity, metric, group-by, top-N, reduction
        3. check_aws_credentials()   – probe real AWS connectivity
        4. get_cost_data()           – fetch real or synthetic cost data
        5. calculate_all_insights()  – compute FinOps metrics
        6. Render tabs: Dashboard | FinOps Insights | Data Table | About
    """

    # ── STEP 1: Authentication gate ───────────────────────────────────────────
    # require_login() renders login/signup UI and calls st.stop() if not authenticated.
    user_email = require_login()

    # ── Page Header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="main-header">
        <h1>☁️ Cloud Cost Management Panel</h1>
        <p>Interactive AWS FinOps Dashboard &nbsp;·&nbsp;
           Logged in as <b>{user_email}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SIDEBAR – filters and logout button
    # ─────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard Controls")
        st.markdown(f"👤 **{user_email}**")

        if st.button("🚪 Log Out", use_container_width=True):
            logout_user()   # clears session state and triggers st.rerun()

        st.markdown("---")

        st.markdown("### 📅 Date Range")
        today = date.today()
        default_start = today - timedelta(days=30)
        start_date = st.date_input("Start Date", value=default_start, max_value=today)
        end_date = st.date_input("End Date", value=today, min_value=start_date)

        if start_date >= end_date:
            st.error("⚠️ Start date must be before end date.")
            st.stop()

        st.markdown("---")

        st.markdown("### 📊 Granularity")
        granularity = st.selectbox("Select Granularity", ["DAILY", "MONTHLY"])

        st.markdown("### 💰 Cost Metric")
        metric_display = st.selectbox(
            "Select Metric", ["Unblended Cost", "Amortized Cost"]
        )
        metric_map = {
            "Unblended Cost": "UnblendedCost",
            "Amortized Cost": "AmortizedCost",
        }
        metric = metric_map[metric_display]

        st.markdown("### 🗂️ Group By")
        group_display = st.selectbox(
            "Group By", ["Service", "Region", "Linked Account"]
        )
        group_map = {
            "Service": "SERVICE",
            "Region": "REGION",
            "Linked Account": "LINKED_ACCOUNT",
        }
        group_by = group_map[group_display]

        st.markdown("---")

        st.markdown("### 🏆 Top-N Groups")
        top_n = st.slider("Show Top N Groups", min_value=3, max_value=15, value=5)

        st.markdown("### ✂️ Cost Reduction Policy")
        reduction_pct = st.slider(
            "Reduction Target (%)",
            min_value=0, max_value=30, value=10,
            help="Simulate applying a cost-saving policy across all groups.",
        )

        st.markdown("---")
        st.markdown("""
        <small style='color:#a8b2d8;'>
        💡 Set AWS credentials via <code>aws configure</code>
        or environment variables to enable live data.
        </small>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Detect AWS connectivity
    # ─────────────────────────────────────────────────────────────────────────
    with st.spinner("Checking AWS connectivity…"):
        aws_available = check_aws_credentials()

    col_badge, _ = st.columns([4, 4])
    with col_badge:
        if aws_available:
            st.markdown(
                '<span class="mode-badge-live">'
                "✅ Real AWS Mode – Connected to Cost Explorer"
                "</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="mode-badge-demo">'
                "⚠️ Demo Mode – AWS credentials not detected, using synthetic data"
                "</span>",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Fetch or generate data
    # ─────────────────────────────────────────────────────────────────────────
    with st.spinner("Loading cost data…"):
        df, is_real = get_cost_data(
            start_date, end_date, granularity, metric, group_by, aws_available
        )

    if not is_real and aws_available:
        st.warning(
            "AWS Cost Explorer returned no data for the selected period. "
            "Switched to Demo Mode automatically."
        )

    if df is None or df.empty:
        st.error("No data available. Please adjust the date range and try again.")
        st.stop()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Compute insights
    # ─────────────────────────────────────────────────────────────────────────
    insights = calculate_all_insights(df, reduction_pct)

    # ─────────────────────────────────────────────────────────────────────────
    # TABBED LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    tab_dash, tab_insights, tab_data, tab_about = st.tabs([
        "📊 Dashboard",
        "💡 FinOps Insights",
        "📋 Data Table",
        "ℹ️ About / Deployment",
    ])

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 1 – DASHBOARD
    # ═════════════════════════════════════════════════════════════════════════
    with tab_dash:

        st.markdown('<p class="section-title">📌 Key Metrics</p>', unsafe_allow_html=True)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.metric("💵 Total AWS Spend", f"${insights['total_spend']:,.2f}")

        with kpi2:
            mom = insights["mom_change"]
            if mom is not None:
                delta_str = f"{mom:+.1f}%"
                st.metric("📈 Period-over-Period Change", delta_str,
                          delta=delta_str, delta_color="inverse")
            else:
                st.metric("📈 Period-over-Period Change", "N/A")

        with kpi3:
            st.metric(
                "🏅 Top-3 Concentration",
                f"{insights['top3_concentration']}%",
                help="Share of total spend from the top 3 groups.",
            )

        with kpi4:
            st.metric(
                f"✂️ Projected Savings ({reduction_pct}%)",
                f"${insights['projected_savings']:,.2f}",
                delta=f"New total: ${insights['projected_cost']:,.2f}",
                delta_color="off",
            )

        st.markdown("---")
        st.markdown('<p class="section-title">📊 Cost Visualisations</p>',
                    unsafe_allow_html=True)

        chart_ts, chart_bar, chart_pie = st.tabs([
            "📈 Time Series", "📊 Top-N Bar Chart", "🍩 Distribution"
        ])

        with chart_ts:
            st.plotly_chart(
                create_time_series_chart(df, reduction_pct), use_container_width=True
            )
        with chart_bar:
            st.plotly_chart(create_bar_chart(df, top_n), use_container_width=True)
        with chart_pie:
            st.plotly_chart(create_pie_chart(df, top_n), use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 2 – FINOPS INSIGHTS
    # ═════════════════════════════════════════════════════════════════════════
    with tab_insights:

        st.markdown('<p class="section-title">💡 FinOps Insight Panel</p>',
                    unsafe_allow_html=True)
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"""
            <div class="insight-card">
                <h4>💵 Total Spend</h4>
                <p>Total AWS Spend: <b>${insights['total_spend']:,.2f}</b></p>
            </div>""", unsafe_allow_html=True)

            mom = insights["mom_change"]
            if mom is not None:
                direction = "increased" if mom > 0 else "decreased"
                arrow = "🔴" if mom > 0 else "🟢"
                mom_text = (
                    f"{arrow} Costs <b>{direction}</b> by <b>{abs(mom):.1f}%</b>"
                    " vs. the previous equivalent period."
                )
            else:
                mom_text = "Not enough data for period comparison."

            st.markdown(f"""
            <div class="insight-card">
                <h4>📈 Period-over-Period Change</h4>
                <p>{mom_text}</p>
            </div>""", unsafe_allow_html=True)

            top3_str = ", ".join(insights["top3_names"])
            st.markdown(f"""
            <div class="insight-card">
                <h4>🏅 Top-3 Service Concentration</h4>
                <p>Top 3 groups (<i>{top3_str}</i>) account for
                <b>{insights['top3_concentration']}%</b> of total spend.</p>
            </div>""", unsafe_allow_html=True)

        with col_right:
            anom_count = insights["anomaly_count"]
            if anom_count == 0:
                anomaly_body = "<p>✅ No major anomalies detected in the selected period.</p>"
            else:
                rows_html = "".join(
                    f"<li><b>{d}</b> — ${c:,.2f}</li>"
                    for d, c in insights["anomaly_dates"][:5]
                )
                anomaly_body = (
                    f"<p>⚠️ <b>{anom_count} "
                    f"anomal{'y' if anom_count == 1 else 'ies'} detected</b> "
                    f"(threshold: ${insights['anomaly_threshold']:,.2f}/period):<br>"
                    f"<ul style='margin:0.3rem 0 0 1rem;'>{rows_html}</ul></p>"
                )

            st.markdown(f"""
            <div class="insight-card">
                <h4>🔍 Anomaly Detection (mean ± 2σ)</h4>
                {anomaly_body}
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="insight-card">
                <h4>✂️ Projected Savings ({reduction_pct}% Reduction)</h4>
                <p>Estimated Savings: <b>${insights['projected_savings']:,.2f}</b><br>
                Projected Total after reduction: <b>${insights['projected_cost']:,.2f}</b></p>
            </div>""", unsafe_allow_html=True)

            mom = insights["mom_change"]
            if mom is not None and mom > 10:
                reco = ("📌 Costs are rising quickly. Consider rightsizing EC2 "
                        "instances or enabling Savings Plans.")
            elif insights["top3_concentration"] > 80:
                reco = ("📌 Spend is highly concentrated. Optimise your top services.")
            elif anom_count > 0:
                reco = ("📌 Review anomaly dates for unexpected spikes "
                        "or misconfigured resources.")
            else:
                reco = ("📌 Costs look stable. Keep monitoring and review "
                        "Reserved Instance coverage.")

            st.markdown(f"""
            <div class="insight-card">
                <h4>🧠 Smart Recommendation</h4>
                <p>{reco}</p>
            </div>""", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 3 – DATA TABLE
    # ═════════════════════════════════════════════════════════════════════════
    with tab_data:

        st.markdown('<p class="section-title">📋 Raw Cost Data</p>',
                    unsafe_allow_html=True)
        col_tbl, col_summary = st.columns([3, 1])

        with col_tbl:
            pivot = (
                df.groupby(["Date", "Group"])["Cost"]
                .sum()
                .reset_index()
                .sort_values(["Date", "Cost"], ascending=[True, False])
            )
            pivot["Date"] = pivot["Date"].dt.strftime("%Y-%m-%d")
            pivot["Cost"] = pivot["Cost"].round(4)
            st.dataframe(
                pivot.rename(columns={"Group": group_display, "Cost": "Cost (USD)"}),
                use_container_width=True,
                hide_index=True,
            )

        with col_summary:
            st.markdown("**Summary by Group**")
            summary = (
                df.groupby("Group")["Cost"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            summary["Cost"] = summary["Cost"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(
                summary.rename(columns={"Group": group_display, "Cost": "Total Cost"}),
                use_container_width=True,
                hide_index=True,
            )

    # ═════════════════════════════════════════════════════════════════════════
    # TAB 4 – ABOUT / DEPLOYMENT NOTES
    # ═════════════════════════════════════════════════════════════════════════
    with tab_about:

        st.markdown("## ℹ️ About This Project")
        st.markdown("""
        **Cloud Cost Management Panel** is an AWS FinOps dashboard built as part
        of a cloud computing assignment.

        | Component | Technology |
        |---|---|
        | Web framework | Streamlit |
        | Cloud SDK | boto3 (AWS Cost Explorer) |
        | Data processing | pandas, numpy |
        | Charts | Plotly |
        | Authentication | SQLite + bcrypt |
        | Container | Docker |
        | Reverse proxy | Nginx |
        | HTTPS | Let's Encrypt / Certbot |
        | Hosting | AWS EC2 Ubuntu |
        """)

        st.markdown("---")
        st.markdown("## 🚀 Deployment Summary")
        st.markdown("""
        ```
        EC2 Instance  →  Docker (Streamlit app :8501)
                      →  Nginx reverse proxy (:80 / :443 HTTPS)
                      →  Let's Encrypt SSL certificate
        ```
        Full step-by-step commands are in **DEPLOYMENT_GUIDE.md**.
        """)

        st.markdown("---")
        st.markdown("## 🔑 Authentication Note")
        st.markdown("""
        This app uses simplified **academic-demo authentication**:
        - Users stored in local **SQLite** (`users.db`)
        - Passwords hashed with **bcrypt** (never plain text)

        > **Production note:** Replace with **AWS Cognito** or a managed
        > identity provider for real workloads.
        """)

        st.markdown("---")
        st.markdown("## 📋 Final Deliverables")
        st.markdown("""
        | Deliverable | Link |
        |---|---|
        | Live App URL | *(add after deployment)* |
        | GitHub Repo URL | *(add after push)* |
        """)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<center><small style='color:#555;'>"
        "Cloud Cost Management Panel &nbsp;·&nbsp; "
        "Built with Streamlit, boto3, pandas &amp; Plotly &nbsp;·&nbsp; "
        "Assignment Submission"
        "</small></center>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

