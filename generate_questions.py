import os
import json
import gspread
from google.oauth2.service_account import Credentials
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
GCP_CRED_JSON = os.environ.get("GCP_CREDENTIALS")

# १. गुगल शीटशी कनेक्शन
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_dict = json.loads(GCP_CRED_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# २. गुगलला विचारणे: "सध्या कोणते मॉडेल्स उपलब्ध आहेत?"
print("उपलब्ध मॉडेल्सची यादी तपासत आहे...")
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
list_response = requests.get(list_url)
models_data = list_response.json()

valid_model_name = None

# जे मॉडेल 'generateContent' ला सपोर्ट करतात, ते आपोआप निवडणे
if 'models' in models_data:
    for model in models_data['models']:
        if 'generateContent' in model.get('supportedGenerationMethods', []) and 'flash' in model['name']:
            valid_model_name = model['name']
            break
    
    # जर flash नाही मिळाला, तर कोणताही चालणारा मॉडेल निवडणे
    if not valid_model_name:
        for model in models_data['models']:
            if 'generateContent' in model.get('supportedGenerationMethods', []):
                valid_model_name = model['name']
                break
else:
    print("API Key Error:", models_data)
    exit()

if not valid_model_name:
    print("Error: तुमच्या API Key साठी एकही योग्य मॉडेल सापडला नाही!")
    exit()

print(f"सक्सेस! योग्य मॉडेल सापडला: '{valid_model_name}'. आता प्रश्न बनवत आहे...")

# ३. मिळालेला योग्य मॉडेल वापरून प्रश्न तयार करणे
url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={GEMINI_API_KEY}"
prompt = "Generate 5 multiple choice questions for NEET exam on the topic 'Physics: Thermodynamics'. Return ONLY a valid JSON array of objects. Keys: question, optionA, optionB, optionC, optionD, correctOption, explanation. Do not use markdown tags."

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.2}
}

headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
data = response.json()

# ४. आलेले प्रश्न शीटमध्ये सेव्ह करणे
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
        print(f"यशस्वी! गुगल शीटमध्ये {len(questions)} नवीन प्रश्न जोडले गेले आहेत. शीट तपासा!")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("API ने पाठवलेला मजकूर:", text_response)
else:
    print("अंतिम API Error:", data)
