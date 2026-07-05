import os
import json
import gspread
from google.oauth2.service_account import Credentials
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
GCP_CRED_JSON = os.environ.get("GCP_CREDENTIALS")

# गुगल शीटशी कनेक्शन
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_dict = json.loads(GCP_CRED_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# मुख्य मॉडेल (नवीन v1 API)
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
prompt = "Generate 5 multiple choice questions for NEET exam on the topic 'Physics: Thermodynamics'. Return ONLY a valid JSON array of objects. Keys: question, optionA, optionB, optionC, optionD, correctOption, explanation. Do not use markdown tags."

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.2}
}

headers = {"Content-Type": "application/json"}

print("Gemini कडून प्रश्न जनरेट करत आहे (gemini-1.5-flash)...")
response = requests.post(url, json=payload, headers=headers)
data = response.json()

# जर पहिला मॉडेल सापडला नाही (404 Error), तर आपोआप दुसरा प्रयत्न (Fallback)
if 'error' in data and data['error'].get('code') == 404:
    print("पहिला मॉडेल सापडला नाही. आता 'gemini-pro' वापरून पुन्हा प्रयत्न करत आहे...")
    url_fallback = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    response = requests.post(url_fallback, json=payload, headers=headers)
    data = response.json()

# आलेले प्रश्न शीटमध्ये टाकणे
if 'candidates' in data:
    try:
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        questions = json.loads(text_response)

        print("गुगल शीटमध्ये प्रश्न सेव्ह करत आहे...")
        for q in questions:
            row = [
                q.get('question', ''), q.get('optionA', ''), q.get('optionB', ''), 
                q.get('optionC', ''), q.get('optionD', ''), q.get('correctOption', ''), 
                q.get('explanation', '')
            ]
            sheet.append_row(row)
        print(f"यशस्वी! गुगल शीटमध्ये {len(questions)} नवीन प्रश्न जोडले गेले आहेत.")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
else:
    print("अंतिम API Error:", data)
