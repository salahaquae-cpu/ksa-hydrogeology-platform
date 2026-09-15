import base64
import requests
import markdown
import webbrowser
import os
import io
from PIL import Image

API_KEY = "sk-hn-salahaquae-830ae996-701380693f4c639ce90280c219b330aa"
IMAGE_PATH = "mihpt_log_1.png"

if not os.path.exists(IMAGE_PATH):
    print(f"Error: Could not find '{IMAGE_PATH}'.")
    exit()

# Optimize image size for visual tokens
with Image.open(IMAGE_PATH) as img:
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    max_size = (1600, 1600)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

# Strict Arabic Prompt Instruction
arabic_prompt = """
[تعليمات صارمة: يجب أن يكون كل النص الناتج باللغة العربية الفصحى فقط. يمنع استخدام اللغة الإنجليزية في الشرح والتحليل].

أنت استشاري هيدروجيولوجي. قم بتحليل سجل MiHPT المرفق باللغة العربية واكتب تقريراً فنياً كاملاً يتضمن:

# تقرير تحليل سجل MiHPT عالي الدقة

## 1. نطاقات التلوث الرئيسية (Contaminant Hotspots)
- حدد الأعماق التي تظهر فيها أعلى قراءات لكواشف PID و FID و XSD باللغة العربية (مثال: من عمق X متر إلى Y متر).

## 2. المقارنة الهيدروليكية والموصلية (EC & HPT Analysis)
- قارن بين قمم الملوثات وقيم الموصلية الكهربائية (EC) وضغط المحقن (HPT Pressure).
- هل التلوث يقع في طبقة عالية النفاذية (رمل/حصى) أم طبقة طينية محتجزة؟

## 3. التقييم البيئي وتوصيات المعالجة
قدّم التوصيات في جدول منظم باللغة العربية يحتوي على:
| النطاق العمقي | نوع الطبقة | مستوى الخطر | تقنية المعالجة المقترحة |
"""

payload = {
    "model": "humain-m3-research-preview",
    "messages": [
        {
            "role": "system",
            "content": "You are a hydrogeology expert. CRITICAL REQUIREMENT: Output MUST be completely in Arabic (اللغة العربية). Do not write any explanatory text in English."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": arabic_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ],
    "temperature": 0.2,  # Low temperature forces strict adherence to formatting
    "max_tokens": 4000
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

print("إرسال طلب تحليل MiHPT باللغة العربية...")
response = requests.post("https://api.node.humain.com/v1/chat/completions", json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    choice = data["choices"][0]

    report_content = choice["message"].get("content")
    if not report_content and "reasoning_content" in choice["message"]:
        report_content = choice["message"]["reasoning_content"]

    if report_content:
        # Save raw Markdown
        with open("MiHPT_Analysis_Report_AR.md", "w", encoding="utf-8") as f:
            f.write(report_content)

        # Render HTML
        html_body = markdown.markdown(report_content, extensions=['tables'])
        html_document = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير تحليل سجل MiHPT</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #2d3748; line-height: 1.8; padding: 40px; direction: rtl; text-align: right; max-width: 900px; margin: auto; }}
        h1 {{ color: #1a365d; border-bottom: 3px solid #2b6cb0; padding-bottom: 8px; text-align: center; }}
        h2 {{ color: #2b6cb0; border-right: 4px solid #3182ce; padding-right: 10px; margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: right; }}
        th {{ background-color: #2b6cb0; color: white; }}
        tr:nth-child(even) {{ background-color: #f7fafc; }}
    </style>
</head>
<body>{html_body}</body>
</html>"""

        html_path = os.path.abspath("MiHPT_Analysis_Report_AR.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_document)

        print(f"تم إنشاء التقرير بالعربية بنجاح: {html_path}")
        webbrowser.open(f"file://{html_path}")
    else:
        print("الاستجابة فارغة.")
else:
    print("API Error Response:", response.text)