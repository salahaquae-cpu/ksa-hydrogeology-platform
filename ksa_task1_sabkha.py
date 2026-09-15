import requests
import markdown
import webbrowser
import os

API_KEY = "sk-hn-salahaquae-830ae996-701380693f4c639ce90280c219b330aa"

prompt_text = (
    "اكتب تقريراً هيدروجيولوجياً وتقييماً كيميائياً متقدماً باللغة العربية لبيئة صبخة ساحلية (Coastal Sabkha) في منطقة الجبيل الصناعية بالمملكة العربية السعودية.\n\n"
    "يتضمن التقرير النقاط التالية:\n"
    "1. **الكيمياء الجيولوجية للسبخة:** تحليل التأثيرات التبخيرية الشديدة عند ملوحة مياه جوفية تتجاوز (TDS > 100,000 mg/L) ومستوى ماء جوفي سطحي (أقل من 1.5 متر).\n"
    "2. **ديناميكية حراك المعادن الثقيلة:** تقييم ذوبانية وحراك النيكل (Ni) والفاناديوم (V) الناتجة عن التكرير البترول تحت ظروف القوة الأيونية العالية (High Ionic Strength) ومعاملات النشاط الأيوني.\n"
    "3. **توازن الأيونات الرئيسية:** قياس نسب الصوديوم/الكلوريد والكبريتات/الكلوريد وتكون متبخرات الأنايدرايت والجبس والهاليت.\n"
    "4. **توصيات المعالجة والرصد:** تقديم استراتيجية إعادة تأهيل هيدروليكية ومراقبة بيئية متوافقة مع معايير المركز الوطني للرقابة على الالتزام البيئي (NCEC)."
)

payload = {
    "model": "humain-m3-research-preview",
    "messages": [
        {
            "role": "system",
            "content": "أنت خبير كيمياء هيدروجيولوجية متخصص في البيئات القاحلة والسبخات الساحلية في المملكة العربية السعودية. اكتب تقريراً باللغة العربية الفصحى حصراً وبشكل علمي دقيق."
        },
        {"role": "user", "content": prompt_text}
    ],
    "temperature": 0.2,
    "max_tokens": 3500
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

print("جاري تشغيل الاختبار 1: كيمياء صبخة الجبيل الساحلية...")
response = requests.post("https://api.node.humain.com/v1/chat/completions", json=payload, headers=headers)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        content = data["choices"][0]["message"].get("content")
        if content:
            with open("KSA_Task1_Sabkha_Assessment.md", "w", encoding="utf-8") as f:
                f.write(content)

            html_body = markdown.markdown(content, extensions=['tables'])
            html_doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقييم كيمياء صبخة الجبيل الساحلية - KSA</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #2d3748; line-height: 1.8; padding: 40px; direction: rtl; text-align: right; max-width: 950px; margin: auto; }}
        h1 {{ color: #742a2a; border-bottom: 3px solid #c53030; padding-bottom: 10px; text-align: center; }}
        h2 {{ color: #9b2c2c; border-right: 4px solid #c53030; padding-right: 12px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: right; }}
        th {{ background-color: #9b2c2c; color: white; }}
        tr:nth-child(even) {{ background-color: #fff5f5; }}
    </style>
</head>
<body>{html_body}</body>
</html>"""

            html_path = os.path.abspath("KSA_Task1_Sabkha_Assessment.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_doc)

            print("تم إنشاء تقرير الاختبار 1 بنجاح! جاري الفتح في المتصفح...")
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