import requests
import markdown
import webbrowser
import os

API_KEY = "sk-hn-salahaquae-830ae996-701380693f4c639ce90280c219b330aa"

prompt_text = (
    "اكتب دراسة تقييم أثر بيئي (EIA) باللغة العربية لتأثير الصرف الساحلي عالي الملوحة والحرارة المرتفعة الناجم عن محطات التحلية ومشاريع البحر الأحمر (Red Sea Global / NEOM / AMAALA) على المياه الجوفية والبيئة الساحلية.\n\n"
    "تتضمن الدراسة:\n"
    "1. **هيدروديناميكية السحابة الملحية (Brine Plume Sinking):** محاكاة غوص السحابة شديدة الملوحة في الخزان الجوفي الشعابي المرجاني الساحلي (Carbonate Reef Aquifer) نتيجة فروق الكثافة المائية.\n"
    "2. **الانتشار الحراري والملحي:** تقييم التشتت الملحي-الحراري عند درجة حرارة مياه تصريف تتجاوز المعتاد بـ (+5°C) وملوحة تصل إلى 65,000 mg/L مقارنة ببيئة البحر الأحمر.\n"
    "3. **التأثير على البيئات الحساسة:** تقييم المخاطر على أشجار المانغروف والشعاب المرجانية الحافة للساحل.\n"
    "4. **خطة الإدارة والحد من الأثر البيئي:** تقديم حلول هندسية تعتمد معايير الصرف الصفري (Zero Liquid Discharge - ZLD) وحقن المياه عميقاً دون المساس بالطبقات السطحية."
)

payload = {
    "model": "humain-m3-research-preview",
    "messages": [
        {
            "role": "system",
            "content": "أنت خبير تقييم أثر بيئي وهيدرولوجيا ساحلية متقدمة متخصص في بيئة البحر الأحمر والمشاريع الكبرى في المملكة العربية السعودية. اكتب التقرير باللغة العربية الفصحى حصراً."
        },
        {"role": "user", "content": prompt_text}
    ],
    "temperature": 0.2,
    "max_tokens": 3500
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

print("جاري تشغيل الاختبار 3: دراسة أثر المحاليل الملحية الساحلية على البحر الأحمر...")
response = requests.post("https://api.node.humain.com/v1/chat/completions", json=payload, headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        content = data["choices"][0]["message"].get("content")
        if content:
            with open("KSA_Task3_Red_Sea_Brine_Impact.md", "w", encoding="utf-8") as f:
                f.write(content)

            html_body = markdown.markdown(content, extensions=['tables'])
            html_doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دراسة الأثر البيئي للمحاليل الملحية - البحر الأحمر</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #2d3748; line-height: 1.8; padding: 40px; direction: rtl; text-align: right; max-width: 950px; margin: auto; }}
        h1 {{ color: #22543d; border-bottom: 3px solid #38a169; padding-bottom: 10px; text-align: center; }}
        h2 {{ color: #2f855a; border-right: 4px solid #38a169; padding-right: 12px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: right; }}
        th {{ background-color: #2f855a; color: white; }}
        tr:nth-child(even) {{ background-color: #f0fff4; }}
    </style>
</head>
<body>{html_body}</body>
</html>"""

            html_path = os.path.abspath("KSA_Task3_Red_Sea_Brine_Impact.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_doc)

            print("تم إنشاء تقرير الاختبار 3 بنجاح! جاري الفتح في المتصفح...")
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