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

# २. NEET चा संपूर्ण सिलॅबस (तुम्ही दिलेली संपूर्ण यादी)
syllabus = [
    # --- PHYSICS (Class 11 & 12) ---
    {"subject": "Physics", "chapter": "Physics and Measurement"},
    {"subject": "Physics", "chapter": "Kinematics"},
    {"subject": "Physics", "chapter": "Laws of Motion"},
    {"subject": "Physics", "chapter": "Work, Energy and Power"},
    {"subject": "Physics", "chapter": "System of Particles and Rotational Motion"},
    {"subject": "Physics", "chapter": "Gravitation"},
    {"subject": "Physics", "chapter": "Properties of Solids and Liquids"},
    {"subject": "Physics", "chapter": "Thermodynamics"},
    {"subject": "Physics", "chapter": "Kinetic Theory of Gases"},
    {"subject": "Physics", "chapter": "Oscillations"},
    {"subject": "Physics", "chapter": "Waves"},
    {"subject": "Physics", "chapter": "Electrostatics"},
    {"subject": "Physics", "chapter": "Current Electricity"},
    {"subject": "Physics", "chapter": "Magnetic Effects of Current and Magnetism"},
    {"subject": "Physics", "chapter": "Electromagnetic Induction and Alternating Currents"},
    {"subject": "Physics", "chapter": "Electromagnetic Waves"},
    {"subject": "Physics", "chapter": "Optics (Ray Optics and Wave Optics)"},
    {"subject": "Physics", "chapter": "Dual Nature of Matter and Radiation"},
    {"subject": "Physics", "chapter": "Atoms and Nuclei"},
    {"subject": "Physics", "chapter": "Electronic Devices (Semiconductor Electronics)"},
    {"subject": "Physics", "chapter": "Experimental Skills"},

    # --- CHEMISTRY (Class 11 & 12) ---
    {"subject": "Chemistry", "chapter": "Some Basic Concepts of Chemistry"},
    {"subject": "Chemistry", "chapter": "Structure of Atom"},
    {"subject": "Chemistry", "chapter": "Classification of Elements and Periodicity in Properties"},
    {"subject": "Chemistry", "chapter": "Chemical Bonding and Molecular Structure"},
    {"subject": "Chemistry", "chapter": "States of Matter"},
    {"subject": "Chemistry", "chapter": "Thermodynamics"},
    {"subject": "Chemistry", "chapter": "Equilibrium"},
    {"subject": "Chemistry", "chapter": "Redox Reactions"},
    {"subject": "Chemistry", "chapter": "Hydrogen"},
    {"subject": "Chemistry", "chapter": "s-Block Elements"},
    {"subject": "Chemistry", "chapter": "Some p-Block Elements"},
    {"subject": "Chemistry", "chapter": "Organic Chemistry - Some Basic Principles and Techniques"},
    {"subject": "Chemistry", "chapter": "Hydrocarbons"},
    {"subject": "Chemistry", "chapter": "Environmental Chemistry"},
    {"subject": "Chemistry", "chapter": "Solutions"},
    {"subject": "Chemistry", "chapter": "Electrochemistry"},
    {"subject": "Chemistry", "chapter": "Chemical Kinetics"},
    {"subject": "Chemistry", "chapter": "d- and f-Block Elements"},
    {"subject": "Chemistry", "chapter": "Coordination Compounds"},
    {"subject": "Chemistry", "chapter": "Haloalkanes and Haloarenes"},
    {"subject": "Chemistry", "chapter": "Alcohols, Phenols and Ethers"},
    {"subject": "Chemistry", "chapter": "Aldehydes, Ketones and Carboxylic Acids"},
    {"subject": "Chemistry", "chapter": "Amines"},
    {"subject": "Chemistry", "chapter": "Biomolecules"},
    {"subject": "Chemistry", "chapter": "Polymers"},
    {"subject": "Chemistry", "chapter": "Chemistry in Everyday Life"},

    # --- BIOLOGY (Class 11 & 12) ---
    {"subject": "Biology", "chapter": "The Living World"},
    {"subject": "Biology", "chapter": "Biological Classification"},
    {"subject": "Biology", "chapter": "Plant Kingdom"},
    {"subject": "Biology", "chapter": "Animal Kingdom"},
    {"subject": "Biology", "chapter": "Morphology of Flowering Plants"},
    {"subject": "Biology", "chapter": "Anatomy of Flowering Plants"},
    {"subject": "Biology", "chapter": "Structural Organisation in Animals"},
    {"subject": "Biology", "chapter": "Cell: The Unit of Life"},
    {"subject": "Biology", "chapter": "Biomolecules"},
    {"subject": "Biology", "chapter": "Cell Cycle and Cell Division"},
    {"subject": "Biology", "chapter": "Transport in Plants"},
    {"subject": "Biology", "chapter": "Mineral Nutrition"},
    {"subject": "Biology", "chapter": "Photosynthesis in Higher Plants"},
    {"subject": "Biology", "chapter": "Respiration in Plants"},
    {"subject": "Biology", "chapter": "Plant Growth and Development"},
    {"subject": "Biology", "chapter": "Digestion and Absorption"},
    {"subject": "Biology", "chapter": "Breathing and Exchange of Gases"},
    {"subject": "Biology", "chapter": "Body Fluids and Circulation"},
    {"subject": "Biology", "chapter": "Excretory Products and Their Elimination"},
    {"subject": "Biology", "chapter": "Locomotion and Movement"},
    {"subject": "Biology", "chapter": "Neural Control and Coordination"},
    {"subject": "Biology", "chapter": "Chemical Coordination and Integration"},
    {"subject": "Biology", "chapter": "Reproduction in Organisms"},
    {"subject": "Biology", "chapter": "Sexual Reproduction in Flowering Plants"},
    {"subject": "Biology", "chapter": "Human Reproduction"},
    {"subject": "Biology", "chapter": "Reproductive Health"},
    {"subject": "Biology", "chapter": "Principles of Inheritance and Variation"},
    {"subject": "Biology", "chapter": "Molecular Basis of Inheritance"},
    {"subject": "Biology", "chapter": "Evolution"},
    {"subject": "Biology", "chapter": "Human Health and Disease"},
    {"subject": "Biology", "chapter": "Strategies for Enhancement in Food Production"},
    {"subject": "Biology", "chapter": "Microbes in Human Welfare"},
    {"subject": "Biology", "chapter": "Biotechnology: Principles and Processes"},
    {"subject": "Biology", "chapter": "Biotechnology and Its Applications"},
    {"subject": "Biology", "chapter": "Organisms and Populations"},
    {"subject": "Biology", "chapter": "Ecosystem"},
    {"subject": "Biology", "chapter": "Biodiversity and Conservation"},
    {"subject": "Biology", "chapter": "Environmental Issues"}
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

# ४. प्रश्न मागवणे (एका वेळी ५ प्रश्न, उच्च दर्जाचे)
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
            # युनिक Question ID तयार करणे (उदा. BIO-A1B2C3)
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
