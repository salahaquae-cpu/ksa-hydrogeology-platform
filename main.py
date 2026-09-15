import base64
import requests
import json
import os

# --- 1. إعداد البيانات والمفتاح ---
API_KEY = "sk-hn-salahaquae-830ae996-826b69cd87999b5c88b495864be0244b"  # مفتاح الـ API الخاص بك
MODEL = "humain-m3-research-preview"

# قائمة الصور المراد تحليلها
image_files = [
    "Screenshot 2026-09-07 102031.png",
]

print("🚀 بدأ تنفيذ main.py - تحليل الصور (HRSC Batch Analysis)")

results = {}

# --- 2. الحلقة التكرارية لمعالجة كل صورة ---
for img in image_files:
    if not os.path.exists(img):
        print(f"⚠️ تحذير: الملف {img} غير موجود في المجلد المحلي، سيتم تخطيه.")
        continue

    print(f"\n🔎 جاري تحليل الصورة: {img}")

    with open(img, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # إعداد الحمولة المعتمدة لـ HUMAIN Node API
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "أنت استشاري هيدروجيولوجي وخبير بيئي معتمد في تقييم سجلات HRSC و MiHPT. قم بتحليل المنحنيات بدقة وقدم تقريراً فنياً شاملاً باللغة العربية."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"حلّل سجل HRSC الظاهر في الصورة ({img}) وفق منهجية HRSC المعتمدة، واستخرج النطاقات الناقلة والتخزينية ومستويات التلوث، ثم قدّم تقريراً فنياً باللغة العربية."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000
    }

    try:
        # استخدام الرابط الصحيح المنتهي بـ api.node.humain.com
        response = requests.post(
            url="https://api.node.humain.com/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=120
        )

        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            results[img] = response.json()
        else:
            print(f"❌ خطأ في الاستجابة: {response.status_code} - {response.text}")
            results[img] = {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بالـ API: {str(e)}")
        results[img] = {"error": str(e)}

# --- 3. حفظ النتائج الخام في ملف JSON ---
with open("humain_image_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\n✅ تم حفظ النتائج الخام في ملف: humain_image_results.json")

# --- 4. إنشاء التقرير العربي الشامل (Markdown) ---
print("\n📝 جاري إنشاء التقرير الفني الموحد باللغة العربية...")
report_lines = []
report_lines.append("# تقرير فني شامل — نتائج تحليل سجلات HRSC عبر HUMAIN M3\n")
report_lines.append("--------------------------------------------------------\n")

for img, result in results.items():
    report_lines.append(f"\n## 📁 نتائج تحليل السجل الميداني: {img}\n")

    if "error" in result:
        report_lines.append(f"⚠️ فشل تحليل الصورة: {result['error']}")
        continue

    try:
        content = result["choices"][0]["message"]["content"]
        if content:
            report_lines.append(content)
        else:
            report_lines.append("⚠️ لا يوجد نص في استجابة النموذج.")
    except Exception as e:
        report_lines.append(f"⚠️ خطأ أثناء قراءة استجابة النموذج: {e}")

with open("HRSC_Report_Arabic.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("\n✅ تم توليد التقرير العربي بنجاح في الملف: HRSC_Report_Arabic.md")
