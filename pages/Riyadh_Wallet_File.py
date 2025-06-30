import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 تحليل المحفظة الاستثمارية", layout="wide")
st.title("📈 تقييم المحفظة - السوق السعودي")

uploaded_file = st.file_uploader("📥 قم بتحميل ملف Excel أو CSV يحتوي على المحفظة", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig", thousands=",")
    else:
        df = pd.read_excel(uploaded_file, thousands=",")

    # التأكد من الأعمدة
    required_cols = {
        "الرمز", "الشركة", "المحفظة", "مرهون", "متوسط التكلفة",
        "بيع تحت التسوية", "شراء تحت التسوية", "سعر السوق",
        "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد", "سعر الإغلاق"
    }

    if not required_cols.issubset(set(df.columns)):
        st.error(f"❌ الملف يجب أن يحتوي على الأعمدة التالية:\n{required_cols}")
    else:
        # تحويل الأعمدة الرقمية
        numeric_cols = ["المحفظة", "مرهون", "متوسط التكلفة", "بيع تحت التسوية", "شراء تحت التسوية",
                        "سعر السوق", "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد", "سعر الإغلاق"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # حساب الإجماليات
        total_cost = df["إجمالي التكلفة"].sum()
        total_value = df["القيمة السوقية"].sum()
        total_gain = df["الربح/الخسارة"].sum()
        total_return = (total_gain / total_cost) * 100 if total_cost else 0

        # عرض ملخص المحفظة
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 إجمالي التكلفة", f"{total_cost:,.2f} ريال")
        col2.metric("📈 القيمة السوقية", f"{total_value:,.2f} ريال")
        col3.metric("🚦 العائد الإجمالي", f"{total_gain:,.2f} ريال", f"{total_return:.2f}%")

        # عرض جدول المحفظة
        st.subheader("📋 تفاصيل الأسهم في المحفظة")
        selected_cols = [
            "الرمز", "الشركة", "المحفظة", "متوسط التكلفة", "سعر السوق",
            "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد"
        ]
        st.dataframe(df[selected_cols].round(2), use_container_width=True)

        # توزيع الأسهم
        st.subheader("📊 توزيع المحفظة حسب الأسهم")
        weights = df.set_index("الشركة")["القيمة السوقية"].dropna()
        weights = weights[weights > 0]
        if not weights.empty:
            fig, ax = plt.subplots()
            ax.pie(weights, labels=weights.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا توجد بيانات صالحة للرسم البياني.")

        # الأسهم الرابحة والخاسرة
        st.subheader("🔍 الأسهم الرابحة والخاسرة")
        winners = df[df["الربح/الخسارة"] > 0].sort_values("الربح/الخسارة", ascending=False)
        losers = df[df["الربح/الخسارة"] < 0].sort_values("الربح/الخسارة")

        col1, col2 = st.columns(2)
        with col1:
            st.success("🟢 الأسهم الرابحة")
            st.dataframe(winners[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2))
        with col2:
            st.error("🔴 الأسهم الخاسرة")
            st.dataframe(losers[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2))
else:
    st.info("👈 يرجى رفع ملف يحتوي على بيانات المحفظة.")
