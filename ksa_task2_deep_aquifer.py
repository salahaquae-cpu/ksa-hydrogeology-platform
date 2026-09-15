import requests
import markdown
import webbrowser
import os

API_KEY = "sk-hn-salahaquae-830ae996-701380693f4c639ce90280c219b330aa"

prompt_text = (
    "اكتب تقريراً هندسياً باللغة العربية يحلل مخاطر التسرب والتلوث المتبادل بين الطبقات المائية العميقة والسطحية في المملكة العربية السعودية (مثل متكونات الساق، الوسيع، والبيَاض).\n\n"
    "يتضمن التقرير:\n"
    "1. **الآلية الهيدروليكية للتسرب (Hydraulic Short-Circuiting):** تحليل تأثير الآبار المهجورة أو غير المكملة إنشائياً كمسارات تفضيلية لانتقال الملوثات من الطبقات السطحية إلى الأحواض الأحفورية العميقة.\n"
    "2. **النمذجة الرياضية لتدفق التسرب:** حساب معدل التسرب العمودي (Vertical Leakage Rate) استناداً إلى فرق الضغط البيزومتري (Piezometric Head Differential) ومعامل نفاذية طبقة السد العازلة (Aquitard Vertical Conductivity Kz).\n"
    "3. **تقييم المخاطر على خزان المياه الجوفية الوطني:** قياس مدى تهديد استدامة مياه الشرب والزراعة وفق معايير وزارة البيئة والمياه والزراعة (MEWA).\n"
    "4. **خطة العزل الهندسي والإغلاق الفني:** تقديم جدول ببروتوكولات الإغلاق الهيكلي (Well Abandonment & Cement Grouting Protocols)."
)

payload = {
    "model": "humain-m3-research-preview",
    "messages": [
        {
            "role": "system",
            "content": "أنت استشاري هندسة مياه جوفية متخصص في الطبقات المائية الأحفورية والطباقية الجيولوجية للمملكة العربية السعودية (الغطاء الرسوبي العربي). اكتب تقريراً باللغة العربية الفصحى حصراً."
        },
        {"role": "user", "content": prompt_text}
    ],
    "temperature": 0.2,
    "max_tokens": 3500
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

print("جاري تشغيل الاختبار 2: تسرب الملوثات للطبقات الجوفية العميقة...")
response = requests.post("https://api.node.humain.com/v1/chat/completions", json=payload, headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        content = data["choices"][0]["message"].get("content")
        if content:
            with open("KSA_Task2_Deep_Aquifer_Leakage.md", "w", encoding="utf-8") as f:
                f.write(content)

            html_body = markdown.markdown(content, extensions=['tables'])
            html_doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقييم تسرب الملوثات للطبقات العميقة - KSA</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #2d3748; line-height: 1.8; padding: 40px; direction: rtl; text-align: right; max-width: 950px; margin: auto; }}
        h1 {{ color: #1a365d; border-bottom: 3px solid #2b6cb0; padding-bottom: 10px; text-align: center; }}
        h2 {{ color: #2b6cb0; border-right: 4px solid #3182ce; padding-right: 12px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: right; }}
        th {{ background-color: #2b6cb0; color: white; }}
        tr:nth-child(even) {{ background-color: #ebf8ff; }}
    </style>
</head>
<body>{html_body}</body>
</html>"""

            html_path = os.path.abspath("KSA_Task2_Deep_Aquifer_Leakage.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_doc)

            print("تم إنشاء تقرير الاختبار 2 بنجاح! جاري الفتح في المتصفح...")
            webbrowser.open(f"file://{html_path}")
        else:
            print("الاستجابة فارغة.")
    except Exception as e:
        print(f"فشل فك تشفير JSON: {e}")
        print("استجابة الخادم الخام:")
        print(response.text)
else:
    print("خطأ في الاتصال بالـ API:")
    print(response.text)