import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="📊 تقييم المحفظة - السوق السعودي", layout="wide")
st.title("📊 تقييم محفظة استثمارية في السوق السعودي")

# تحميل الملف
uploaded_file = st.file_uploader("📥 قم بتحميل ملف CSV أو Excel يحتوي على بيانات المحفظة", type=["csv", "xlsx"])

if uploaded_file:
    # قراءة الملف
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # التحقق من الأعمدة المطلوبة
    required_cols = {"symbol", "shares", "buy_price"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ الملف يجب أن يحتوي على الأعمدة التالية: {required_cols}")
    else:
        # جلب الأسعار الحالية من Yahoo Finance
        def get_price(symbol):
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                return hist["Close"].iloc[-1]
            except:
                return None

        st.info("⏳ يتم الآن تحميل الأسعار الحالية للأسهم...")
        df["current_price"] = df["symbol"].apply(get_price)
        df["current_value"] = df["shares"] * df["current_price"]
        df["initial_value"] = df["shares"] * df["buy_price"]
        df["pnl"] = df["current_value"] - df["initial_value"]
        df["pnl_percent"] = (df["pnl"] / df["initial_value"]) * 100

        st.success("✅ تم حساب التقييم بنجاح")

        st.subheader("📋 تفاصيل المحفظة")
        st.dataframe(df[["symbol", "shares", "buy_price", "current_price", "pnl", "pnl_percent"]].round(2))

        st.subheader("📈 ملخص المحفظة")
        total_current = df["current_value"].sum()
        total_initial = df["initial_value"].sum()
        total_pnl = df["pnl"].sum()
        total_pnl_percent = (total_pnl / total_initial) * 100 if total_initial > 0 else 0

        st.markdown(f"""
        - 💼 **إجمالي قيمة الشراء:** {total_initial:,.2f} ريال  
        - 📈 **القيمة الحالية للمحفظة:** {total_current:,.2f} ريال  
        - 💰 **الربح / الخسارة:** {total_pnl:,.2f} ريال ({total_pnl_percent:.2f}%)
        """)

else:
    st.warning("📁 يرجى تحميل ملف يحتوي على بيانات المحفظة لتقييمها.")

