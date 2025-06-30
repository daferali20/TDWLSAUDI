import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
#import arabic_reshaper
from bidi.algorithm import get_display

# إعداد صفحة Streamlit
st.set_page_config(page_title="📊 تحليل المحفظة الاستثمارية", layout="wide")

# دالة لمعالجة النصوص العربية
def arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# عنوان التطبيق
st.markdown(f"<h1 style='text-align: right;'>{arabic_text('📈 تقييم المحفظة - السوق السعودي')}</h1>", unsafe_allow_html=True)

# تحميل الملف
uploaded_file = st.file_uploader(arabic_text("📥 قم بتحميل ملف Excel أو CSV يحتوي على المحفظة"), type=["xlsx", "csv"])

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
            st.error(arabic_text(f"❌ الملف ينقصه الأعمدة التالية: {', '.join(missing_cols)}"))
        else:
            # تحويل الأعمدة الرقمية
            numeric_cols = ["المحفظة", "مرهون", "متوسط التكلفة", "بيع تحت التسوية", "شراء تحت التسوية",
                          "سعر السوق", "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد", "سعر الإغلاق"]
            
            for col in numeric_cols:
                # معالجة القيم النصية التي تحتوي على فواصل
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
            st.subheader(arabic_text("📊 ملخص المحفظة"))
            col1, col2, col3 = st.columns(3)
            col1.metric(arabic_text("💰 إجمالي التكلفة"), f"{total_cost:,.2f} {arabic_text('ريال')}")
            col2.metric(arabic_text("📈 القيمة السوقية"), f"{total_value:,.2f} {arabic_text('ريال')}")
            col3.metric(arabic_text("🚦 العائد الإجمالي"), 
                        f"{total_gain:,.2f} {arabic_text('ريال')}", 
                        f"{total_return:.2f}%")

            # عرض جدول المحفظة
            st.divider()
            st.subheader(arabic_text("📋 تفاصيل الأسهم في المحفظة"))
            selected_cols = [
                "الرمز", "الشركة", "المحفظة", "متوسط التكلفة", "سعر السوق",
                "إجمالي التكلفة", "القيمة السوقية", "الربح/الخسارة", "العائد"
            ]
            st.dataframe(df[selected_cols].round(2), use_container_width=True)

            # توزيع الأسهم
            st.divider()
            st.subheader(arabic_text("📊 توزيع المحفظة حسب الأسهم"))
            weights = df.set_index("الشركة")["القيمة السوقية"].dropna()
            weights = weights[weights > 0]
            
            if not weights.empty:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(weights, labels=weights.index, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")
                ax.set_title(arabic_text("توزيع القيمة السوقية للأسهم"))
                st.pyplot(fig)
                plt.close()
            else:
                st.warning(arabic_text("⚠️ لا توجد بيانات صالحة للرسم البياني."))

            # الأسهم الرابحة والخاسرة
            st.divider()
            st.subheader(arabic_text("🔍 الأسهم الرابحة والخاسرة"))
            winners = df[df["الربح/الخسارة"] > 0].sort_values("الربح/الخسارة", ascending=False)
            losers = df[df["الربح/الخسارة"] < 0].sort_values("الربح/الخسارة")

            col1, col2 = st.columns(2)
            with col1:
                st.success(arabic_text(f"🟢 الأسهم الرابحة ({len(winners)})"))
                st.dataframe(winners[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2), 
                            use_container_width=True)
            with col2:
                st.error(arabic_text(f"🔴 الأسهم الخاسرة ({len(losers)})"))
                st.dataframe(losers[["الرمز", "الشركة", "الربح/الخسارة", "العائد"]].round(2), 
                            use_container_width=True)

            # تنبيهات ذكية
            st.divider()
            st.subheader(arabic_text("🚦 توصيات وتنبيهات ذكية"))
            col1, col2 = st.columns(2)

            with col1:
                gainers = df[df["العائد"] >= 10]
                st.success(arabic_text(f"🟢 أسهم رابحة (+10% فأكثر): {len(gainers)}"))
                if not gainers.empty:
                    st.dataframe(gainers[["الرمز", "الشركة", "العائد"]].round(2), 
                                use_container_width=True)

            with col2:
                losers = df[df["العائد"] <= -10]
                st.error(arabic_text(f"🔴 أسهم خاسرة (-10% فأقل): {len(losers)}"))
                if not losers.empty:
                    st.dataframe(losers[["الرمز", "الشركة", "العائد"]].round(2), 
                                use_container_width=True)

            # دالة لإنشاء PDF
            def generate_pdf(data):
                pdf = FPDF()
                pdf.add_page()
                
                # إضافة خط عربي
                try:
                    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
                    pdf.set_font("Arial", "", 14)
                except:
                    st.warning(arabic_text("⚠️ تم استخدام خط افتراضي لإنشاء PDF"))
                    pdf.set_font("Arial", "", 14)
                
                # عنوان التقرير
                pdf.cell(0, 10, arabic_text("تقرير المحفظة الاستثمارية - السوق السعودي"), 0, 1, 'C')
                pdf.ln(10)
                
                # ملخص المحفظة
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, arabic_text("ملخص المحفظة"), 0, 1, 'R')
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, arabic_text(f"إجمالي التكلفة: {total_cost:,.2f} ريال"), 0, 1, 'R')
                pdf.cell(0, 10, arabic_text(f"القيمة السوقية: {total_value:,.2f} ريال"), 0, 1, 'R')
                pdf.cell(0, 10, arabic_text(f"الربح / الخسارة: {total_gain:,.2f} ريال ({total_return:.2f}%)"), 0, 1, 'R')
                pdf.ln(10)
                
                # جدول الأسهم
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, arabic_text("تفاصيل الأسهم"), 0, 1, 'R')
                
                # رؤوس الأعمدة
                headers = ["الرمز", "الشركة", "الكمية", "متوسط السعر", "السعر السوقي", "الربح/الخسارة", "العائد"]
                col_widths = [20, 50, 20, 25, 25, 30, 20]
                
                pdf.set_font("Arial", "B", 10)
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, arabic_text(header), 1, 0, 'R')
                pdf.ln()
                
                # بيانات الأسهم
                pdf.set_font("Arial", "", 10)
                for _, row in data.iterrows():
                    pdf.cell(col_widths[0], 10, str(row["الرمز"]), 1, 0, 'R')
                    pdf.cell(col_widths[1], 10, arabic_text(str(row["الشركة"])), 1, 0, 'R')
                    pdf.cell(col_widths[2], 10, str(row["المحفظة"]), 1, 0, 'R')
                    pdf.cell(col_widths[3], 10, f"{row['متوسط التكلفة']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[4], 10, f"{row['سعر السوق']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[5], 10, f"{row['الربح/الخسارة']:,.2f}", 1, 0, 'R')
                    pdf.cell(col_widths[6], 10, f"{row['العائد']:.2f}%", 1, 1, 'R')
                
                return pdf.output(dest='S').encode('latin-1')

            # زر تحميل PDF
            st.divider()
            st.subheader(arabic_text("📄 تحميل تقرير PDF"))
            pdf_bytes = generate_pdf(df)
            st.download_button(
                label=arabic_text("📥 تحميل التقرير كـ PDF"),
                data=pdf_bytes,
                file_name=arabic_text("تقرير_المحفظة.pdf"),
                mime="application/pdf"
            )

    except Exception as e:
        st.error(arabic_text(f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}"))
else:
    st.info(arabic_text("👈 يرجى رفع ملف محفظتك للبدء."))

# تنسيق إضافي للواجهة
st.markdown("""
<style>
    .stTextInput, .stSelectbox, .stTextArea, .stAlert {
        direction: rtl;
        text-align: right;
    }
    .stDataFrame {
        direction: ltr;
    }
</style>
""", unsafe_allow_html=True)
