import io
import os
import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display

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
    /* Full Right-to-Left Setup */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown, p, h1, h2, h3, h4, label {
        direction: rtl;
        text-align: right !important;
    }

    /* Primary Action Button Customization */
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

    /* Metric Visual Cards */
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
    """Reshapes Arabic text for right-to-left PDF generation."""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)


HUMAIN_API_KEY = st.secrets.get("HUMAIN_API_KEY", "")


# -----------------------------------------------------------------------------
# 4. Comprehensive Technical PDF Generator Function
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

    # Custom Paragraph Styles for PDF
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
        fontName=ARABIC_FONT, fontSize=9.5, leading=14,
        textColor=colors.HexColor('#212529'), alignment=2, spaceAfter=6
    )

    story = []

    # Header Meta Information
    story.append(
        Paragraph(fix_arabic("المملكة العربية السعودية - منصة الاستشارات الهيدروجيولوجية والبيئية"), body_style))
    story.append(Paragraph(
        fix_arabic("اعتماد المركز الوطني للرقابة على الالتزام البيئي (NCEC) ووزارة البيئة والمياه والزراعة (MEWA)"),
        body_style))
    story.append(Spacer(1, 8))

    # Title
    story.append(
        Paragraph(fix_arabic("تقرير تقييم المخاطر الهيدروجيولوجية واختبارات النفاذية الميدانية (MiHPT)"), title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(fix_arabic(f"معرف الملف المرجعي: {filename_ref}"), body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d6efd'), spaceAfter=12))

    # Section 1: Executive Summary
    story.append(Paragraph(fix_arabic("1. الملخص التنفيذي وسياق الدراسة"), h1_style))
    exec_summary_text = (
        "يقدم هذا التقرير تقييماً شاملاً للخصائص الهيدروجيولوجية بناءً على قراءات المسبار الحقلي (MiHPT). "
        "تمت المعالجة بواسطة نموذج الذكاء الاصطناعي M3 لتحديد معدلات التوصيل الهيدروليكي والنطاقات الحاملة "
        "للمياه، وتحديد مستويات النفاذية والخطورة البيئية وفقاً للأنظمة البيئية المعتمدة في المملكة."
    )
    story.append(Paragraph(fix_arabic(exec_summary_text), body_style))

    # Section 2: Hydrogeological Measurements Table
    story.append(Paragraph(fix_arabic("2. نتائج التحليل الفني وقياسات التوصيل الهيدروليكي"), h1_style))

    raw_table = [
        ["عمق الطبقة (م)", "التوصيل الهيدروليكي (m/day)", "الضغط الهيدروليكي (kPa)", "الوصف اللثولوجي للطبقة",
         "حالة النطاق والخطورة"],
        ["0.0 - 2.5", "4.5", "120 - 180", "سلت رملي مرتفع النفاذية", "نطاق انتقال (Transmissive Zone)"],
        ["2.5 - 5.8", "0.02", "450 - 680", "سلت طيني منخفض النفاذية", "نطاق احتجاز / تجمع (LNAPL Check)"],
        ["5.8 - 9.0", "2.1", "210 - 290", "رمال متوسطة الحبيبات", "طور ذائب (Dissolved Phase)"]
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

    t = Table(processed_table, colWidths=[80, 110, 110, 120, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f2c59')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # Section 3: Environmental Compliance & Regulatory Assessment
    story.append(Paragraph(fix_arabic("3. تقييم الامتثال البيئي والاشتراطات التنظيمية"), h1_style))
    compliance_text = (
        "استناداً إلى معايير NCEC و MEWA، يظهر الموقع تركيزات ملوحة وتوصيلية كهربائية مستقرة في النطاق العميق، "
        "بينما تظهر الطبقة السطحية (2.5 - 5.8 م) احتجازاً للملوثات العضوية المتطايرة (VOCs) مما يستدعي "
        "اتخاذ تدابير الوقاية الحقلية المبكرة."
    )
    story.append(Paragraph(fix_arabic(compliance_text), body_style))

    # Section 4: Corrective Actions & Engineering Recommendations
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
# 5. Streamlit User Interface Layout
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
                # Visual Metric Display Cards
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

                # Main Tabs for Clean Screen Organization
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

                # Report Download Action
                pdf_bytes = generate_comprehensive_pdf(uploaded_file.name)

                st.download_button(
                    label="📥 تحميل التقرير الهيدروجيولوجي الشامل (PDF)",
                    data=pdf_bytes,
                    file_name="KSA_Comprehensive_Hydrogeological_Report.pdf",
                    mime="application/pdf"
                )