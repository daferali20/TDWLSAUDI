import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64

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

    # تنبيهات ذكية
        st.subheader("🚦 توصيات وتنبيهات ذكية")
        col1, col2 = st.columns(2)

        with col1:
            gainers = df[df["العائد"] >= 10]
            st.success(f"🟢 أسهم رابحة (+10%): {len(gainers)}")
            st.dataframe(gainers[["الرمز", "المحفظة"]].round(2))

        with col2:
            losers = df[df["العائد"] <= -10]
            st.error(f"🔴 أسهم خاسرة (-10%): {len(losers)}")
            st.dataframe(losers[["الرمز", "المحفظة"]].round(2))

        # رسم بياني للقطاعات
        #st.subheader("📊 توزيع المحفظة حسب القطاعات")
        #sector_summary = df.groupby("sector")["current_value"].sum()
        #fig, ax = plt.subplots()
        #ax.pie(sector_summary, labels=sector_summary.index, autopct="%1.1f%%", startangle=90)
        #ax.axis("equal")
        #st.pyplot(fig)
        
        sector_summary = df.groupby("الشركة")["القيمة السوقية"].sum()

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
