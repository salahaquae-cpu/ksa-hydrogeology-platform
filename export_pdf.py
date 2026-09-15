import base64
import requests

API_KEY = "sk-hn-salahaquae-830ae996-701380693f4c639ce90280c219b330aa"
IMAGE_PATH = "Screenshot 2026-09-07 102052.png"  # تأكد من وجود الصورة بهذا الاسم في المجلد

# قراءة الصورة وتحويلها إلى Base64
with open(IMAGE_PATH, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "humain-m3-research-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "حلّل هذا الجدول الخاص بقراءات EC و HPT واستخرج الطبقات الحابسة والطبقات الناقلة، بالعربية."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        }
    ],
    "max_tokens": 2500
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("جاري إرسال الطلب إلى HUMAIN API...")
response = requests.post("https://api.node.humain.com/v1/chat/completions", json=payload, headers=headers)

print(f"رمز الاستجابة (Status Code): {response.status_code}")

if response.status_code == 200:
    data = response.json()
    message = data["choices"][0]["message"]

    # آليّة آمنة لاستخراج النص بغض النظر عن شكل المفتاح
    report_content = message.get("content")

    if report_content:
        with open("EC_HPT_Analysis.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("تم حفظ التقرير بنجاح في EC_HPT_Analysis.md")
    else:
        print("\nلم يتم العثور على 'content' مباشر داخل الرسالة. هيكل الرسالة المستلمة هو:")
        print(message)
else:
    print("حدث خطأ في الاتصال:")
    print(response.text)