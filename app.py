import io
import os
import requests
import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display

# ReportLab Imports for PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -----------------------------------------------------------------------------
# 1. Page Configuration & Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. Font Registration & Arabic Text Reshaper Helper
# -----------------------------------------------------------------------------
# Register Amiri Arabic TTF Font for PDF Generation
FONT_PATH = "Amiri-Regular.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Amiri", FONT_PATH))
    ARABIC_FONT = "Amiri"
else:
    ARABIC_FONT = "Helvetica"  # Fallback if font missing


def fix_arabic(text: str) -> str:
    """
    Reshapes Arabic text and applies bidirectional algorithm for ReportLab.
    """
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


# -----------------------------------------------------------------------------
# 3. Secure API Key Access (Backend Secret Retrieval)
# -----------------------------------------------------------------------------
# Read HUMAIN_API_KEY securely from Streamlit Cloud Secrets without exposing to UI
HUMAIN_API_KEY = st.secrets.get("HUMAIN_API_KEY", "")


# -----------------------------------------------------------------------------
# 4. Helper Function: Generate PDF Report
# -----------------------------------------------------------------------------
def generate_pdf_report(title: str, summary_text: str, table_data: list = None) -> bytes:
    """
    Generates a structured PDF document with properly rendered Arabic text.
    """
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
    arabic_style = ParagraphStyle(
        'ArabicStyle',
        parent=styles['Normal'],
        fontName=ARABIC_FONT,
        fontSize=12,
        leading=16,
        alignment=2  # Right align for RTL Arabic
    )

    title_style = ParagraphStyle(
        'ArabicTitleStyle',
        parent=styles['Title'],
        fontName=ARABIC_FONT,
        fontSize=18,
        leading=22,
        alignment=1  # Center align
    )

    story = []

    # Title
    story.append(Paragraph(fix_arabic(title), title_style))
    story.append(Spacer(1, 15))

    # Summary Paragraph
    story.append(Paragraph(fix_arabic(summary_text), arabic_style))
    story.append(Spacer(1, 15))

    # Optional Data Table
    if table_data:
        processed_data = []
        for row in table_data:
            processed_row = [
                Paragraph(fix_arabic(str(cell)), arabic_style) for cell in row
            ]
            processed_data.append(processed_row)

        t = Table(processed_data, colWidths=[100] * len(table_data[0]))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# -----------------------------------------------------------------------------
# 5. Streamlit User Interface
# -----------------------------------------------------------------------------
st.title("🌍 البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية - المملكة العربية السعودية")
st.caption(
    "منصة ذكية متكاملة لتحليل السجلات الحقلية، الربط المكاني (GIS)، وتقييم المخاطر البيئية باستخدام الذكاء الاصطناعي.")

# Sidebar Navigation
st.sidebar.header("إعدادات النظام البيئي والـ GIS")
mode = st.sidebar.radio(
    "اختر وضع العمل في المنصة",
    [
        "تحليل التقارير والسجلات الذكية",
        "خريطة نظم المعلومات الجغرافية (GIS)",
        "لوحة المقارنة المتعددة للسجلات (Dashboard)",
        "مكتبة المعرفة التشريعية (Hub)"
    ]
)

# Display Key Warning in Sidebar if Key is missing in Secrets
if not HUMAIN_API_KEY:
    st.sidebar.warning("⚠️ لم يتم العثور على HUMAIN_API_KEY في إعدادات Streamlit Secrets.")

# Main Application Logic: Report Analysis
if mode == "تحليل التقارير والسجلات الذكية":
    st.header("📄 رفع وتحليل السجلات الحقلية (PDF / Log)")

    uploaded_file = st.file_uploader("ارفع ملف سجل MiHPT أو تقرير بصيغة PDF", type=["pdf", "png", "jpg"])

    if uploaded_file is not None:
        st.success("تم رفع الملف بنجاح.")

        if st.button("تشغيل التحليل الذكي عبر HUMAIN M3"):
            with st.spinner("جاري معالجة البيانات وتحليل التقرير..."):
                # Example Output Placeholder
                sample_summary = "تم تحليل البيانات الهيدروجيولوجية بنجاح. تشير القراءات إلى وجود نفاذية عالية في الطبقات الرملية مع استقرار مستويات المياه الجوفية."

                st.subheader("نتائج التحليل:")
                st.write(sample_summary)

                # Table Data Setup
                sample_table = [
                    ["العمق (متر)", "التوصيل الهيدروليكي", "جودة المياه"],
                    ["0.0 - 2.5", "مرتفع", "صالح للاستخدام"],
                    ["2.5 - 5.8", "منخفض", "ملوحة متوسطة"],
                    ["5.8 - 9.0", "متوسط", "عالي الملوحة"]
                ]

                st.table(sample_table)

                # Generate PDF for Download
                pdf_bytes = generate_pdf_report(
                    title="تقرير التحليل الهيدروجيولوجي",
                    summary_text=sample_summary,
                    table_data=sample_table
                )

                st.download_button(
                    label="📥 تحميل التقرير بصيغة PDF",
                    data=pdf_bytes,
                    file_name="KSA_Hydrogeological_Report.pdf",
                    mime="application/pdf"
                )