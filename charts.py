"""
charts.py – Plotly Chart Builders
===================================
All chart creation functions are kept here to keep app.py clean.

Each function returns a plotly.graph_objects.Figure that can be passed
directly to st.plotly_chart().

Public API:
    create_time_series_chart(df, reduction_pct) -> go.Figure
    create_bar_chart(df, top_n)                 -> go.Figure
    create_pie_chart(df, top_n)                 -> go.Figure
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ── Shared dark theme layout defaults ────────────────────────────────────────
_DARK_LAYOUT = dict(
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    font=dict(color="#cdd6f4", family="Inter, sans-serif"),
)


# ─────────────────────────────────────────────────────────────────────────────
# TIME-SERIES CHART
# ─────────────────────────────────────────────────────────────────────────────

def create_time_series_chart(df: pd.DataFrame, reduction_pct: float) -> go.Figure:
    """
    Line chart showing:
        - Actual Cost (red solid line)
        - Projected Cost After Reduction (green dashed line)

    Args:
        df:            DataFrame[Date, Group, Cost].
        reduction_pct: Reduction percentage for the projected line (0–30).

    Returns:
        A Plotly Figure ready for st.plotly_chart().
    """
    # Aggregate all groups into a single daily total
    daily = df.groupby("Date")["Cost"].sum().reset_index().sort_values("Date")
    daily["Projected Cost"] = daily["Cost"] * (1 - reduction_pct / 100)

    fig = go.Figure()

    # Actual cost trace
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Cost"],
        mode="lines+markers",
        name="Actual Cost",
        line=dict(color="#e94560", width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Actual: $%{y:,.2f}<extra></extra>",
    ))

    # Projected cost trace
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Projected Cost"],
        mode="lines",
        name=f"Projected (−{reduction_pct:.0f}%)",
        line=dict(color="#38ef7d", width=2, dash="dash"),
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Projected: $%{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        **_DARK_LAYOUT,
        title=dict(text="Cost Over Time (Actual vs Projected)", x=0, font=dict(size=16)),
        xaxis=dict(
            title="Date",
            gridcolor="#1e3a5f",
            showgrid=True,
        ),
        yaxis=dict(
            title="Cost (USD)",
            gridcolor="#1e3a5f",
            showgrid=True,
            tickprefix="$",
            tickformat=",.0f",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# BAR CHART
# ─────────────────────────────────────────────────────────────────────────────

def create_bar_chart(df: pd.DataFrame, top_n: int) -> go.Figure:
    """
    Horizontal bar chart ranking the top-N groups by total cost.

    Args:
        df:    DataFrame[Date, Group, Cost].
        top_n: Number of groups to display.

    Returns:
        A Plotly Figure ready for st.plotly_chart().
    """
    group_totals = (
        df.groupby("Group")["Cost"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    fig = go.Figure(go.Bar(
        x=group_totals["Cost"],
        y=group_totals["Group"],
        orientation="h",
        marker=dict(
            color=group_totals["Cost"],
            colorscale="Plasma",
            showscale=True,
            colorbar=dict(title="USD", tickprefix="$"),
        ),
        hovertemplate="<b>%{y}</b><br>Total Cost: $%{x:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        **_DARK_LAYOUT,
        title=dict(text=f"Top {top_n} Groups by Total Cost", x=0, font=dict(size=16)),
        xaxis=dict(
            title="Total Cost (USD)",
            gridcolor="#1e3a5f",
            tickprefix="$",
            tickformat=",.0f",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            gridcolor="#1e3a5f",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# PIE / DONUT CHART
# ─────────────────────────────────────────────────────────────────────────────

def create_pie_chart(df: pd.DataFrame, top_n: int) -> go.Figure:
    """
    Donut chart showing cost distribution across the top-N groups.
    Groups beyond top-N are collapsed into an "Others" slice.

    Args:
        df:    DataFrame[Date, Group, Cost].
        top_n: Number of individual slices before grouping into "Others".

    Returns:
        A Plotly Figure ready for st.plotly_chart().
    """
    group_totals = (
        df.groupby("Group")["Cost"]
        .sum()
        .sort_values(ascending=False)
    )

    top = group_totals.head(top_n)
    others = group_totals.iloc[top_n:].sum()

    labels = list(top.index)
    values = list(top.values)

    if others > 0:
        labels.append("Others")
        values.append(others)

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(
            colors=px.colors.qualitative.Vivid,
            line=dict(color="#0d1117", width=2),
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Cost: $%{value:,.2f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
        textposition="outside",
        textinfo="label+percent",
    ))

    fig.update_layout(
        **_DARK_LAYOUT,
        title=dict(text="Cost Distribution by Group", x=0, font=dict(size=16)),
        legend=dict(orientation="v", x=1.05),
        showlegend=True,
    )
    return fig
