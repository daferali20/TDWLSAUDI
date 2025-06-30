import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64

# إعداد صفحة Streamlit
st.set_page_config(page_title="📊 تحليل المحفظة الاستثمارية", layout="wide")
st.title("📈 تقييم المحفظة - السوق السعودي")

# تحميل الملف
uploaded_file = st.file_uploader("📥 قم بتحميل ملف Excel أو CSV يحتوي على المحفظة", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # قراءة الملف
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig", thousands=",")
        else:
            df = pd.read_excel(uploaded_file, thousands=",")

        # ... [الكود السابق حتى جزء إنشاء PDF] ...

            def generate_pdf(data):
                pdf = FPDF()
                pdf.add_page()
                
                # حل مشكلة الخط العربي - استخدام خط Arial بدلاً من Cairo إذا لم يتوفر
                try:
                    pdf.add_font('Cairo', '', 'Cairo-Regular.ttf', uni=True)
                    pdf.set_font("Cairo", "", 14)
                except:
                    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
                    pdf.set_font("Arial", "", 14)
                    st.warning("⚠️ تم استخدام خط Arial بدلاً من Cairo لإنشاء PDF")
                
                # عنوان التقرير
                pdf.cell(0, 10, txt="تقرير المحفظة الاستثمارية - السوق السعودي", ln=True, align="C")
                pdf.ln(10)
                
                # ملخص المحفظة
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, txt="ملخص المحفظة", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, txt=f"إجمالي التكلفة: {total_cost:,.2f} ريال", ln=True)
                pdf.cell(0, 10, txt=f"القيمة السوقية: {total_value:,.2f} ريال", ln=True)
                pdf.cell(0, 10, txt=f"الربح / الخسارة: {total_gain:,.2f} ريال ({total_return:.2f}%)", ln=True)
                pdf.ln(10)
                
                # جدول الأسهم
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, txt="تفاصيل الأسهم", ln=True)
                
                # رؤوس الأعمدة
                headers = ["الرمز", "الشركة", "الكمية", "متوسط السعر", "السعر السوقي", "الربح/الخسارة", "العائد"]
                col_widths = [20, 50, 20, 25, 25, 30, 20]
                
                pdf.set_font("Arial", "B", 10)
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, 1)
                pdf.ln()
                
                # بيانات الأسهم
                pdf.set_font("Arial", "", 10)
                for _, row in data.iterrows():
                    pdf.cell(col_widths[0], 10, str(row["الرمز"]), 1)
                    pdf.cell(col_widths[1], 10, str(row["الشركة"]), 1)
                    pdf.cell(col_widths[2], 10, str(row["المحفظة"]), 1)
                    pdf.cell(col_widths[3], 10, f"{row['متوسط التكلفة']:,.2f}", 1)
                    pdf.cell(col_widths[4], 10, f"{row['سعر السوق']:,.2f}", 1)
                    pdf.cell(col_widths[5], 10, f"{row['الربح/الخسارة']:,.2f}", 1)
                    pdf.cell(col_widths[6], 10, f"{row['العائد']:.2f}%", 1)
                    pdf.ln()
                
                return pdf.output(dest='S').encode('latin-1')

            # زر تحميل PDF
            pdf_bytes = generate_pdf(df)
            st.download_button(
                label="📥 تحميل التقرير كـ PDF",
                data=pdf_bytes,
                file_name="تقرير_المحفظة.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}")
else:
    st.info("👈 يرجى رفع ملف محفظتك للبدء.")
