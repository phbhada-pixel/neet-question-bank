import os
import json
import gspread
from google.oauth2.service_account import Credentials
import requests
import random
import uuid

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
GCP_CRED_JSON = os.environ.get("GCP_CREDENTIALS")

# १. गुगल शीटशी कनेक्शन
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_dict = json.loads(GCP_CRED_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# २. विषयांची आणि चाप्टर्सची यादी (तुम्ही यात भविष्यात आणखी चाप्टर्स वाढवू शकता)
syllabus = [
    {"subject": "Physics", "chapter": "Thermodynamics"},
    {"subject": "Physics", "chapter": "Kinematics"},
    {"subject": "Chemistry", "chapter": "Chemical Bonding"},
    {"subject": "Chemistry", "chapter": "Organic Chemistry: Some Basic Principles"},
    {"subject": "Botany", "chapter": "Plant Kingdom"},
    {"subject": "Botany", "chapter": "Photosynthesis in Higher Plants"},
    {"subject": "Zoology", "chapter": "Human Reproduction"},
    {"subject": "Zoology", "chapter": "Evolution"}
]

# या यादीतून एक विषय आणि चाप्टर आपोआप निवडणे
selected_topic = random.choice(syllabus)
subject = selected_topic["subject"]
chapter = selected_topic["chapter"]

print(f"आजचा विषय: {subject} - {chapter}")

# ३. गुगलला उपलब्ध मॉडेल्स विचारणे
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
list_response = requests.get(list_url)
models_data = list_response.json()

valid_model_name = None
if 'models' in models_data:
    for model in models_data['models']:
        if 'generateContent' in model.get('supportedGenerationMethods', []) and 'flash' in model['name']:
            valid_model_name = model['name']
            break
    if not valid_model_name:
        for model in models_data['models']:
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                valid_model_name = model['name']
                break

if not valid_model_name:
    print("Error: योग्य मॉडेल सापडला नाही!")
    exit()

# ४. API ला सविस्तर माहितीसह प्रश्न विचारणे
url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={GEMINI_API_KEY}"
prompt = f"Generate 5 multiple choice questions for NEET exam on the Subject: '{subject}' and Chapter: '{chapter}'. Return ONLY a valid JSON array of objects. Keys must be exactly: 'question', 'optionA', 'optionB', 'optionC', 'optionD', 'correctOption', 'explanation'. The 'explanation' must be highly detailed and informative for students. Do not use markdown tags."

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.3}
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
data = response.json()

# ५. नवीन फॉरमॅटनुसार गुगल शीटमध्ये सेव्ह करणे
if 'candidates' in data:
    try:
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        questions = json.loads(text_response)

        print("गुगल शीटमध्ये डेटा सेव्ह करत आहे...")
        for q in questions:
            # युनिक Question ID तयार करणे (उदा. PHY-8A2F4B)
            q_id = f"{subject[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
            
            row = [
                q_id,
                subject,
                chapter,
                q.get('question', ''),
                q.get('optionA', ''),
                q.get('optionB', ''),
                q.get('optionC', ''),
                q.get('optionD', ''),
                q.get('correctOption', ''),
                q.get('explanation', '')
            ]
            sheet.append_row(row)
        print(f"यशस्वी! {subject} - {chapter} चे {len(questions)} नवीन प्रश्न जोडले गेले.")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
else:
    print("अंतिम API Error:", data)
