import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64

# إعداد صفحة Streamlit
st.set_page_config(page_title="📊 تحليل المحفظة الاستثمارية", layout="wide")
st.title("📈 تقييم المحفظة - السوق السعودي")

uploaded_file = st.file_uploader("📥 قم بتحميل ملف Excel أو CSV يحتوي على المحفظة", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # قراءة الملف
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig", thousands=",")
        else:
            df = pd.read_excel(uploaded_file, thousands=",")

        # التأكد من الأعمدة المطلوبة
        required_cols = {
            "الرمز", "الشركة", "المحفظة", "مرهون", "متوسط التكلفة",
            "بيع تحت التسوية", "شراء تحت التسوية", "سعر السوق",
            "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد", "سعر الإغلاق"
        }

        if not required_cols.issubset(set(df.columns)):
            missing_cols = required_cols - set(df.columns)
            st.error(f"❌ الملف ينقصه الأعمدة التالية: {', '.join(missing_cols)}")
        else:
            # تحويل الأعمدة الرقمية
            numeric_cols = ["المحفظة", "مرهون", "متوسط التكلفة", "بيع تحت التسوية", "شراء تحت التسوية",
                          "سعر السوق", "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد", "سعر الإغلاق"]
            
            for col in numeric_cols:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # حساب الإجماليات
            total_cost = df["إجمالي التكلفة"].sum()
            total_value = df["القيمة السوقية"].sum()
            total_gain = df["الربح/الخسارة"].sum()
            total_return = (total_gain / total_cost) * 100 if total_cost else 0

            # عرض ملخص المحفظة
            st.divider()
            st.subheader("📊 ملخص المحفظة")
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 إجمالي التكلفة", f"{total_cost:,.2f} ريال")
            col2.metric("📈 القيمة السوقية", f"{total_value:,.2f} ريال")
            col3.metric("🚦 العائد الإجمالي", f"{total_gain:,.2f} ريال", f"{total_return:.2f}%")

            # عرض جدول المحفظة
            st.divider()
            st.subheader("📋 تفاصيل الأسهم في المحفظة")
            selected_cols = [
                "الرمز", "الشركة", "المحفظة", "متوسط التكلفة", "سعر السوق",
                "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد"
            ]
            st.dataframe(df[selected_cols].round(2), use_container_width=True)

            # توزيع الأسهم
            st.divider()
            st.subheader("📊 توزيع المحفظة حسب الأسهم")
            weights = df.set_index("الشركة")["القيمة السوقية"].dropna()
            weights = weights[weights > 0]
            
            if not weights.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(weights, labels=weights.index, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
                plt.close()
            else:
                st.warning("⚠️ لا توجد بيانات صالحة للرسم البياني.")

            # الأسهم الرابحة والخاسرة
            st.divider()
            st.subheader("🔍 الأسهم الرابحة والخاسرة")
            winners = df[df["الربح/الخسارة"] > 0].sort_values("الربح/الخسارة", ascending=False)
            losers = df[df["الربح/الخسارة"] < 0].sort_values("الربح/الخسارة")

            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🟢 الأسهم الرابحة ({len(winners)})")
                st.dataframe(winners[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2), 
                            use_container_width=True)
            with col2:
                st.error(f"🔴 الأسهم الخاسرة ({len(losers)})")
                st.dataframe(losers[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2), 
                            use_container_width=True)

            # تنبيهات ذكية
            st.divider()
            st.subheader("🚦 توصيات وتنبيهات ذكية")
            col1, col2 = st.columns(2)

            with col1:
                gainers = df[df["العائد"] >= 10]
                st.success(f"🟢 أسهم رابحة (+10% فأكثر): {len(gainers)}")
                if not gainers.empty:
                    st.dataframe(gainers[["الرمز", "الشركة", "العائد"]].round(2), 
                                use_container_width=True)

            with col2:
                losers = df[df["العائد"] <= -10]
                st.error(f"🔴 أسهم خاسرة (-10% فأقل): {len(losers)}")
                if not losers.empty:
                    st.dataframe(losers[["الرمز", "الشركة", "العائد"]].round(2), 
                                use_container_width=True)

            # دالة لإنشاء PDF
            def generate_pdf(data):
                pdf = FPDF()
                pdf.add_page()
                
                # إعداد الخط
                try:
                    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
                    pdf.set_font("Arial", "", 14)
                except:
                    pdf.set_font("Arial", "", 14)
                
                # عنوان التقرير
                pdf.cell(0, 10, "تقرير المحفظة الاستثمارية - السوق السعودي", 0, 1, 'C')
                pdf.ln(10)
                
                # ملخص المحفظة
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "ملخص المحفظة", 0, 1, 'R')
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"إجمالي التكلفة: {total_cost:,.2f} ريال", 0, 1, 'R')
                pdf.cell(0, 10, f"القيمة السوقية: {total_value:,.2f} ريال", 0, 1, 'R')
                pdf.cell(0, 10, f"الربح / الخسارة: {total_gain:,.2f} ريال ({total_return:.2f}%)", 0, 1, 'R')
                pdf.ln(10)
                
                # جدول الأسهم
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "تفاصيل الأسهم", 0, 1, 'R')
                
                # رؤوس الأعمدة
                headers = ["الرمز", "الشركة", "الكمية", "متوسط السعر", "السعر السوقي", "الربح/الخسارة", "العائد"]
                col_widths = [20, 50, 20, 25, 25, 30, 20]
                
                pdf.set_font("Arial", "B", 10)
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, 1, 0, 'R')
                pdf.ln()
                
                # بيانات الأسهم
                pdf.set_font("Arial", "", 10)
                for _, row in data.iterrows():
                    pdf.cell(col_widths[0], 10, str(row["الرمز"]), 1, 0, 'R')
                    pdf.cell(col_widths[1], 10, str(row["الشركة"]), 1, 0, 'R')
                    pdf.cell(col_widths[2], 10, str(row["المحفظة"]), 1, 0, 'R')
                    pdf.cell(col_widths[3], 10, f"{row['متوسط التكلفة']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[4], 10, f"{row['سعر السوق']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[5], 10, f"{row['الربح/الخسارة']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[6], 10, f"{row['العائد']:.2f}%", 1, 1, 'R')
                
                return pdf.output(dest='S').encode('latin-1')

            # زر تحميل PDF
            st.divider()
            st.subheader("📄 تحميل تقرير PDF")
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
