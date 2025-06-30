import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 تحليل المحفظة الاستثمارية", layout="wide")
st.title("📈 تقييم محفظتك في السوق السعودي")

# تحميل الملف
uploaded_file = st.file_uploader("📥 قم بتحميل ملف Excel أو CSV يحتوي على بيانات المحفظة", type=["xlsx", "csv"])

if uploaded_file:
    # قراءة الملف حسب الامتداد
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    required_cols = {
        "Code", "Stock", "Holding", "Pledge", "Average cost",
        "Unsettled sell", "Unsettled buy", "Market Price", 
        "Total Cost", "Current Value", "Gain/Loss", "Return", "Closing Price"
    }

    if not required_cols.issubset(df.columns):
        st.error(f"❌ الملف يجب أن يحتوي على الأعمدة التالية: {required_cols}")
    else:
        st.success("✅ تم تحميل الملف بنجاح!")

        # حساب ملخص المحفظة
        total_cost = df["Total Cost"].sum()
        total_value = df["Current Value"].sum()
        total_gain = df["Gain/Loss"].sum()
        total_return = (total_gain / total_cost) * 100 if total_cost else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 إجمالي التكلفة", f"{total_cost:,.2f} ريال")
        col2.metric("📈 القيمة السوقية", f"{total_value:,.2f} ريال")
        col3.metric("🚦 العائد الإجمالي", f"{total_gain:,.2f} ريال", f"{total_return:.2f} %")

        st.subheader("📋 تفاصيل المحفظة")
        display_df = df[[
            "Code", "Stock", "Holding", "Average cost", "Market Price",
            "Total Cost", "Current Value", "Gain/Loss", "Return"
        ]].copy()
        st.dataframe(display_df.round(2), use_container_width=True)

        st.subheader("📊 توزيع المحفظة حسب الأسهم")
        weights = df.set_index("Stock")["Current Value"]
        weights = weights[weights > 0]
        fig, ax = plt.subplots()
        ax.pie(weights, labels=weights.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # تصنيف الأسهم الرابحة والخاسرة
        st.subheader("🔍 الأسهم الرابحة والخاسرة")
        winners = df[df["Gain/Loss"] > 0].sort_values("Gain/Loss", ascending=False)
        losers = df[df["Gain/Loss"] < 0].sort_values("Gain/Loss")

        col1, col2 = st.columns(2)
        with col1:
            st.success("🟢 الأسهم الرابحة")
            st.dataframe(winners[["Code", "Stock", "Gain/Loss", "Return"]].round(2))
        with col2:
            st.error("🔴 الأسهم الخاسرة")
            st.dataframe(losers[["Code", "Stock", "Gain/Loss", "Return"]].round(2))

else:
    st.info("👈 يرجى رفع الملف لبدء التحليل.")
