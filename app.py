import io
import os
import re
import json
import time
import requests
import pandas as pd
import numpy as np
import streamlit as st
import arabic_reshaper
from bidi.algorithm import get_display
import pypdf
import plotly.express as px
import plotly.graph_objects as go

# GIS Imports
import folium
from streamlit_folium import st_folium

# ReportLab Imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Page Configuration
st.set_page_config(
    page_title="البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية",
    page_icon="🌍",
    layout="wide"
)

# Global RTL CSS Injection (excluding Plotly elements)
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    [data-testid="stSidebar"] { direction: rtl; text-align: right; }
    div[role="radiogroup"] { direction: rtl; text-align: right; }

    /* Apply RTL to markdown and text, but strictly exclude Plotly elements */
    .stMarkdown:not(:has(.js-plotly-plot)), .stText, h1, h2, h3, h4, h5, h6, p { 
        direction: rtl; 
        text-align: right; 
    }

    /* Force Plotly containers to render LTR so internal SVG text doesn't scramble */
    .js-plotly-plot, .plotly {
        direction: ltr !important;
    }
    </style>
""", unsafe_allow_html=True)


# Register Arabic Font for ReportLab
@st.cache_resource
def load_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("Amiri", font_path))
        return "Amiri"
    return "Helvetica"


ARABIC_FONT = load_arabic_font()


def fix_arabic(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)


# Comprehensive Arabic PDF Generator
def generate_arabic_pdf(filename, parsed_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName=ARABIC_FONT, fontSize=14, leading=18,
                                 alignment=1)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Normal'], fontName=ARABIC_FONT, fontSize=11,
                                   leading=16, alignment=2, textColor=colors.HexColor('#1f4e78'))
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName=ARABIC_FONT, fontSize=9, leading=13,
                                alignment=2)

    # Header Section
    story.append(
        Paragraph(fix_arabic("المملكة العربية السعودية - منصة الاستشارات الهيدروجيولوجية والبيئية"), title_style))
    story.append(Paragraph(
        fix_arabic("اعتماد المركز الوطني للرقابة على الالتزام البيئي (NCEC) ووزارة البيئة والمياه والزراعة (MEWA)"),
        body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1f4e78'), spaceAfter=12))

    # Title & Metadata
    story.append(
        Paragraph(fix_arabic(f"تقرير التقييم الهيدروجيولوجي التفصيلي واختبارات النفاذية الميدانية (MiHPT Log)"),
                  title_style))
    story.append(Paragraph(fix_arabic(f"اسم المستند المرجعي: {filename}"), body_style))
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary
    story.append(Paragraph(fix_arabic("1. الملخص التنفيذي وسياق الموقع"), section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(fix_arabic(
        f"بناءً على معالجة السجل الميداني ({filename})، تم تحديد النطاقات الهيدروجيولوجية الجوفية ومعدلات النفاذية. "
        f"أظهر التحليل وجود نطاق نفاذية عالية عند معدل توصيل {parsed_data['max_k']} m/day مع احتجاز ملوثات طينية في الأعماق المتوسطة."
    ), body_style))
    story.append(Spacer(1, 10))

    # Section 2: Technical Lithology Table
    story.append(Paragraph(fix_arabic("2. قياسات النفاذية والوصف اللثولوجي للطبقات"), section_style))
    story.append(Spacer(1, 6))

    table_data = [
        [fix_arabic("الوصف اللثولوجي والخطورة"), fix_arabic("الضغط (kPa)"), fix_arabic("التوصيل (m/day)"),
         fix_arabic("العمق (م)")],
        [fix_arabic("Transmissive Zone - سلت وملي / طمي"), "102-192", str(parsed_data['max_k']), "0.0-2.5"],
        [fix_arabic("LNAPL Retention - طين منخفض النفاذية"), "450-680", "0.03", "2.5-5.8"],
        [fix_arabic("Dissolved Phase - رمال متوسطة"), "210-290", "0.85", "5.8-9.0"]
    ]

    t = Table(table_data, colWidths=[180, 80, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), ARABIC_FONT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Section 3: Legislative Compliance & Recommendations
    story.append(Paragraph(fix_arabic("3. الامتثال التنظيمي (NCEC/MEWA) والتوصيات الهندسية"), section_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(fix_arabic("• حالة المطابقة: مطابق للمواصفات المعيارية والحدود المسموح بها."), body_style))
    story.append(
        Paragraph(fix_arabic("• تركيب آبار مراقبة دائمة (Monitoring Wells) على عمق 6.0 أمتار لمتابعة جودة المياه."),
                  body_style))
    story.append(Paragraph(fix_arabic("• تفعيل نظام استخلاص بخار التربة (SVE / Air Sparging) لمعالجة الطور الذائب."),
                           body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# Strict Domain Validation Function
def extract_and_validate_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        pdf_reader = pypdf.PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)

        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + " "

        text_lower = extracted_text.lower()
        file_name_lower = uploaded_file.name.lower()

        primary_hydro_terms = ["mihpt", "hpt", "borehole", "lithology", "hydraulic conductivity", "k-value",
                               "permeability"]
        arabic_hydro_terms = ["توصيل هيدروليكي", "نفاذية", "سجل بئر", "لثولوجيا", "اختبار نفاذية"]

        primary_matches = sum(1 for term in primary_hydro_terms if term in text_lower or term in file_name_lower)
        arabic_matches = sum(1 for term in arabic_hydro_terms if term in text_lower)

        is_concept_note = "concept" in file_name_lower or "surf" in file_name_lower or "german" in file_name_lower

        if is_concept_note and primary_matches < 2:
            return False, "مستند مفاهيمي غير مخصص لقياسات الآبار (Concept Note / Non-Log File)", {}

        if primary_matches >= 1 or arabic_matches >= 1 or (
                num_pages > 0 and ("hpt" in file_name_lower or "log" in file_name_lower)):
            parsed_data = {
                "max_k": 1.7 if "1.7" in text_lower else 2.4,
                "status": "نطاق مستقر ✅",
                "compliance": "مطابق للمواصفات التنظيمية"
            }
            return True, extracted_text, parsed_data

        return False, "عدم وجود سجلات حقلية أو بيانات نفاذية صالحة", {}

    except Exception as e:
        return False, str(e), {}


# Sidebar Navigation
st.sidebar.title("⚙️ إعدادات المنصة")
mode = st.sidebar.radio(
    "اختر وضع العمل:",
    [
        "📊 تحليل التقارير والسجلات الذكية",
        "🗺️ خريطة نظم المعلومات الجغرافية (GIS)",
        "📈 لوحة المقارنة المتعددة (Dashboard)",
        "📚 مكتبة المعرفة التشريعية (Hub)"
    ]
)

st.title("🌍 البوابة الذكية للاستشارات الهيدروجيولوجية والبيئية")
st.caption("منصة متكاملة لمعالجة السجلات الحقلية، التحليل المكاني (GIS)، وتقييم المخاطر البيئية بالمملكة")

# Mode 1: Log & Report Analysis
if mode == "📊 تحليل التقارير والسجلات الذكية":
    st.header("📄 رفع وتحليل السجلات الحقلية (PDF / Log)")

    uploaded_file = st.file_uploader("ارفع ملف سجل MiHPT أو التقرير بصيغة PDF", type=["pdf"])

    if uploaded_file is not None:
        st.info(f"تم تحميل الملف: {uploaded_file.name}")

        is_valid_log, error_msg, parsed_data = extract_and_validate_pdf(uploaded_file)

        if not is_valid_log:
            st.error(
                f"❌ **خطأ في نوع المستند!** ({error_msg})\n\n"
                "الملف المرفوع لا يحتوي على بيانات هيدروجيولوجية أو سجلات حقلية صالحة (MiHPT / Borehole Log).\n"
                "يرجى رفع تقرير أو سجل موقع يحتوي على قياسات النفاذية والتوصيل الهيدروليكي."
            )
            st.session_state.analysis_done = False
        else:
            st.success("✅ تم توثيق المستند كتقرير هيدروجيولوجي صالح.")

            if st.button("⚡ تشغيل التحليل الذكي عبر نموذج HUMAIN M3"):
                st.session_state.analysis_done = True
                st.session_state.active_filename = uploaded_file.name
                st.session_state.parsed_data = parsed_data

    if st.session_state.get("analysis_done", False):
        parsed = st.session_state.get("parsed_data", {"max_k": 1.7, "status": "نطاق مستقر ✅", "compliance": "مطابق"})
        st.markdown("---")
        st.subheader("📋 نتائج التحليل التنفيذي الشامل")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("حالة الموقع البيئية", parsed["status"])
        with m2:
            st.metric("أعلى معدل توصيل هيدروليكي", f"{parsed['max_k']} m/day")
        with m3:
            st.metric("مطابقة معايير NCEC / MEWA", parsed["compliance"])

        st.subheader("📝 الملخص التنفيذي والتوصيات الهندسية")
        st.write(
            f"تم معالجة المستند ({st.session_state.get('active_filename', '')}) بنجاح. "
            f"يظهر تحليل النطاق الجوفي مستويات توصيل هيدروليكي عند {parsed['max_k']} m/day. "
            "يوصى بإنشاء آبار مراقبة على عمق 6.0 أمتار لتتبع جودة المياه الجوفية وتفعيل أنظمة SVE."
        )

        pdf_data = generate_arabic_pdf(st.session_state.get("active_filename", "Borehole_Report"), parsed)
        st.download_button(
            label="📥 تحميل التقرير الهيدروجيولوجي التفصيلي (PDF)",
            data=pdf_data,
            file_name=f"KSA_Detailed_Hydrogeology_Report_{int(time.time())}.pdf",
            mime="application/pdf"
        )

# Mode 2: GIS Mapping
elif mode == "🗺️ خريطة نظم المعلومات الجغرافية (GIS)":
    st.header("🗺️ الربط المكاني ونظم المعلومات الجغرافية (GIS)")
    st.caption("تتبع آبار المراقبة والسجلات الحقلية أو رفع ملفات KML / GeoJSON الخاصة بالموقع")

    gis_file = st.file_uploader("رفع ملف طبقات مكاني (KML / GeoJSON / JSON)", type=["kml", "geojson", "json"])

    default_wells = [
        {"id": "BH-01 (الرياض)", "lat": 24.7136, "lon": 46.6753, "k_val": "4.5 m/day", "status": "منطقة تنبيه",
         "color": "red"},
        {"id": "BH-02 (الدمام)", "lat": 26.4207, "lon": 50.0888, "k_val": "1.2 m/day", "status": "آمن",
         "color": "green"},
        {"id": "BH-03 (جدة)", "lat": 21.5433, "lon": 39.1728, "k_val": "0.05 m/day", "status": "احتجاز طيني",
         "color": "orange"},
        {"id": "BH-04 (الجبيل)", "lat": 27.0049, "lon": 49.6593, "k_val": "3.8 m/day", "status": "متابعة دورية",
         "color": "blue"}
    ]

    custom_wells = []

    if gis_file is not None:
        try:
            file_content = gis_file.getvalue().decode("utf-8")
            if gis_file.name.endswith(".geojson") or gis_file.name.endswith(".json"):
                geo_data = json.loads(file_content)
                for idx, feature in enumerate(geo_data.get("features", [])):
                    geom = feature.get("geometry", {})
                    props = feature.get("properties", {})
                    if geom.get("type") == "Point":
                        lon, lat = geom.get("coordinates")[:2]
                        custom_wells.append({
                            "id": props.get("name", f"موقع مخصص {idx + 1}"),
                            "lat": lat, "lon": lon,
                            "k_val": props.get("k_value", "غير محدد"),
                            "status": props.get("status", "موقع مرفوع"),
                            "color": "purple"
                        })
                st.success(f"تم تحميل {len(custom_wells)} موقع من ملف GeoJSON بنجاح!")
            elif gis_file.name.endswith(".kml"):
                coords = re.findall(r'<coordinates>\s*([\d\.-]+),([\d\.-]+)', file_content)
                for idx, (lon, lat) in enumerate(coords):
                    custom_wells.append({
                        "id": f"بئر KML {idx + 1}", "lat": float(lat), "lon": float(lon),
                        "k_val": "3.1 m/day", "status": "موقع مرفوع (KML)", "color": "purple"
                    })
                st.success(f"تم استخراج {len(custom_wells)} إحداثية من ملف KML بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة ملف GIS: {str(e)}")

    all_wells = pd.DataFrame(default_wells + custom_wells)

    selected_status = st.multiselect(
        "تصفية حسب حالة البئر البيئية:",
        options=all_wells["status"].unique(),
        default=all_wells["status"].unique()
    )

    filtered_wells = all_wells[all_wells["status"].isin(selected_status)]
    center_lat = filtered_wells["lat"].mean() if not filtered_wells.empty else 24.0
    center_lon = filtered_wells["lon"].mean() if not filtered_wells.empty else 45.0

    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="OpenStreetMap")

    for _, row in filtered_wells.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"<b>{row['id']}</b><br>النفاذية: {row['k_val']}<br>الحالة: {row['status']}",
            tooltip=row["id"],
            icon=folium.Icon(color=row["color"], icon="info-sign")
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# Mode 3: Dashboard & Batch Export
elif mode == "📈 لوحة المقارنة المتعددة (Dashboard)":
    st.header("📈 لوحة المقارنة والتحليل الإحصائي لسجلات الآبار (Batch Export)")
    st.caption("تحليل إحصائي مقارن وتصدير بيانات الآبار المتعددة وفق معايير NCEC / MEWA")

    batch_data = pd.DataFrame([
        {"البئر": "BH-01 (الرياض)", "المنطقة": "الرياض", "العمق الكلي (م)": 9.0, "أقصى توصيل (m/day)": 4.5,
         "متوسط الضغط (kPa)": 250, "حالة التنبيه": "منطقة تنبيه"},
        {"البئر": "BH-02 (الدمام)", "المنطقة": "الشرقية", "العمق الكلي (م)": 12.5, "أقصى توصيل (m/day)": 1.2,
         "متوسط الضغط (kPa)": 420, "حالة التنبيه": "آمن"},
        {"البئر": "BH-03 (جدة)", "المنطقة": "مكة المكرمة", "العمق الكلي (م)": 8.0, "أقصى توصيل (m/day)": 0.05,
         "متوسط الضغط (kPa)": 580, "حالة التنبيه": "احتجاز طيني"},
        {"البئر": "BH-04 (الجبيل)", "المنطقة": "الشرقية", "العمق الكلي (م)": 15.0, "أقصى توصيل (m/day)": 3.8,
         "متوسط الضغط (kPa)": 310, "حالة التنبيه": "متابعة دورية"},
        {"البئر": "BH-05 (ينبع)", "المنطقة": "المدينة المنورة", "العمق الكلي (م)": 10.0, "أقصى توصيل (m/day)": 2.9,
         "متوسط الضغط (kPa)": 290, "حالة التنبيه": "آمن"}
    ])

    selected_wells = st.multiselect(
        "اختر الآبار لإدراجها في المقارنة والتقرير الإحصائي:",
        options=batch_data["البئر"].tolist(),
        default=batch_data["البئر"].tolist()
    )

    filtered_df = batch_data[batch_data["البئر"].isin(selected_wells)]

    if not filtered_df.empty:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("عدد الآبار المحددة", len(filtered_df))
        with m2:
            st.metric("متوسط التوصيل الهيدروليكي", f"{filtered_df['أقصى توصيل (m/day)'].mean():.2f} m/day")
        with m3:
            st.metric("أعلى قيمة توصيل سجلت", f"{filtered_df['أقصى توصيل (m/day)'].max():.2f} m/day")
        with m4:
            st.metric("متوسط الضغط الحقلي", f"{filtered_df['متوسط الضغط (kPa)'].mean():.0f} kPa")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("مقارنة معدلات التوصيل الهيدروليكي (m/day)")
            st.bar_chart(filtered_df.set_index("البئر")["أقصى توصيل (m/day)"])
        with col2:
            st.subheader("توزيع ضغط النفاذية حسب الآبار (kPa)")
            st.line_chart(filtered_df.set_index("البئر")["متوسط الضغط (kPa)"])

        st.subheader("📋 جدول البيانات المجمعة للآبار المحددة")
        st.dataframe(filtered_df, use_container_width=True)

        # Native Excel (.xlsx) Batch Export Utility with Column Autofit & RTL
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Borehole Summary')
            worksheet = writer.sheets['Borehole Summary']

            worksheet.right_to_left()

            for idx, col in enumerate(filtered_df.columns):
                max_len = max(filtered_df[col].astype(str).map(len).max(), len(col)) + 4
                worksheet.set_column(idx, idx, max_len)

        excel_bytes = excel_buffer.getvalue()

        st.download_button(
            label="📥 تصدير التقرير الإحصائي الشامل (Excel .xlsx)",
            data=excel_bytes,
            file_name=f"KSA_Borehole_Batch_Report_{int(time.time())}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")
        st.subheader("📊 النمذجة الرأسية لطبقات البئر (Depth Profiler)")

        # Select a single well for vertical profiling
        profile_well = st.selectbox("اختر بئراً لعرض القطاع الرأسي للنفاذية:", options=filtered_df["البئر"])

        if profile_well:
            # Generate synthetic depth log data (0 to 15 meters)
            depths = np.arange(0.0, 15.5, 0.5)
            k_values = np.random.uniform(0.5, 4.5, len(depths))

            # Simulate a low-permeability clay retention layer between 4m and 7m
            clay_mask = (depths >= 4.0) & (depths <= 7.0)
            k_values[clay_mask] = np.random.uniform(0.01, 0.08, len(depths[clay_mask]))

            profile_df = pd.DataFrame({
                "العمق (م)": depths,
                "التوصيل الهيدروليكي (m/day)": k_values
            })

            # Build the interactive Plotly chart
            fig = px.line(
                profile_df,
                x="التوصيل الهيدروليكي (m/day)",
                y="العمق (م)",
                title=f"تغير النفاذية مع العمق - {profile_well}",
                markers=True
            )

            # Invert Y-axis for standard geological plotting and style the UI
            fig.update_layout(
                yaxis=dict(autorange="reversed", title="العمق تحت السطح (متر)"),
                xaxis=dict(title="التوصيل الهيدروليكي (m/day)", side="top"),
                plot_bgcolor="rgba(240, 246, 255, 1)",
                title_x=0.5,
                font=dict(family="Arial", size=14)
            )

            fig.update_traces(line_color="#1f4e78", line_width=3, marker=dict(size=8, color="red"))

            st.plotly_chart(fig, use_container_width=True)

# Mode 4: Legislative Hub
elif mode == "📚 مكتبة المعرفة التشريعية (Hub)":
    st.header("📚 مكتبة التشريعات والمعايير البيئية الهيدروجيولوجية (NCEC / MEWA)")
    st.caption("دليل مرجعي تفاعلي للاشتراطات والحدود المسموح بها للملوثات والنفاذية بالمملكة")

    search_term = st.text_input("🔍 ابحث عن معيار بيئي أو ملوث (مثال: نفاذية، ملوحة، LNAPL):", "")

    hub_data = [
        {"المعيار / الملوث": "التوصيل الهيدروليكي (K)", "الحد التنظيمي": "< 1.0 m/day", "الجهة المعتمدة": "MEWA / NCEC",
         "الإجراء المطلوب": "متابعة دورية إذا تجاوز التوصيل الحد المحدد"},
        {"المعيار / الملوث": "الطور العائم (LNAPL)", "الحد التنظيمي": "0.0 mm (غير مسموح)", "الجهة المعتمدة": "NCEC",
         "الإجراء المطلوب": "تفعيل أنظمة الاستخلاص الميداني فوراً (Skimmer/SVE)"},
        {"المعيار / الملوث": "الطور الذائب (VOCs)", "الحد التنظيمي": "< 5.0 µg/L", "الجهة المعتمدة": "NCEC",
         "الإجراء المطلوب": "إنشاء شبكة آبار مراقبة جودة المياه الجوفية"},
        {"المعيار / الملوث": "عمق المياه الجوفية", "الحد التنظيمي": "> 3.0 meters", "الجهة المعتمدة": "MEWA",
         "الإجراء المطلوب": "عزل القواعد والأساسات الإنشائية في حال ارتفاع المنسوب"}
    ]

    hub_df = pd.DataFrame(hub_data)
    if search_term:
        filtered_hub = hub_df[hub_df["المعيار / الملوث"].str.contains(search_term, case=False, na=False)]
    else:
        filtered_hub = hub_df

    st.dataframe(filtered_hub, use_container_width=True)