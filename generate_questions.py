import os
import json
import gspread
from google.oauth2.service_account import Credentials
import requests
import random
import uuid
from datetime import datetime, timedelta

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
GCP_CRED_JSON = os.environ.get("GCP_CREDENTIALS")

# १. गुगल शीटशी कनेक्शन
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds_dict = json.loads(GCP_CRED_JSON)
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# गुगल शीटमधील आधीचे सर्व प्रश्न वाचून घेणे (डुप्लिकेट टाळण्यासाठी)
try:
    existing_questions_list = sheet.col_values(4) 
except:
    existing_questions_list = []

# २. NEET 2025 चा सविस्तर सिलॅबस (PDF नुसार सविस्तर Topics सह)
syllabus = [
    # --- PHYSICS ---
    {"subject": "Physics", "chapter": "Physics and Measurement", "topics": "Units of measurements, System of Units, SI Units, fundamental and derived units, least count, significant figures, Errors in measurements, Dimensions of Physics quantities, dimensional analysis."},
    {"subject": "Physics", "chapter": "Kinematics", "topics": "Frame of reference, motion in a straight line, Position-time graph, speed, velocity, Uniform and non-uniform motion, average speed, instantaneous velocity, uniformly accelerated motion, Scalars and Vectors, Relative Velocity, Motion in a plane, Projectile Motion, Uniform Circular Motion."},
    {"subject": "Physics", "chapter": "Laws of Motion", "topics": "Force, inertia, Newton's laws of motion, Momentum, Impulses, Law of conservation of linear momentum. Static and Kinetic friction, rolling friction. Dynamics of uniform circular motion, centripetal force."},
    {"subject": "Physics", "chapter": "Work, Energy, and Power", "topics": "Work done by a constant/variable force; kinetic and potential energies, work-energy theorem, power. Potential energy of spring, conservative/non-conservative forces, elastic and inelastic collisions."},
    {"subject": "Physics", "chapter": "Rotational Motion", "topics": "Centre of mass, moment of a force, torque, angular momentum, conservation of angular momentum. Moment of inertia, radius of gyration, parallel and perpendicular axes theorems, equilibrium of rigid bodies."},
    {"subject": "Physics", "chapter": "Gravitation", "topics": "Universal law of gravitation. Acceleration due to gravity, Kepler's law, Gravitational potential energy, Escape velocity, orbital velocity of satellite."},
    {"subject": "Physics", "chapter": "Properties of Solids and Liquids", "topics": "Elastic behaviour, Stress-strain, Hooke's Law, Young's modulus. Pressure due to fluid, Pascal's law, Viscosity, Stokes' law, terminal velocity, Bernoulli's principle. Surface tension, Heat transfer (conduction, convection, radiation)."},
    {"subject": "Physics", "chapter": "Thermodynamics", "topics": "Thermal equilibrium, zeroth, first and second law of thermodynamics. Isothermal and adiabatic processes, reversible and irreversible processes."},
    {"subject": "Physics", "chapter": "Kinetic Theory of Gases", "topics": "Equation of state of a perfect gas, work done on compressing a gas, Kinetic interpretation of temperature, RMS speed, Degrees of freedom, Law of equipartition of energy, Mean free path."},
    {"subject": "Physics", "chapter": "Oscillations and Waves", "topics": "Periodic motion, SHM and its equation, phase, restoring force, Simple pendulum. Wave motion, Longitudinal/transverse waves, Principle of superposition, Standing waves, Beats."},
    {"subject": "Physics", "chapter": "Electrostatics", "topics": "Electric charges, Coulomb's law, Electric field, Electric dipole, Gauss's law and applications, Electric potential, Equipotential surfaces, Conductors, insulators, Dielectrics, capacitors, energy stored."},
    {"subject": "Physics", "chapter": "Current Electricity", "topics": "Electric current, Drift velocity, Ohm's law, V-I characteristics, Electrical resistance, resistivity, combinations of resistors. Kirchhoff's laws, Wheatstone bridge, Metre Bridge."},
    {"subject": "Physics", "chapter": "Magnetic Effects of Current and Magnetism", "topics": "Biot Savart law, Ampere's law, Force on a moving charge, Force on a current-carrying conductor, Moving coil galvanometer, Magnetic dipole, Para-, dia- and ferromagnetic substances."},
    {"subject": "Physics", "chapter": "Electromagnetic Induction and AC", "topics": "Faraday's law, Lenz's Law, Eddy currents, Self and mutual inductance. Alternating currents, LCR series circuit, resonance, AC generator, transformer."},
    {"subject": "Physics", "chapter": "Electromagnetic Waves", "topics": "Displacement current, Electromagnetic spectrum (radio, micro, IR, visible, UV, X-rays, Gamma rays), Transverse nature."},
    {"subject": "Physics", "chapter": "Optics", "topics": "Reflection, refraction, spherical mirrors, lenses, Total internal reflection, Prism, Microscope, Telescope. Wave optics: Huygens' principle, Interference, Young's double-slit, Diffraction, Polarization."},
    {"subject": "Physics", "chapter": "Dual Nature of Matter and Radiation", "topics": "Photoelectric effect, Einstein's photoelectric equation, Matter waves, de Broglie relation."},
    {"subject": "Physics", "chapter": "Atoms and Nuclei", "topics": "Alpha-particle scattering, Rutherford's model, Bohr model, hydrogen spectrum. Nucleus composition, mass defect, binding energy, nuclear fission, fusion."},
    {"subject": "Physics", "chapter": "Electronic Devices", "topics": "Semiconductors, p-n junction diode, forward and reverse bias, LED, photodiode, solar cell, Zener diode, Logic gates (OR, AND, NOT, NAND, NOR)."},
    {"subject": "Physics", "chapter": "Experimental Skills", "topics": "Vernier calipers, Screw gauge, Simple Pendulum, Metre Scale, Young's modulus, Surface tension, Viscosity, Speed of sound, Specific heat capacity, Resistivity, Ohm's law, Galvanometer, Focal length of mirrors/lenses, Prism, Diode characteristics."},

    # --- CHEMISTRY ---
    {"subject": "Chemistry", "chapter": "Some Basic Concepts in Chemistry", "topics": "Dalton's atomic theory, Atomic/molecular masses, mole concept, molar mass, empirical/molecular formulae, stoichiometry."},
    {"subject": "Chemistry", "chapter": "Atomic Structure", "topics": "Bohr model, dual nature of matter, de Broglie, Heisenberg uncertainty, Quantum mechanics, quantum numbers, shapes of orbitals, Aufbau, Pauli's, Hund's rule."},
    {"subject": "Chemistry", "chapter": "Chemical Bonding and Molecular Structure", "topics": "Ionic and covalent bonds, VSEPR theory, Valence bond theory, hybridization (s, p, d), Resonance, Molecular Orbital Theory, Hydrogen bonding."},
    {"subject": "Chemistry", "chapter": "Chemical Thermodynamics", "topics": "System, surroundings, first law, enthalpy, Hess's law, heat of reaction. Second law, Spontaneity, Entropy, Gibbs energy change."},
    {"subject": "Chemistry", "chapter": "Solutions", "topics": "Concentration of solution (molality, molarity, mole fraction), Raoult's Law, Ideal/non-ideal solutions, Colligative properties (lowering of VP, depression of FP, elevation of BP, osmotic pressure), van't Hoff factor."},
    {"subject": "Chemistry", "chapter": "Equilibrium", "topics": "Physical/chemical equilibrium, Le Chatelier's principle, Ionic equilibrium, pH scale, common ion effect, hydrolysis of salts, solubility products, buffer solutions."},
    {"subject": "Chemistry", "chapter": "Redox Reactions and Electrochemistry", "topics": "Oxidation number, balancing redox reactions. Electrolytic conduction, Kohlrausch's law, Galvanic cells, Nernst equation, Fuel cells."},
    {"subject": "Chemistry", "chapter": "Chemical Kinetics", "topics": "Rate of reaction, factors affecting rate, order and molecularity, zero/first-order reactions, half-life, Arrhenius theory, activation energy."},
    {"subject": "Chemistry", "chapter": "Classification of Elements", "topics": "Modern periodic law, s, p, d, f blocks, periodic trends (atomic radii, ionization enthalpy, electron gain enthalpy, electronegativity)."},
    {"subject": "Chemistry", "chapter": "p-Block Elements", "topics": "Group 13 to 18 Elements: Electronic configuration, general trends in physical/chemical properties, unique behaviour of first element."},
    {"subject": "Chemistry", "chapter": "d and f-Block Elements", "topics": "Transition Elements: properties, colour, catalytic behaviour, magnetic properties, alloys. K2Cr2O7, KMnO4. Lanthanoids and Actinoids."},
    {"subject": "Chemistry", "chapter": "Co-ordination Compounds", "topics": "Werner's theory, ligands, IUPAC nomenclature, isomerism, Valence bond and Crystal field theory, importance in biology/analysis."},
    {"subject": "Chemistry", "chapter": "Purification and Characterisation of Organic Compounds", "topics": "Crystallization, distillation, extraction, chromatography. Qualitative analysis (N, S, P, halogens). Quantitative analysis (empirical/molecular formulae)."},
    {"subject": "Chemistry", "chapter": "Some Basic Principles of Organic Chemistry", "topics": "Tetravalency of carbon, functional groups, Isomerism. IUPAC Nomenclature. Homolytic/heterolytic fission, electrophiles, nucleophiles. Inductive/electromeric effect, resonance, hyperconjugation."},
    {"subject": "Chemistry", "chapter": "Hydrocarbons", "topics": "Alkanes, Alkenes, Alkynes (Nomenclature, isomerism, preparation, Markownikoff's rule, Ozonolysis). Aromatic hydrocarbons (Benzene, electrophilic substitution)."},
    {"subject": "Chemistry", "chapter": "Organic Compounds Containing Halogens", "topics": "Preparation, properties, Nature of C-X bond, mechanisms of substitution reactions. Uses and environmental effects of freons, DDT."},
    {"subject": "Chemistry", "chapter": "Organic Compounds Containing Oxygen", "topics": "Alcohols, Phenols, Ethers: Preparation, acidic nature, substitution. Aldehydes and Ketones: Nucleophilic addition, oxidation/reduction, aldol condensation, Cannizzaro. Carboxylic Acids."},
    {"subject": "Chemistry", "chapter": "Organic Compounds Containing Nitrogen", "topics": "Amines: Nomenclature, classification, basic character. Diazonium Salts: Importance in synthesis."},
    {"subject": "Chemistry", "chapter": "Biomolecules", "topics": "Carbohydrates (monosaccharides, oligosaccharides). Proteins (amino acids, peptide bond, structures, denaturation, enzymes). Vitamins, Nucleic Acids (DNA, RNA)."},
    {"subject": "Chemistry", "chapter": "Principles Related to Practical Chemistry", "topics": "Detection of functional groups, preparation of inorganic/organic compounds, titrimetric exercises, qualitative salt analysis, Enthalpy of solution/neutralization."},

    # --- BIOLOGY ---
    {"subject": "Biology", "chapter": "Diversity in Living World", "topics": "Taxonomy, Binomial nomenclature, Five kingdom classification (Monera, Protista, Fungi, Plantae, Animalia), Viruses, Viroids, Lichens."},
    {"subject": "Biology", "chapter": "Structural Organisation in Animals and Plants", "topics": "Morphology and anatomy of flowering plants (root, stem, leaf, flower, fruit). Animal tissues, morphology/anatomy of insects (Frog)."},
    {"subject": "Biology", "chapter": "Cell Structure and Function", "topics": "Prokaryotic/eukaryotic cell, organelles (ER, Golgi, mitochondria, ribosomes, plastids, nucleus). Biomolecules (proteins, carbohydrates, lipids, enzymes). Cell cycle, mitosis, meiosis."},
    {"subject": "Biology", "chapter": "Plant Physiology", "topics": "Photosynthesis (light/dark reactions, C3, C4, photorespiration). Respiration (glycolysis, TCA cycle, ETS). Plant growth regulators (auxin, gibberellin, cytokinin, ethylene, ABA)."},
    {"subject": "Biology", "chapter": "Human Physiology", "topics": "Breathing/respiration, Body fluids/circulation (heart, ECG, double circulation), Excretory system (urine formation, osmoregulation), Locomotion (muscles, skeletal system), Neural control (CNS, PNS, nerve impulse), Chemical coordination (endocrine glands, hormones)."},
    {"subject": "Biology", "chapter": "Reproduction", "topics": "Sexual reproduction in flowering plants (pollination, double fertilization, endosperm, embryo). Human Reproduction (gametogenesis, menstrual cycle, fertilization, pregnancy). Reproductive health, birth control, IVF, STDs."},
    {"subject": "Biology", "chapter": "Genetics and Evolution", "topics": "Mendelian inheritance, co-dominance, multiple alleles, linkage, sex determination, genetic disorders. Molecular basis (DNA, RNA, replication, transcription, translation, human genome project). Evolution (origin of life, Darwin, Natural selection, Hardy-Weinberg)."},
    {"subject": "Biology", "chapter": "Biology and Human Welfare", "topics": "Health and Disease (Malaria, Typhoid, HIV, Cancer, immunology). Microbes in human welfare (food processing, industrial production, sewage treatment, biogas)."},
    {"subject": "Biology", "chapter": "Biotechnology and Its Applications", "topics": "Genetic engineering (Recombinant DNA technology). Application in health and agriculture (insulin, gene therapy, Bt crops, transgenic animals)."},
    {"subject": "Biology", "chapter": "Ecology and Environment", "topics": "Population interactions, Ecosystem (energy flow, pyramids), Biodiversity and conservation (hotspots, national parks, sanctuaries)."}
]

selected_topic = random.choice(syllabus)
subject = selected_topic["subject"]
chapter = selected_topic["chapter"]
topics = selected_topic["topics"] # <--- नवीन! (डिटेल सिलॅबस)

difficulties = ["Easy", "Medium", "Hard", "Advanced conceptual"]
question_types = ["Assertion-Reason", "Statement based", "Direct conceptual", "Numerical/Application based"]

selected_difficulty = random.choice(difficulties)
selected_type = random.choice(question_types)

print(f"आजचा विषय: {subject} - {chapter} | प्रकार: {selected_difficulty}, {selected_type}")

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

# ४. प्रश्न मागवणे (प्रॉम्प्टमध्ये डिटेल सिलॅबस 'Topics' जोडले आहेत)
url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={GEMINI_API_KEY}"
prompt = f"Generate 10 UNIQUE and {selected_difficulty} level '{selected_type}' multiple choice questions for NEET 2025 exam on the Subject: '{subject}' and Chapter: '{chapter}'. The questions MUST be strictly based ONLY on the following specific topics: {topics}. Make sure these are not the most common questions. Return ONLY a valid JSON array of objects. Keys must be exactly: 'question', 'optionA', 'optionB', 'optionC', 'optionD', 'correctOption', 'explanation'. The 'explanation' must be highly detailed. Do not use markdown tags."

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.8} # Temperature थोडे आणखी वाढवले आहे (नवीन प्रकारचे प्रश्न येण्यासाठी)
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
data = response.json()

# ५. गुगल शीटमध्ये डुप्लिकेट तपासून आणि वेळेसह सेव्ह करणे
if 'candidates' in data:
    try:
        text_response = data['candidates'][0]['content']['parts'][0]['text']
        text_response = text_response.replace('```json', '').replace('```', '').strip()
        questions = json.loads(text_response)

        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S")

        saved_count = 0
        duplicate_count = 0

        print("गुगल शीटमध्ये डेटा सेव्ह करत आहे...")
        for q in questions:
            question_text = q.get('question', '').strip()
            
            if question_text in existing_questions_list:
                duplicate_count += 1
                continue 

            q_id = f"{subject[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
            row = [
                q_id,
                subject,
                chapter,
                question_text,
                q.get('optionA', ''),
                q.get('optionB', ''),
                q.get('optionC', ''),
                q.get('optionD', ''),
                q.get('correctOption', ''),
                q.get('explanation', ''),
                timestamp 
            ]
            sheet.append_row(row)
            saved_count += 1
            
        print(f"यशस्वी! {saved_count} नवीन प्रश्न जोडले गेले. ({duplicate_count} डुप्लिकेट प्रश्न वगळले).")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
else:
    print("अंतिम API Error:", data)
