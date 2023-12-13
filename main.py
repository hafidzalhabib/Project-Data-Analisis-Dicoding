import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)
formatter = ScalarFormatter()
formatter.set_scientific(False)

df = pd.read_csv("df.csv")
payment = pd.read_csv("payment.csv")

df.sort_values(by="order_purchase_timestamp", inplace=True)
df.reset_index(inplace=True)
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max() + timedelta(days=1)

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

new_df = df[(df["order_purchase_timestamp"] >= str(start_date)) &
                (df["order_purchase_timestamp"] <= str(end_date))]
# new_df["order_purchase_timestamp"] = pd.to_datetime(new_df["order_purchase_timestamp"])

def daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df


def monthly_orders(df):
    monthly_orders = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique"
    })
    monthly_orders.index = monthly_orders.index.strftime('%B %Y')
    monthly_orders = monthly_orders.reset_index()
    monthly_orders.rename(columns={
        "order_id": "Jumlah Order"
    }, inplace=True)
    return monthly_orders

def monthly_rev(df):
    monthly_rev = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "price": "sum"
    })
    monthly_rev.index = monthly_rev.index.strftime('%B %Y')
    monthly_rev = monthly_rev.reset_index()
    monthly_rev.rename(columns={
        "price": "Penjualan"
    }, inplace=True)
    return monthly_rev

def category_orders(df):
    category_orders = df.groupby(by='product_category_name_english').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    category_orders = category_orders.reset_index()
    category_orders.rename(columns={
        "product_category_name_english": "Category",
        "order_id": "Jumlah Order",
        "price": "Penjualan"
    }, inplace=True)
    return category_orders

def df_value_counts(df):
    value_counts_result = payment['payment_type'].value_counts()
    df_value_counts = pd.DataFrame({'payment_type': value_counts_result.index, 'count': value_counts_result.values})
    df_value_counts['persentase'] = (df_value_counts['count'] / df_value_counts['count'].sum()) * 100
    df_value_counts['persentase'] = df_value_counts['persentase'].map('{:.1f}%'.format)
    return df_value_counts

def pay_(df):
    # for barplot
    pay_ = payment.groupby(by="payment_type").agg({
        "payment_value": "sum"
    }).reset_index().sort_values(by="payment_value", ascending=False)
    return pay_

def rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",  # menghitung jumlah order
        "price": "sum"  # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df


daily_orders_df = daily_orders_df(new_df)
monthly_orders = monthly_orders(new_df)
monthly_rev = monthly_rev(new_df)
category_orders = category_orders(new_df)
df_value_counts = df_value_counts(new_df)
pay_ = pay_(new_df)
rfm_df = rfm_df(new_df)

st.header('E-Commerce Dashboard :sparkles:')
st.caption("""[Sumber Data](%s)"""
            % "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")

st.subheader('Daily Orders')
cols1, cols2 = st.columns(2)
with cols1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
with cols2:
    total_revenue = daily_orders_df.revenue.sum()
    st.metric("Total Revenue", value=total_revenue)
figs, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(figs)

st.subheader('Monthly Orders')
col1, col2 = st.columns(2)
with col1:
    # Berdasarkan jumlah order per bulannya
    fig1 = plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders["order_purchase_timestamp"], monthly_orders["Jumlah Order"], marker='o', linewidth=2,
             color="#72BCD4")
    plt.title("Jumlah Order per Bulan", loc="center", fontsize=20)
    for index, value in enumerate(monthly_orders["Jumlah Order"]):
        plt.text(index, value + 2, value, ha='center', va='bottom', size=8)
    plt.xticks(fontsize=10, rotation=90)
    plt.yticks(fontsize=10)
    st.pyplot(fig1)
with col2:
    # Berdasarkan total penjualan per bulannya
    fig2 = plt.figure(figsize=(10, 5))
    plt.plot(monthly_rev["order_purchase_timestamp"], monthly_rev["Penjualan"], marker='o', linewidth=2,
             color="#72BCD4")
    plt.title("Total Penjualan per Bulan", loc="center", fontsize=20)
    plt.xticks(fontsize=10, rotation=90)
    plt.yticks(fontsize=10)
    plt.gca().yaxis.set_major_formatter(formatter)
    st.pyplot(fig2)

st.subheader("Best & Worst Performing Product")
# Berdasarkan jumlah order per kategorinya
fig3, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
fig3.suptitle("Jumlah Order per Kategori", fontsize=30)
# Visualisasi paling banyak
by_orders_up = category_orders.sort_values(by = "Jumlah Order", ascending = False)[:10].reset_index()
sns.barplot(x = "Jumlah Order", y = "Category", data = by_orders_up, palette = "GnBu", ax=ax1)
ax1.set_title("Berdasarkan jumlah order paling banyak", fontsize = 20)
ax1.set_ylabel(None)
ax1.set_xlabel(None)
ax1.tick_params(axis ='y', labelsize=11)
ax1.tick_params(axis ='x', labelsize=11)
# Visualisasi paling sedikit
by_orders_down = category_orders.sort_values(by = "Jumlah Order")[:10].reset_index()
sns.barplot(x = "Jumlah Order", y = "Category", data = by_orders_down, palette = "GnBu", ax = ax2)
ax2.set_title("Berdasarkan jumlah order paling sedikit", fontsize = 20)
ax2.set_ylabel(None)
ax2.set_xlabel(None)
ax2.invert_xaxis()
ax2.yaxis.set_label_position("right")
ax2.yaxis.tick_right()
ax2.tick_params(axis ='y', labelsize=12)
ax2.tick_params(axis ='x', labelsize=11)
st.pyplot(fig3)
# Berdasarkan total penjualan per kategorinya
fig4, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
fig4.suptitle("Total Penjualan per Kategori", fontsize=30)
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
# Visualisasi paling banyak
by_penjualan_up = category_orders.sort_values(by = "Penjualan", ascending = False)[:10].reset_index()
sns.barplot(x = "Penjualan", y = "Category", data = by_penjualan_up, palette = "GnBu", ax=ax1)
ax1.set_title("Berdasarkan total penjualan paling banyak", fontsize = 20)
ax1.set_ylabel(None)
ax1.set_xlabel(None)
ax1.xaxis.set_major_formatter(formatter)
ax1.tick_params(axis ='y', labelsize=11)
ax1.tick_params(axis ='x', labelsize=11)
# Visualisasi paling sedikit
by_penjualan_down = category_orders.sort_values(by = "Penjualan")[:10].reset_index()
sns.barplot(x = "Penjualan", y = "Category", data = by_penjualan_down, palette = "GnBu", ax = ax2)
ax2.set_title("Berdasarkan total penjualan paling sedikit", fontsize = 20)
ax2.set_ylabel(None)
ax2.set_xlabel(None)
ax2.invert_xaxis()
ax2.yaxis.set_label_position("right")
ax2.yaxis.tick_right()
ax2.xaxis.set_major_formatter(formatter)
ax2.tick_params(axis ='y', labelsize=11)
ax2.tick_params(axis ='x', labelsize=11)
st.pyplot(fig4)

st.subheader('Orders by Payment Type')
fig5, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
fig5.suptitle("Jumlah Order dan Total Pembayaran Berdasarkan Tipe Pembayaran", fontsize=30)
colors = ['red', 'blue', 'green', 'yellow']
ax1.set_title("Berdasarkan Total Pembayaran", fontsize = 20)
patches, texts = ax1.pie(
    x=df_value_counts["count"],
    labels= df_value_counts["persentase"],
    colors=colors,
    startangle=180,
    textprops={'fontsize': 15},
    explode=[0.12, 0.01, 0.01, 0.02]
)
ax1.legend(patches, df_value_counts["payment_type"], loc="best")
ax1.axis('equal')
ax2.set_title("Berdasarkan Jumlah order", fontsize = 20)
sns.barplot(x = "payment_type", y = "payment_value", data = pay_, palette = colors, ax = ax2)
for index, value in enumerate(pay_['payment_value']):
    ax2.text(index, value + 1, value, ha='center', va='bottom', size = 15)
ax2.set_ylabel(None)
ax2.set_xlabel(None)
ax2.yaxis.set_major_formatter(formatter)
ax2.tick_params(axis ='y', labelsize=15)
ax2.tick_params(axis ='x', labelsize=15)
st.pyplot(fig5)

st.subheader('Best Customer Based on RFM Parameters')
co1, co2, co3 = st.columns(3)
with co1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
with co2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with co3:
    avg_frequency = round(rfm_df.monetary.mean(),2)
    st.metric("Average Monetary", value=avg_frequency)

fig6, (ax1) = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
plt.tight_layout()

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(x="recency", y="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax = ax1)
ax1.set_ylabel(None)
ax1.set_xlabel(None)
ax1.set_title("By Recency (days)", loc="center", fontsize=18)
st.pyplot(fig6)

fig7, ax2 = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
sns.barplot(x="frequency", y="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax= ax2)
ax2.set_ylabel(None)
ax2.set_xlabel(None)
ax2.set_title("By Frequency", loc="center", fontsize=18)
st.pyplot(fig7)

fig8, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 5))
sns.barplot(x="monetary", y="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax = ax)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("By Monetary", loc="center", fontsize=18)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig8)
