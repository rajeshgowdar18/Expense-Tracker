# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model import load_model, predict_category
import io

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Expense Categorizer",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Expense Categorizer")
st.caption("Upload your bank statement CSV and get instant category breakdown")

# ── Load model ───────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_model()

model = get_model()

# ── Category colors ──────────────────────────────────────────
COLORS = {
    "Food":          "#EF9F27",
    "Transport":     "#378ADD",
    "Shopping":      "#D4537E",
    "Bills":         "#1D9E75",
    "Entertainment": "#7F77DD",
    "Health":        "#D85A30",
    "Others":        "#888780",
}

# ── Sidebar: manual entry ─────────────────────────────────────
with st.sidebar:
    st.header("Quick test")
    test_desc = st.text_input("Transaction description", placeholder="e.g. swiggy order")
    if test_desc:
        cat = predict_category(model, test_desc)
        color = COLORS.get(cat, "#888")
        st.markdown(
            f"<div style='background:{color}22;border-left:4px solid {color};"
            f"padding:10px 14px;border-radius:6px;margin-top:8px'>"
            f"<b style='color:{color}'>{cat}</b></div>",
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown("**Expected CSV columns**")
    st.code("Date, Description, Amount")
    st.caption("Amount should be a number (negative = debit)")

# ── Main: CSV upload ──────────────────────────────────────────
uploaded = st.file_uploader("Upload bank statement CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    # Flexible column detection
    desc_col   = next((c for c in df.columns if "desc" in c.lower() or "narr" in c.lower() or "detail" in c.lower()), df.columns[1])
    amount_col = next((c for c in df.columns if "amount" in c.lower() or "debit" in c.lower()), df.columns[2])

    df["Category"] = df[desc_col].astype(str).apply(
        lambda x: predict_category(model, x)
    )
    df["Amount"] = pd.to_numeric(df[amount_col], errors="coerce").abs()

    st.success(f"Categorized {len(df)} transactions")

    # ── Metrics row ───────────────────────────────────────────
    total    = df["Amount"].sum()
    top_cat  = df.groupby("Category")["Amount"].sum().idxmax()
    num_cats = df["Category"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total spend",       f"₹{total:,.0f}")
    c2.metric("Top category",      top_cat)
    c3.metric("Categories found",  num_cats)

    st.divider()

    # ── Charts row ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Spend by category")
        cat_totals = df.groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(
            cat_totals,
            names="Category",
            values="Amount",
            color="Category",
            color_discrete_map=COLORS,
            hole=0.4,
        )
        fig_pie.update_traces(textposition="outside", textinfo="label+percent")
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Amount per category")
        fig_bar = px.bar(
            cat_totals.sort_values("Amount", ascending=True),
            x="Amount",
            y="Category",
            orientation="h",
            color="Category",
            color_discrete_map=COLORS,
            text_auto=".0f",
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Transactions table ────────────────────────────────────
    st.subheader("All transactions")

    # Category filter
    selected_cats = st.multiselect(
        "Filter by category",
        options=df["Category"].unique().tolist(),
        default=df["Category"].unique().tolist(),
    )
    filtered = df[df["Category"].isin(selected_cats)]

    # Color-code category column
    def highlight_cat(val):
        color = COLORS.get(val, "#888")
        return f"background-color:{color}22; color:{color}; font-weight:500"

    st.dataframe(
        filtered.style.map(highlight_cat, subset=["Category"]),
        use_container_width=True,
        height=360,
    )

    # ── Download ──────────────────────────────────────────────
    csv_out = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download categorized CSV",
        data=csv_out,
        file_name="categorized_expenses.csv",
        mime="text/csv",
    )

else:
    # Demo mode — show sample data
    st.info("No file uploaded yet. Here's a preview with sample data:")

    sample = pd.DataFrame({
        "Date":        ["2024-01-01","2024-01-02","2024-01-03","2024-01-04","2024-01-05"],
        "Description": ["Swiggy order","Uber ride","Netflix subscription","Apollo pharmacy","Electricity bill"],
        "Amount":      [350, 180, 649, 420, 1200],
        "Category":    ["Food","Transport","Entertainment","Health","Bills"],
    })
    st.dataframe(sample, use_container_width=True)