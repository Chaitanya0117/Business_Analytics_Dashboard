import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Pro Universal Analytics Dashboard", layout="wide", page_icon="📊")

st.title("🌍 Pro Universal Business Analytics Dashboard")

# ---------------- DARK MODE TOGGLE ---------------- #
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    st.markdown(
        """
        <style>
        .reportview-container {background-color: #0E1117; color: #F0F0F0;}
        .stButton>button {background-color: #1F1F1F;}
        </style>
        """,
        unsafe_allow_html=True
    )

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

    # Convert object to datetime if possible
    for col in object_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='raise')
            datetime_cols.append(col)
        except:
            continue
    object_cols = [col for col in object_cols if col not in datetime_cols]

    # ---------------- SIDEBAR FILTERS ---------------- #
    st.sidebar.header("🔍 Filters")

    # Numeric filters
    numeric_filters = {}
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        numeric_filters[col] = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))

    # Categorical filters
    categorical_filters = {}
    for col in object_cols:
        options = df[col].dropna().unique().tolist()
        categorical_filters[col] = st.sidebar.multiselect(f"Select {col}", options, default=options)

    # Date filters
    date_filters = {}
    for col in datetime_cols:
        min_date, max_date = df[col].min().date(), df[col].max().date()
        date_filters[col] = st.sidebar.date_input(f"{col} range", [min_date, max_date])

    # ---------------- APPLY FILTERS ---------------- #
    filtered_df = df.copy()

    for col, (low, high) in numeric_filters.items():
        filtered_df = filtered_df[(filtered_df[col] >= low) & (filtered_df[col] <= high)]

    for col, selected in categorical_filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

    for col, drange in date_filters.items():
        filtered_df = filtered_df[(filtered_df[col].dt.date >= drange[0]) & (filtered_df[col].dt.date <= drange[1])]

    # ---------------- KPI SELECTION ---------------- #
    st.sidebar.header("⚡ KPI Selection")
    selected_numeric = st.sidebar.multiselect("Select Numeric Column(s) for KPIs", numeric_cols, default=numeric_cols[:1])

    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    if not filtered_df.empty and selected_numeric:
        metric_col = selected_numeric[0]
        col1.metric("💰 Sum", f"{filtered_df[metric_col].sum():,.2f}")
        col2.metric("📈 Average", f"{filtered_df[metric_col].mean():,.2f}")
        col3.metric("🔽 Min", f"{filtered_df[metric_col].min():,.2f}")
        col4.metric("🔼 Max", f"{filtered_df[metric_col].max():,.2f}")
    else:
        col1.metric("💰 Sum", 0)
        col2.metric("📈 Average", 0)
        col3.metric("🔽 Min", 0)
        col4.metric("🔼 Max", 0)

    st.markdown("---")

    # ---------------- INTERACTIVE CHARTS ---------------- #
    st.subheader("📈 Visualizations")
    chart_cat_col = st.selectbox("Categorical/Date Column for Chart", object_cols + datetime_cols)
    if not filtered_df.empty and selected_numeric:
        metric_col = selected_numeric[0]
        # Bar Chart
        bar_data = filtered_df.groupby(chart_cat_col)[metric_col].sum().reset_index()
        fig_bar = px.bar(bar_data, x=chart_cat_col, y=metric_col, color=metric_col,
                         title=f"{metric_col} by {chart_cat_col}", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie Chart
        fig_pie = px.pie(bar_data, names=chart_cat_col, values=metric_col, title=f"{metric_col} Distribution by {chart_cat_col}")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Trend Line (if date exists)
        if datetime_cols:
            date_col_chart = st.selectbox("Date Column for Trend", datetime_cols)
            filtered_df['Month'] = filtered_df[date_col_chart].dt.to_period('M').astype(str)
            trend_data = filtered_df.groupby('Month')[metric_col].sum().reset_index()
            fig_line = px.line(trend_data, x='Month', y=metric_col, markers=True, title=f"{metric_col} Trend Over Time")
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data to display in charts for selected filters or numeric column.")

    st.markdown("---")

    # ---------------- FILTERED DATA & DOWNLOAD ---------------- #
    st.subheader("📄 Filtered Data")
    st.dataframe(filtered_df)

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button("⬇️ Download Filtered Data as CSV", csv_buffer.getvalue(), "filtered_data.csv", "text/csv")

    # ---------------- AUTOMATED INSIGHTS ---------------- #
    st.subheader("🧠 Insights")
    if not filtered_df.empty and selected_numeric:
        metric_col = selected_numeric[0]
        for col in object_cols[:2]:  # top 2 categorical insights
            if metric_col in filtered_df.columns:
                top_value = filtered_df.groupby(col)[metric_col].sum().idxmax()
                top_val_sum = filtered_df.groupby(col)[metric_col].sum().max()
                pct = (top_val_sum / filtered_df[metric_col].sum()) * 100
                st.success(f"🔥 Top {col}: {top_value} ({pct:.1f}% of total {metric_col})")
    else:
        st.info("No insights available: please select a numeric column for analysis.")

else:
    st.info("👆 Upload a dataset to begin")