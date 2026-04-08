import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Pro Universal Analytics Dashboard", layout="wide", page_icon="📊")

# ---------------- DARK MODE + UI ---------------- #
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown(
        """
        <style>

        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #e2e8f0;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #020617;
            border-right: 1px solid #1e293b;
        }

        /* KPI Cards */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
        }

        /* File uploader */
        section[data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 10px;
        }

        /* Dataframe */
        .stDataFrame {
            background-color: rgba(255,255,255,0.03);
            border-radius: 10px;
        }

        /* Headers */
        h1, h2, h3 {
            color: #f8fafc;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------- HEADER ---------------- #
st.markdown(
    "<h1 style='text-align: center;'>🌍 Pro Universal Business Analytics Dashboard</h1>",
    unsafe_allow_html=True
)
st.caption("Analyze • Visualize • Gain Insights effortlessly")

# ---------------- SERVICES SECTION ---------------- #
st.markdown("## 🚀 What This Dashboard Offers")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📊 **Data Analysis**\n\nAnalyze any dataset with powerful filters.")

with col2:
    st.info("📈 **Visualization**\n\nInteractive charts for better understanding.")

with col3:
    st.info("🧠 **Insights**\n\nAutomatically detect trends and top performers.")

st.markdown("---")

# ---------------- FILE UPLOAD ---------------- #
uploaded_file = st.file_uploader("📂 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:

    # ---------------- READ DATA ---------------- #
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # ---------------- COLUMN DETECTION ---------------- #
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()

    # Convert object → datetime if possible
    for col in object_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='raise')
            datetime_cols.append(col)
        except:
            pass

    object_cols = [col for col in object_cols if col not in datetime_cols]

    # ---------------- SIDEBAR FILTERS ---------------- #
    st.sidebar.header("🔍 Filters")

    filtered_df = df.copy()

    # Numeric filters
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        low, high = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
        filtered_df = filtered_df[(filtered_df[col] >= low) & (filtered_df[col] <= high)]

    # Categorical filters
    for col in object_cols:
        options = df[col].dropna().unique().tolist()
        selected = st.sidebar.multiselect(f"{col}", options, default=options)
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

    # Date filters
    for col in datetime_cols:
        min_date, max_date = df[col].min().date(), df[col].max().date()
        start, end = st.sidebar.date_input(f"{col}", [min_date, max_date])
        filtered_df = filtered_df[
            (filtered_df[col].dt.date >= start) &
            (filtered_df[col].dt.date <= end)
        ]

    # ---------------- KPI ---------------- #
    st.sidebar.header("⚡ KPI Selection")
    selected_numeric = st.sidebar.selectbox("Select KPI Column", numeric_cols) if numeric_cols else None

    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    if not filtered_df.empty and selected_numeric:
        col1.metric("💰 Sum", f"{filtered_df[selected_numeric].sum():,.2f}")
        col2.metric("📈 Avg", f"{filtered_df[selected_numeric].mean():,.2f}")
        col3.metric("🔽 Min", f"{filtered_df[selected_numeric].min():,.2f}")
        col4.metric("🔼 Max", f"{filtered_df[selected_numeric].max():,.2f}")
    else:
        col1.metric("💰 Sum", 0)
        col2.metric("📈 Avg", 0)
        col3.metric("🔽 Min", 0)
        col4.metric("🔼 Max", 0)

    st.markdown("---")

    # ---------------- VISUALIZATION ---------------- #
    st.subheader("📈 Visualizations")

    chart_col = st.selectbox("Select Column for Chart", object_cols + datetime_cols)

    if not filtered_df.empty and selected_numeric:

        bar_data = filtered_df.groupby(chart_col)[selected_numeric].sum().reset_index()

        fig_bar = px.bar(bar_data, x=chart_col, y=selected_numeric, title="Bar Chart")
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(bar_data, names=chart_col, values=selected_numeric, title="Pie Chart")
        fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

        if datetime_cols:
            date_col = st.selectbox("Trend Column", datetime_cols)
            filtered_df['Month'] = filtered_df[date_col].dt.to_period('M').astype(str)

            trend = filtered_df.groupby('Month')[selected_numeric].sum().reset_index()

            fig_line = px.line(trend, x='Month', y=selected_numeric, markers=True, title="Trend Over Time")
            fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("No data available for visualization.")

    st.markdown("---")

    # ---------------- DATA ---------------- #
    st.subheader("📄 Filtered Data")
    st.dataframe(filtered_df)

    csv = io.StringIO()
    filtered_df.to_csv(csv, index=False)

    st.download_button("⬇️ Download CSV", csv.getvalue(), "filtered_data.csv", "text/csv")

    # ---------------- INSIGHTS ---------------- #
    st.subheader("🧠 Insights")

    if not filtered_df.empty and selected_numeric and object_cols:
        for col in object_cols[:2]:
            top = filtered_df.groupby(col)[selected_numeric].sum().idxmax()
            st.success(f"🔥 Top {col}: {top}")
    else:
        st.info("No insights available.")

else:
    st.info("👆 Upload a dataset to begin")
