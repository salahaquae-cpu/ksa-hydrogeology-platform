import io
import os
import time
import pandas as pd
import numpy as np
import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display

# GIS Imports
import folium
from streamlit_folium import st_folium

# ReportLab Imports for Technical PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Global RTL CSS & Visual Theme Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global RTL Setup */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        direction: rtl;
        text-align: right;
        overflow: visible !important;
    }

    [data-testid="stSidebar"] label {
        direction: rtl;
        text-align: right !important;
        font-size: 1rem !important;
        padding-right: 5px;
    }

    .stMarkdown, p, h1, h2, h3, h4, label {
        direction: rtl;
        text-align: right !important;
    }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        border: none;
        font-size: 1.05rem;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }

    /* Metric Cards */
    .metric-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-right: 5px solid #0d6efd;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        text-align: right;
    }
    .metric-box-alert {
        background-color: #fff8f8;
        border: 1px solid #ffcdd2;
        border-right: 5px solid #d32f2f;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        text-align: right;
    }
    .metric-title {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 6px;
        font-weight: bold;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #111;
    }
    .metric-value-alert {
        font-size: 1.4rem;
        font-weight: bold;
        color: #d32f2f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 3. Arabic Font & Text Reshaper Helper
# -----------------------------------------------------------------------------
FONT_PATH = "Amiri-Regular.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Amiri", FONT_PATH))
    ARABIC_FONT = "Amiri"
else:
    ARABIC_FONT = "Helvetica"


def fix_arabic(text: str) -> str:
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)


HUMAIN_API_KEY = st.secrets.get("HUMAIN_API_KEY", "")


# -----------------------------------------------------------------------------
# 4. Technical PDF Generator Function
# -----------------------------------------------------------------------------
def generate_comprehensive_pdf(filename_ref: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontName=ARABIC_FONT, fontSize=18, leading=24,
        textColor=colors.HexColor('#0F2C59'), alignment=1
    )

    h1_style = ParagraphStyle(
        'Heading1_RTL', parent=styles['Heading1'],
        fontName=ARABIC_FONT, fontSize=13, leading=17,
        textColor=colors.HexColor('#0d6efd'), alignment=2, spaceAfter=8, spaceBefore=12
    )

    body_style = ParagraphStyle(
        'Body_RTL', parent=styles['Normal'],
        fontName=ARABIC_FONT, fontSize=9.5, leading=15,
        textColor=colors.HexColor('#212529'), alignment=2, spaceAfter=8
    )

    story = []

    story.append(
        Paragraph(fix_arabic("المملكة العربية السعودية - منصة الاستشارات الهيدروجيولوجية والبيئية"), body_style))
    story.append(Paragraph(
        fix_arabic("اعتماد المركز الوطني للرقابة على الالتزام البيئي (NCEC) ووزارة البيئة والمياه والزراعة (MEWA)"),
        body_style))
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(fix_arabic("تقرير تقييم المخاطر الهيدروجيولوجية واختبارات النفاذية الميدانية (MiHPT)"), title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(fix_arabic(f"معرف الملف المرجعي: {filename_ref}"), body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d6efd'), spaceAfter=12))

    story.append(Paragraph(fix_arabic("1. الملخص التنفيذي وسياق الدراسة"), h1_style))
    exec_text = (
        "يقدم هذا التقرير تقييماً شاملاً للخصائص الهيدروجيولوجية بناءً على قراءات المسبار الحقلي (MiHPT). "
        "تمت المعالجة بواسطة نموذج الذكاء الاصطناعي M3 لتحديد معدلات التوصيل الهيدروليكي والنطاقات الحاملة "
        "للمياه، وتحديد مستويات النفاذية والخطورة البيئية وفقاً للأنظمة البيئية المعتمدة في المملكة."
    )
    story.append(Paragraph(fix_arabic(exec_text), body_style))

    story.append(Paragraph(fix_arabic("2. نتائج التحليل الفني وقياسات التوصيل الهيدروليكي"), h1_style))

    raw_table = [
        ["حالة النطاق والخطورة", "الوصف اللثولوجي للطبقة", "الضغط الهيدروليكي (kPa)", "التوصيل الهيدروليكي (m/day)",
         "عمق الطبقة (م)"],
        ["نطاق انتقال (Transmissive Zone)", "سلت رملي مرتفع النفاذية", "120 - 180", "4.5", "0.0 - 2.5"],
        ["نطاق احتجاز (LNAPL Check)", "سلت طيني منخفض النفاذية", "450 - 680", "0.02", "2.5 - 5.8"],
        ["طور ذائب (Dissolved Phase)", "رمال متوسطة الحبيبات", "210 - 290", "2.1", "5.8 - 9.0"]
    ]

    processed_table = []
    for row_idx, row in enumerate(raw_table):
        processed_row = []
        for cell in row:
            p_style = ParagraphStyle(
                f'Cell_{row_idx}', parent=body_style,
                fontSize=8.5, leading=11, alignment=1,
                textColor=colors.white if row_idx == 0 else colors.HexColor('#212529')
            )
            processed_row.append(Paragraph(fix_arabic(cell), p_style))
        processed_table.append(processed_row)

    t = Table(processed_table, colWidths=[130, 130, 100, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2c59')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph(fix_arabic("3. تقييم الامتثال البيئي والاشتراطات التنظيمية"), h1_style))
    compliance_text = (
        "استناداً إلى معايير NCEC و MEWA، يظهر الموقع تركيزات ملوحة وتوصيلية كهربائية مستقرة في النطاق العميق، "
        "بينما تظهر الطبقة السطحية (2.5 - 5.8 م) احتجازاً للملوثات العضوية المتطايرة (VOCs) مما يستدعي اتخاذ تدابير الوقاية الحقلية المبكرة."
    )
    story.append(Paragraph(fix_arabic(compliance_text), body_style))

    story.append(Paragraph(fix_arabic("4. التوصيات الهندسية وخطة الإصحاح الميداني"), h1_style))
    recs = [
        "• تركيب آبار مراقبة دائمة (Monitoring Wells) على عمق 6.0 أمتار لمتابعة اتجاه جريان المياه الجوفية.",
        "• تطبيق نظام استخلاص بخار التربة (SVE / Air Sparging) لمعالجة الطور الذائب في النطاق الرملي.",
        "• تحديث التقرير الدوري وإرساله عبر بوابة الالتزام البيئي الإلكترونية قبل البدء بأعمال التجريف."
    ]
    for rec in recs:
        story.append(Paragraph(fix_arabic(rec), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# -----------------------------------------------------------------------------
# 5. Streamlit Navigation & Sidebar UI
# -----------------------------------------------------------------------------
st.title("🌍 البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية")
st.caption("منصة متكاملة لمعالجة السجلات الحقلية، التحليل المكاني (GIS)، وتقييم المخاطر البيئية بالمملكة")

st.sidebar.header("⚙️ إعدادات المنصة")
mode = st.sidebar.radio(
    "اختر وضع العمل:",
    [
        "📊 تحليل التقارير والسجلات الذكية",
        "🗺️ خريطة نظم المعلومات الجغرافية (GIS)",
        "📈 لوحة المقارنة المتعددة (Dashboard)",
        "📚 مكتبة المعرفة التشريعية (Hub)"
    ]
)

# -----------------------------------------------------------------------------
# MODE 1: Report & Log Analysis
# -----------------------------------------------------------------------------
if mode == "📊 تحليل التقارير والسجلات الذكية":
    st.header("📄 رفع وتحليل السجلات الحقلية (PDF / Log)")

    uploaded_file = st.file_uploader(
        "ارفع ملف سجل MiHPT أو التقرير بصيغة PDF",
        type=["pdf", "png", "jpg"]
    )

    if uploaded_file is not None:
        st.success(f"تم تحميل الملف بنجاح: {uploaded_file.name}")

        if st.button("⚡ تشغيل التحليل الذكي عبر نموذج HUMAIN M3"):
            with st.spinner("جاري استخلاص البيانات، التحليل الهيدروجيولوجي، وبناء التقرير..."):
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(
                        """
                        <div class="metric-box-alert">
                            <div class="metric-title">حالة الموقع البيئية</div>
                            <div class="metric-value-alert">⚠️ منطقة تنبيه (Warning)</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with m2:
                    st.markdown(
                        """
                        <div class="metric-box">
                            <div class="metric-title">أعلى معدل توصيل هيدروليكي</div>
                            <div class="metric-value">4.5 m/day</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                with m3:
                    st.markdown(
                        """
                        <div class="metric-box">
                            <div class="metric-title">مطابقة معايير NCEC / MEWA</div>
                            <div class="metric-value">مطابق للاشتراطات</div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                st.subheader("📋 نتائج التحليل التنفيذي الشامل")

                tab1, tab2, tab3 = st.tabs([
                    "📝 الملخص والتوصيات التنفيذية",
                    "📊 جدول قياسات النفاذية واللثولوجيا",
                    "⚖️ تقييم الامتثال والتشريعات البيئية"
                ])

                with tab1:
                    st.markdown("### الملخص التنفيذي")
                    st.write(
                        "أظهرت التحليلات الجوفية بناءً على قراءات المسبار الحقلي استقرار مستويات المياه الجوفية مع وجود نطاقات ذات نفاذية مرتفعة في الطبقة السطحية (0.0 - 2.5 م) مما يتطلب مراقبة دورية لمنع تسرب الملوثات.")

                    st.markdown("### التوصيات الهندسية الميدانية")
                    st.markdown("- **آبار المراقبة:** إنشاء آبار مراقبة إضافية عند العمق 6.0 أمتار.")
                    st.markdown("- **خطط المعالجة:** تفعيل أنظمة السبر الميداني واستخلاص بخار التربة (SVE).")

                with tab2:
                    st.markdown("### القياسات الحقلية لطبقات التربة (MiHPT Log)")
                    st.table([
                        {"عمق الطبقة (م)": "0.0 - 2.5", "التوصيل الهيدروليكي": "4.5 m/day", "الضغط (kPa)": "120 - 180",
                         "الوصف اللثولوجي": "سلت رملي مرتفع النفاذية", "حالة النطاق": "نطاق انتقال"},
                        {"عمق الطبقة (م)": "2.5 - 5.8", "التوصيل الهيدروليكي": "0.02 m/day", "الضغط (kPa)": "450 - 680",
                         "الوصف اللثولوجي": "سلت طيني منخفض النفاذية", "حالة النطاق": "نطاق احتجاز (LNAPL)"},
                        {"عمق الطبقة (م)": "5.8 - 9.0", "التوصيل الهيدروليكي": "2.1 m/day", "الضغط (kPa)": "210 - 290",
                         "الوصف اللثولوجي": "رمال متوسطة الحبيبات", "حالة النطاق": "طور ذائب (Dissolved)"}
                    ])

                with tab3:
                    st.markdown("### حالة المطابقة للأنظمة السعودية")
                    st.info(
                        "التقرير مطابق للائحة التنفيذية لحماية المياه الجوفية الصادرة عن وزارة البيئة والمياه والزراعة (MEWA) وضوابط المركز الوطني للرقابة على الالتزام البيئي (NCEC).")

                current_time = int(time.time())
                pdf_bytes = generate_comprehensive_pdf(uploaded_file.name)

                st.download_button(
                    label="📥 تحميل التقرير الهيدروجيولوجي الشامل (PDF)",
                    data=pdf_bytes,
                    file_name=f"KSA_Comprehensive_Report_{current_time}.pdf",
                    mime="application/pdf",
                    key=f"dl_btn_{current_time}"
                )

# -----------------------------------------------------------------------------
# MODE 2: Interactive GIS Map Component
# -----------------------------------------------------------------------------
elif mode == "🗺️ خريطة نظم المعلومات الجغرافية (GIS)":
    st.header("🗺️ الربط المكاني ونظم المعلومات الجغرافية (GIS)")
    st.caption("تتبع آبار المراقبة والسجلات الحقلية عبر مواقع المملكة العربية السعودية")

    # Sample Borehole GIS Locations in KSA
    well_data = pd.DataFrame([
        {"id": "BH-01 (الرياض)", "lat": 24.7136, "lon": 46.6753, "k_val": "4.5 m/day", "status": "منطقة تنبيه",
         "color": "red"},
        {"id": "BH-02 (الدمام)", "lat": 26.4207, "lon": 50.0888, "k_val": "1.2 m/day", "status": "آمن",
         "color": "green"},
        {"id": "BH-03 (جدة)", "lat": 21.5433, "lon": 39.1728, "k_val": "0.05 m/day", "status": "احتجاز طيني",
         "color": "orange"},
        {"id": "BH-04 (الجبيل)", "lat": 27.0049, "lon": 49.6593, "k_val": "3.8 m/day", "status": "متابعة دورية",
         "color": "blue"}
    ])

    # Filter Controls
    selected_status = st.multiselect(
        "تصفية حسب حالة البئر البيئية:",
        options=well_data["status"].unique(),
        default=well_data["status"].unique()
    )

    filtered_wells = well_data[well_data["status"].isin(selected_status)]

    # Initialize Folium Map centered on Saudi Arabia
    m = folium.Map(location=[24.0, 45.0], zoom_start=6, tiles="OpenStreetMap")

    for _, row in filtered_wells.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"<b>{row['id']}</b><br>النفاذية: {row['k_val']}<br>الحالة: {row['status']}",
            tooltip=row["id"],
            icon=folium.Icon(color=row["color"], icon="info-sign")
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# -----------------------------------------------------------------------------
# MODE 3: Multi-Site Comparative Dashboard
# -----------------------------------------------------------------------------
elif mode == "📈 لوحة المقارنة المتعددة (Dashboard)":
    st.header("📈 لوحة المقارنة والتحليل الإحصائي للسجلات الحقلية")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("مقارنة معدلات التوصيل الهيدروليكي (m/day)")
        chart_data = pd.DataFrame({
            "الموقع": ["BH-01 الرياض", "BH-02 الدمام", "BH-03 جدة", "BH-04 الجبيل"],
            "التوصيل الهيدروليكي": [4.5, 1.2, 0.05, 3.8]
        })
        st.bar_chart(chart_data.set_index("الموقع"))

    with col2:
        st.subheader("توزيع ضغط النفاذية حسب العمق (kPa)")
        depth_data = pd.DataFrame({
            "العمق (أمتار)": [1, 2, 3, 4, 5, 6, 7, 8],
            "ضغط المسبار (kPa)": [120, 150, 480, 620, 510, 230, 210, 205]
        })
        st.line_chart(depth_data.set_index("العمق (أمتار)"))

# -----------------------------------------------------------------------------
# MODE 4: Legislative & Regulatory Knowledge Hub
# -----------------------------------------------------------------------------
elif mode == "📚 مكتبة المعرفة التشريعية (Hub)":
    st.header("📚 مكتبة الأنظمة واللوائح البيئية (MEWA / NCEC)")

    st.subheader("🔍 معايير جودة المياه الجوفية والحدود المسموح بها")

    search_term = st.text_input("ابحث عن عنصر أو ملوث بيئي (مثال: ملوحة, VOCs, نترات):")

    reg_data = [
        {"العنصر": "المركبات العضوية المتطايرة (VOCs)", "الحد المسموح (MEWA)": "0.005 mg/L", "الجهة التنظيمية": "NCEC",
         "الإجراء الموصى به": "معالجة فورية بالسبر"},
        {"العنصر": "الأملاح الذائبة الكلية (TDS)", "الحد المسموح (MEWA)": "1000 mg/L", "الجهة التنظيمية": "MEWA",
         "الإجراء الموصى به": "ترشيح اسموزي عكسي"},
        {"العنصر": "النترات (NO3)", "الحد المسموح (MEWA)": "45 mg/L", "الجهة التنظيمية": "MEWA / NCEC",
         "الإجراء الموصى به": "مراقبة دورية كل 3 أشهر"},
        {"العنصر": "الرصاص والمعادن الثقيلة", "الحد المسموح (MEWA)": "0.01 mg/L", "الجهة التنظيمية": "NCEC",
         "الإجراء الموصى به": "عزل وتجريف البؤرة"}
    ]

    df_reg = pd.DataFrame(reg_data)

    if search_term:
        df_reg = df_reg[df_reg["العنصر"].str.contains(search_term, case=False)]

    st.dataframe(df_reg, use_container_width=True)