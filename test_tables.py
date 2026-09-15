import requests
import json

API_KEY = "sk-hn-salahaquae-830ae996-826b69cd87999b5c88b495864be0244b"
MODEL = "humain-m3-research-preview"
URL = "https://api.node.humain.com/v1/chat/completions"

# إرسال المفتاح بالطريقتين لضمان المصادقة الصحيحة مع الخادم
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# --- 1️⃣ بيانات جدول EC/HPT (استخراج الطبقات الناقلة والحابسة) ---
ec_hpt_table = """
Depth (m),EC (mS/m),HPT Pressure (kPa),Estimated K (m/day)
0.5,25,120,4.2
1.5,40,150,3.8
2.5,180,520,0.01
3.5,310,680,0.005
4.5,85,210,1.8
5.5,50,160,2.9
"""

# --- 2️⃣ بيانات جدول GWS (استخراج أعماق العينات والنطاقات الملوثة) ---
gws_table = """
SampleID,Depth (m),FID Response (ppm),PID Response (ppm),VOC Status
GWS-01,1.5,12,8,Background
GWS-02,3.0,450,680,LNAPL Saturation
GWS-03,4.5,85,110,Dissolved Phase
GWS-04,6.0,15,10,Background
"""

# --- 3️⃣ بيانات جدول PFAS (تقييم المخاطر البيئية وفق معايير NCEC) ---
pfas_table = """
SampleID,Depth (m),PFOS (ng/L),PFOA (ng/L),Total PFAS (ng/L)
P-01,2.0,140,95,235
P-02,4.0,85,40,125
P-03,6.0,12,8,20
"""

tests = [
    {
        "name": "اختبار 1: جدول EC/HPT (الطبقات الناقلة والحابسة)",
        "prompt": f"حلّل هذا الجدول الهيدروجيولوجي لـ EC/HPT واستخرج بوضوح النطاقات الناقلة (Transmissive Zones) والنطاقات التخزينية الحابسة (Storage Zones) مع تحديد أعماقها، وقدم تقريراً فنياً بالعربية:\n\n{ec_hpt_table}",
        "output_file": "EC_HPT_Analysis.md"
    },
    {
        "name": "اختبار 2: جدول GWS (أعماق العينات ونطاقات التلوث)",
        "prompt": f"حلّل بيانات جدول مسح المياه الجوفية (GWS) واستخرج أعماق العينات وقراءات PID/FID، وحدد نطاق الذروة للتلوث الهيدروكربوني، بالعربية:\n\n{gws_table}",
        "output_file": "GWS_Analysis.md"
    },
    {
        "name": "اختبار 3: جدول PFAS (تقييم المخاطر البيئية وفق NCEC)",
        "prompt": f"حلّل جدول قياسات مركبات PFAS وقدم تقييم مخاطر بيئية شامل موجه للمركز الوطني للالتزام البيئي (NCEC)، مع تحديد العينات المتجاوزة للحدود المسموح بها، بالعربية:\n\n{pfas_table}",
        "output_file": "PFAS_Risk_Analysis.md"
    }
]

print("🚀 بدأ تشغيل اختبارات الجداول عبر HUMAIN M3...\n")

for test in tests:
    print(f"🔎 جاري تشغيل: {test['name']}...")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "أنت خبير هيدروجيولوجي وتقييم مخاطر بيئية معتمد في المملكة العربية السعودية (NCEC/MEWA)."
            },
            {
                "role": "user",
                "content": test["prompt"]
            }
        ],
        "max_tokens": 2000
    }

    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=120)
        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']

            with open(test["output_file"], "w", encoding="utf-8") as f:
                f.write(f"# {test['name']}\n\n" + content)

            print(f"✅ تم حفظ التقرير بنجاح في: {test['output_file']}\n")
        else:
            print(f"❌ خطأ: {response.status_code} - {response.text}\n")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال: {str(e)}\n")

print("✨ اكتملت العملية!")