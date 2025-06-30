# مكتبات التحليل والتقارير
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="📊 تقييم المحفظة السعودية الذكي", layout="wide")
st.title("📊 تقييم محفظة استثمارية في السوق السعودي - نسخة متكاملة")

# رفع الملف
uploaded_file = st.file_uploader("📥 قم بتحميل ملف CSV يحتوي على بيانات المحفظة", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"symbol", "shares", "buy_price"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ الملف يجب أن يحتوي على الأعمدة التالية: {required_cols}")
    else:
        with st.spinner("🔄 يتم الآن تحميل الأسعار والقطاعات..."):

            def fetch_data(symbol):
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    info = ticker.info
                    return {
                        "price": hist["Close"].iloc[-1] if not hist.empty else None,
                        "sector": info.get("sector", "غير معروف")
                    }
                except:
                    return {"price": None, "sector": "غير معروف"}

            results = df["symbol"].apply(fetch_data)
            df["current_price"] = [r["price"] for r in results]
            df["sector"] = [r["sector"] for r in results]

        df["initial_value"] = df["shares"] * df["buy_price"]
        df["current_value"] = df["shares"] * df["current_price"]
        df["pnl"] = df["current_value"] - df["initial_value"]
        df["pnl_percent"] = (df["pnl"] / df["initial_value"]) * 100

        # إجماليات
        total_initial = df["initial_value"].sum()
        total_current = df["current_value"].sum()
        total_pnl = df["pnl"].sum()
        total_pnl_percent = (total_pnl / total_initial) * 100 if total_initial else 0

        st.success("✅ تم حساب المحفظة وتحليلها بنجاح!")

        # جدول التحليل
        st.subheader("📋 تفاصيل المحفظة")
        st.dataframe(df[["symbol", "sector", "shares", "buy_price", "current_price", "pnl", "pnl_percent"]].round(2))

        # تنبيهات ذكية
        st.subheader("🚦 توصيات وتنبيهات ذكية")
        col1, col2 = st.columns(2)

        with col1:
            gainers = df[df["pnl_percent"] >= 10]
            st.success(f"🟢 أسهم رابحة (+10%): {len(gainers)}")
            st.dataframe(gainers[["symbol", "pnl_percent"]].round(2))

        with col2:
            losers = df[df["pnl_percent"] <= -10]
            st.error(f"🔴 أسهم خاسرة (-10%): {len(losers)}")
            st.dataframe(losers[["symbol", "pnl_percent"]].round(2))

        # رسم بياني للقطاعات
        sector_summary = df.groupby("sector")["current_value"].sum()

        st.write("بيانات القطاعات:", sector_summary)  # عرض البيانات
        
        # تنظيف البيانات
        sector_summary = sector_summary.dropna()
        sector_summary = sector_summary[sector_summary > 0]
        
        if sector_summary.empty:
            st.warning("⚠️ لا توجد بيانات صحيحة للرسم البياني.")
        else:
            import matplotlib.pyplot as plt
            plt.close('all')
            fig, ax = plt.subplots()
            ax.pie(sector_summary, labels=sector_summary.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

        # تقرير PDF
        st.subheader("📄 تحميل تقرير PDF")
        from fpdf import FPDF

    def generate_pdf(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('Cairo', '', 'Cairo-Regular.ttf', uni=True)
        pdf.set_font("Cairo", "", 14)
    
        pdf.cell(200, 10, txt="تقرير المحفظة الاستثمارية - السوق السعودي", ln=True, align="C")
        pdf.ln(10)
    
        # ملخص
        pdf.set_font("Cairo", "", 12)
        pdf.cell(200, 10, txt=f"إجمالي الشراء: {total_initial:,.2f} ريال", ln=True)
        pdf.cell(200, 10, txt=f"القيمة الحالية: {total_current:,.2f} ريال", ln=True)
        pdf.cell(200, 10, txt=f"الربح / الخسارة: {total_pnl:,.2f} ريال ({total_pnl_percent:.2f}%)", ln=True)
        pdf.ln(10)
    
        # رؤوس الجدول
        pdf.set_font("Cairo", "B", 11)
        headers = ["السهم", "القطاع", "الكمية", "سعر الشراء", "السعر الحالي", "الربح %"]
        col_widths = [35, 35, 25, 30, 30, 25]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1)
        pdf.ln()
    
        # الصفوف
        pdf.set_font("Cairo", "", 10)
        for _, row in data.iterrows():
            values = [
                row["symbol"],
                row["sector"][:15],
                str(row["shares"]),
                f"{row['buy_price']:.2f}",
                f"{row['current_price']:.2f}",
                f"{row['pnl_percent']:.2f}%"
            ]
            for i, val in enumerate(values):
                pdf.cell(col_widths[i], 10, val, 1)
            pdf.ln()
    
        # حفظ الملف في الذاكرة
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
     

        pdf_buffer = generate_pdf(df)
        st.download_button("📥 تحميل التقرير كـ PDF", data=pdf_buffer.getvalue(), file_name="portfolio_report.pdf", mime="application/pdf")

else:
    st.info("👈 يرجى رفع ملف محفظتك للبدء.")
