import streamlit as st
import plotly.express as px
from utils.loader import load_data
from utils.metrics import add_metrics


# CONFIG

st.set_page_config(
    page_title="Supply Chain BI Dashboard",
    layout="wide"
)


# LOAD & PROCESS DATA

@st.cache_data
def get_data():
    df = load_data()
    df = add_metrics(df)
    return df

df = get_data()


# SIDEBAR FILTER

st.sidebar.title("🔍 Filter Data")

product_filter = st.sidebar.multiselect(
    "Product Type",
    df['Product type'].unique(),
    default=df['Product type'].unique()
)

supplier_filter = st.sidebar.multiselect(
    "Supplier Name",
    df['Supplier name'].unique(),
    default=df['Supplier name'].unique()
)

transport_filter = st.sidebar.multiselect(
    "Transportation Mode",
    df['Transportation modes'].unique(),
    default=df['Transportation modes'].unique()
)

df_filtered = df[
    (df['Product type'].isin(product_filter)) &
    (df['Supplier name'].isin(supplier_filter)) &
    (df['Transportation modes'].isin(transport_filter))
]


# NAVIGATION

menu = st.sidebar.radio(
    "Navigation",
    [
        "Executive Summary",
        "Inventory Monitoring",
        "Shipping Performance",
        "Supplier Performance",
        "Transportation Analysis",
        "Insights & Recommendations"
    ]
)


# PAGE 1 - EXECUTIVE SUMMARY

if menu == "Executive Summary":
    st.title("📊 Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total SKU", df_filtered['SKU'].nunique())
    col2.metric("Total Revenue", f"${df_filtered['Revenue generated'].sum():,.0f}")
    col3.metric("Avg Shipping Time", round(df_filtered['Shipping times'].mean(), 2))
    col4.metric("Delay Rate (%)", round(df_filtered['Shipping_Delay_Flag'].mean() * 100, 2))

# PAGE 2 - INVENTORY

elif menu == "Inventory Monitoring":
    st.title("📦 Inventory Monitoring")

    st.dataframe(
        df_filtered[
            ['Product type','SKU','Stock levels','Order quantities','Inventory_Status']
        ]
    )

    fig = px.bar(
        df_filtered,
        x="Product type",
        y="Stock levels",
        color="Inventory_Status",
        title="Stock Levels by Product Type"
    )
    st.plotly_chart(fig, use_container_width=True)


# PAGE 3 - SHIPPING

elif menu == "Shipping Performance":
    st.title("🚚 Shipping Performance")

    fig1 = px.histogram(
        df_filtered,
        x="Shipping times",
        nbins=20,
        title="Distribution of Shipping Times"
    )
    st.plotly_chart(fig1, use_container_width=True)

    carrier_delay = (
        df_filtered.groupby("Shipping carriers")['Shipping_Delay_Flag']
        .mean()
        .reset_index()
    )

    fig2 = px.bar(
        carrier_delay,
        x="Shipping carriers",
        y="Shipping_Delay_Flag",
        title="Delay Rate by Shipping Carrier"
    )
    st.plotly_chart(fig2, use_container_width=True)


# PAGE 4 - SUPPLIER

elif menu == "Supplier Performance":
    st.title("🏭 Supplier Performance")

    supplier_perf = (
        df_filtered.groupby("Supplier name")
        .agg({
            "Lead times":"mean",
            "Manufacturing lead time":"mean",
            "Defect rates":"mean",
            "Revenue generated":"sum"
        })
        .reset_index()
    )

    supplier_perf['Defect Rate (%)'] = supplier_perf['Defect rates'] * 100

    st.dataframe(supplier_perf)


# PAGE 5 - TRANSPORTATION

elif menu == "Transportation Analysis":
    st.title("🚛 Transportation Cost Analysis")

    route_cost = (
        df_filtered.groupby("Routes")['Costs']
        .sum()
        .reset_index()
    )

    fig = px.bar(
        route_cost,
        x="Routes",
        y="Costs",
        title="Total Transportation Cost by Route"
    )
    st.plotly_chart(fig, use_container_width=True)


# PAGE 6 - INSIGHTS & RECOMMENDATIONS

elif menu == "Insights & Recommendations":
    st.title("🧠 Automated Insights & Business Recommendations")

    # Inventory Insight
    low_stock_ratio = (
        (df_filtered['Inventory_Status'] == 'Low Stock').mean() * 100
    )

    st.subheader("📦 Inventory Insight")
    st.write(
        f"Berdasarkan data yang telah difilter, sebesar **{low_stock_ratio:.2f}%** "
        f"produk berada pada kondisi persediaan yang lebih rendah dibandingkan "
        f"jumlah pesanan. Kondisi ini menunjukkan potensi risiko stockout yang "
        f"dapat berdampak pada keterlambatan pemenuhan permintaan pelanggan."
    )

    if low_stock_ratio > 30:
        st.warning(
            "Rekomendasi: Perusahaan disarankan untuk menyesuaikan reorder point "
            "dan meningkatkan akurasi perencanaan persediaan."
        )
    else:
        st.success("Kondisi persediaan relatif stabil dan terkendali.")

    # Shipping Insight
    delay_rate = df_filtered['Shipping_Delay_Flag'].mean() * 100

    st.subheader("🚚 Shipping Insight")
    st.write(
        f"Tingkat keterlambatan pengiriman pada segmen ini mencapai "
        f"**{delay_rate:.2f}%**, yang mengindikasikan perlunya evaluasi "
        f"terhadap efektivitas pengiriman dan ketepatan lead time."
    )

    # Supplier Insight
    worst_supplier = (
        df_filtered.groupby("Supplier name")['Defect rates']
        .mean()
        .idxmax()
    )

    st.subheader("🏭 Supplier Insight")
    st.write(
        f"Supplier dengan tingkat defect tertinggi adalah **{worst_supplier}**, "
        f"yang berpotensi meningkatkan biaya inspeksi dan menurunkan kualitas produk."
    )

    # Transportation Insight
    highest_cost_mode = (
        df_filtered.groupby("Transportation modes")['Costs']
        .mean()
        .idxmax()
    )

    st.subheader("🚛 Transportation Insight")
    st.write(
        f"Moda transportasi dengan biaya rata-rata tertinggi adalah "
        f"**{highest_cost_mode}**. Moda ini sebaiknya digunakan secara selektif "
        f"untuk pengiriman bernilai tinggi atau bersifat prioritas."
    )
