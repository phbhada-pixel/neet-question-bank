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

# २. NEET चा संपूर्ण मुख्य सिलॅबस (यादी)
syllabus = [
    # PHYSICS
    {"subject": "Physics", "chapter": "Thermodynamics"},
    {"subject": "Physics", "chapter": "Kinematics & Motion in a Straight Line"},
    {"subject": "Physics", "chapter": "Laws of Motion"},
    {"subject": "Physics", "chapter": "Work, Energy, and Power"},
    {"subject": "Physics", "chapter": "Electrostatics"},
    {"subject": "Physics", "chapter": "Current Electricity"},
    {"subject": "Physics", "chapter": "Ray Optics and Optical Instruments"},
    {"subject": "Physics", "chapter": "Modern Physics & Atoms"},
    
    # CHEMISTRY
    {"subject": "Chemistry", "chapter": "Chemical Bonding and Molecular Structure"},
    {"subject": "Chemistry", "chapter": "Organic Chemistry: Some Basic Principles"},
    {"subject": "Chemistry", "chapter": "Some Basic Concepts of Chemistry (Mole Concept)"},
    {"subject": "Chemistry", "chapter": "Structure of Atom"},
    {"subject": "Chemistry", "chapter": "Equilibrium"},
    {"subject": "Chemistry", "chapter": "Coordination Compounds"},
    {"subject": "Chemistry", "chapter": "Biomolecules"},
    {"subject": "Chemistry", "chapter": "Solutions & Electrochemistry"},
    
    # BOTANY
    {"subject": "Botany", "chapter": "Plant Kingdom"},
    {"subject": "Botany", "chapter": "Photosynthesis in Higher Plants"},
    {"subject": "Botany", "chapter": "Cell Cycle and Cell Division"},
    {"subject": "Botany", "chapter": "Principles of Inheritance and Variation (Genetics)"},
    {"subject": "Botany", "chapter": "Sexual Reproduction in Flowering Plants"},
    {"subject": "Botany", "chapter": "Biological Classification"},
    {"subject": "Botany", "chapter": "Anatomy of Flowering Plants"},
    
    # ZOOLOGY
    {"subject": "Zoology", "chapter": "Human Reproduction"},
    {"subject": "Zoology", "chapter": "Evolution"},
    {"subject": "Zoology", "chapter": "Animal Kingdom"},
    {"subject": "Zoology", "chapter": "Human Health and Disease"},
    {"subject": "Zoology", "chapter": "Structural Organisation in Animals"},
    {"subject": "Zoology", "chapter": "Chemical Coordination and Integration"},
    {"subject": "Zoology", "chapter": "Biotechnology: Principles and Processes"}
]

# यादीतून एक विषय आणि चाप्टर दरवेळी रँडमली निवडला जाईल
selected_topic = random.choice(syllabus)
subject = selected_topic["subject"]
chapter = selected_topic["chapter"]

print(f"आजचा ऑटो-सिलेक्टेड विषय: {subject} - {chapter}")

# ३. गुगलला चालू मॉडेल विचारणे
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

# ४. प्रश्न मागवणे (एका वेळी ५ प्रश्न)
url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={GEMINI_API_KEY}"
prompt = f"Generate 5 high-quality, conceptual multiple choice questions for NEET exam on the Subject: '{subject}' and Chapter: '{chapter}'. Return ONLY a valid JSON array of objects. Keys must be exactly: 'question', 'optionA', 'optionB', 'optionC', 'optionD', 'correctOption', 'explanation'. The 'explanation' must be highly detailed and informative explaining why the option is correct and others are wrong. Do not use markdown tags."

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.3}
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
data = response.json()

# ५. गुगल शीटमध्ये डेटा सेव्ह करणे
if 'candidates' in data:
    try:
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        questions = json.loads(text_response)

        print("गुगल शीटमध्ये डेटा सेव्ह करत आहे...")
        for q in questions:
            # युनिक Question ID तयार करणे (उदा. BOT-A1B2C3)
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
