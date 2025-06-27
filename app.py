import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="مؤشر الخوف السعودي", layout="centered")

st.title("📉 مؤشر الخوف في السوق السعودي (SFI)")

@st.cache_data(ttl=3600)  # تخزين البيانات لمدة ساعة لتجنب طلبات متكررة
def fetch_market_data():
    try:
        # جلب بيانات المؤشر العام (هذا مثال، تحتاج لاستبداله بمصدر بيانات حقيقي)
        tasi_url = "https://api.tadawul.com.sa/v1/markets/TASI"  # مثال - يحتاج لتفعيل API حقيقي
        sectors_url = "https://api.tadawul.com.sa/v1/sectors"  # مثال - يحتاج لتفعيل API حقيقي
        
        # في حالة عدم وجود API حقيقي، سنستخدم بيانات وهمية مع تنبيه للمستخدم
        st.warning("⚠️ يتم استخدام بيانات تجريبية لأغراض العرض. للتطبيق الفعلي، يلزم تفعيل واجهة برمجة التطبيقات (API) من تداول.")
        
        # بيانات وهمية للمؤشر العام
        tasi_data = {
            "change_percent": round(random.uniform(-2.5, 1.5), 2),
            "volume": random.randint(10000000, 30000000),
            "avg_volume": random.randint(15000000, 25000000),
            "declines": random.randint(50, 200),
            "advances": random.randint(20, 150),
            "market_cap": random.uniform(2000000000000, 3000000000000)
        }
        
        # بيانات وهمية للقطاعات
        sectors = [
            "البنوك", "البتروكيماويات", "التأمين", "الاتصالات", 
            "الطاقة", "الأسمنت", "التجزئة", "الخدمات"
        ]
        
        sectors_data = []
        for sector in sectors:
            sectors_data.append({
                "name": sector,
                "change_percent": round(random.uniform(-3.0, 2.0), 2),
                "volume": random.randint(1000000, 5000000),
                "declines": random.randint(5, 30),
                "total_stocks": random.randint(10, 40),
                "volatility": round(random.uniform(0.5, 3.5), 2)
            })
        
        return tasi_data, pd.DataFrame(sectors_data)
    
    except Exception as e:
        st.error(f"فشل في جلب البيانات: {str(e)}")
        return None, None

def calculate_fear_index(data):
    if data is None:
        return 0
    
    down_ratio = data['declines'] / (data['declines'] + data['advances'])
    volume_ratio = data['volume'] / data['avg_volume']
    tasi_drop = abs(min(0, data['change_percent']))
    
    fear_score = (
        down_ratio * 30 +
        (1 - min(volume_ratio, 1)) * 20 +
        tasi_drop * 15 +
        (1 - (data['market_cap'] / 3000000000000)) * 15 +
        (random.uniform(0, 1) * 20)  # عنصر عشوائي لتمثيل التقلب
    )
    
    return min(round(fear_score, 2), 100)

def calculate_sector_fear(sector):
    down_ratio = sector['declines'] / sector['total_stocks']
    change = abs(min(0, sector['change_percent']))
    
    fear_score = (
        down_ratio * 40 +
        change * 30 +
        (sector['volatility'] / 5) * 30
    )
    
    return min(round(fear_score, 2), 100)

# جلب البيانات
tasi_data, sectors_df = fetch_market_data()

if tasi_data is not None and sectors_df is not None:
    # حساب مؤشر الخوف العام
    fear_score = calculate_fear_index(tasi_data)
    
    # تفسير النتيجة
    if fear_score < 25:
        sentiment = "🟢 السوق مطمئن جدًا"
    elif fear_score < 50:
        sentiment = "🟢 السوق مستقر"
    elif fear_score < 75:
        sentiment = "🟠 قلق في السوق"
    else:
        sentiment = "🔴 خوف شديد في السوق"

    # عرض المؤشر العام
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=fear_score,
        title={'text': "مؤشر الخوف السعودي (SFI)", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red"},
            'steps': [
                {'range': [0, 25], 'color': "lightgreen"},
                {'range': [25, 50], 'color': "green"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 100], 'color': "red"},
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"### 🧠 تحليل: {sentiment}")
    
    # تفاصيل المؤشر العام
    with st.expander("تفاصيل المؤشر العام"):
        st.write(f"📅 تاريخ التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.write(f"🔻 عدد الأسهم الهابطة: {tasi_data['declines']} من أصل {tasi_data['declines'] + tasi_data['advances']}")
        st.write(f"📉 نسبة تغير المؤشر: {tasi_data['change_percent']}%")
        st.write(f"💰 حجم التداول: {tasi_data['volume']:,} (المتوسط: {tasi_data['avg_volume']:,})")
        st.write(f"🏦 القيمة السوقية: {tasi_data['market_cap']:,.2f} ريال")
    
    # مؤشرات الخوف للقطاعات
    st.markdown("## 📊 مؤشر الخوف حسب القطاعات")
    
    # حساب مؤشر الخوف لكل قطاع
    sectors_df['Fear Score'] = sectors_df.apply(calculate_sector_fear, axis=1)
    sectors_df['Sentiment'] = pd.cut(sectors_df['Fear Score'],
                                    bins=[0, 25, 50, 75, 100],
                                    labels=["🟢 مطمئن", "🟢 مستقر", "🟠 قلق", "🔴 خوف شديد"])
    
    # عرض جدول القطاعات
    st.dataframe(sectors_df[['name', 'Fear Score', 'Sentiment', 'change_percent', 'volatility']]
                 .sort_values('Fear Score', ascending=False)
                 .rename(columns={
                     'name': 'القطاع',
                     'Fear Score': 'مؤشر الخوف',
                     'Sentiment': 'الحالة',
                     'change_percent': 'التغير %',
                     'volatility': 'التقلب'
                 }), 
                 height=400)
    
    # عرض رسوم بيانية للقطاعات
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure(go.Bar(
            x=sectors_df['Fear Score'],
            y=sectors_df['name'],
            orientation='h',
            marker_color=['red' if x > 75 else 'orange' if x > 50 else 'green' for x in sectors_df['Fear Score']]
        ))
        fig1.update_layout(title="مؤشر الخوف حسب القطاع", xaxis_title="مؤشر الخوف", yaxis_title="القطاع")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = go.Figure(go.Pie(
            labels=sectors_df['name'],
            values=sectors_df['volume'],
            hole=.3
        ))
        fig2.update_layout(title="حجم التداول حسب القطاع")
        st.plotly_chart(fig2, use_container_width=True)
    
    # تحليل القطاع الأكثر خوفاً
    # تحليل القطاع الأكثر خوفاً
    max_fear_sector = sectors_df.loc[sectors_df['Fear Score'].idxmax()]
    st.markdown(f"### 🔍 تحليل القطاع الأكثر خوفاً: {max_fear_sector['name']}")
    st.write(f"- مؤشر الخوف: {max_fear_sector['Fear Score']} ({max_fear_sector['Sentiment']})")
    st.write(f"- نسبة التغير: {max_fear_sector['change_percent']}%")
    st.write(f"- عدد الأسهم الهابطة: {max_fear_sector['declines']} من أصل {max_fear_sector['total_stocks']}")
    st.write(f"- مستوى التقلب: {max_fear_sector['volatility']}")
else:
    st.error("لا يمكن عرض البيانات حالياً. يرجى المحاولة لاحقاً.")

st.markdown("---")
st.markdown("""
**ملاحظة:** هذا تطبيق تجريبي. لتنفيذ تطبيق حقيقي:
1. تحتاج لتفعيل واجهة برمجة التطبيقات (API) من تداول
2. إضافة معايير أكثر دقة لحساب مؤشر الخوف
3. تحسين خوارزميات حساب التقلبات
""")
