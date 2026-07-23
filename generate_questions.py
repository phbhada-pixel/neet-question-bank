import os
import json
import ast
import requests
import random
import uuid
from datetime import datetime, timedelta
from collections import Counter 
from supabase import create_client, Client 

# ----------------- API KEYS & SECRETS -----------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# --- SUPABASE CREDENTIALS ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
TABLE_NAME = "NEET QUESTION BANK"

# ----------------- १. SUPABASE CONNECTION -----------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Supabase डेटाबेसमधून जुना डेटा वाचत आहे...")
try:
    chapters_response = supabase.table(TABLE_NAME).select("Chapter").execute()
    existing_chapters_list = [row['Chapter'] for row in chapters_response.data]

    questions_response = supabase.table(TABLE_NAME).select("Question").execute()
    existing_questions_list = [row['Question'] for row in questions_response.data]
    print("✅ जुना डेटा यशस्वीरित्या वाचला!")
except Exception as e:
    print(f"⚠️ Supabase Error (Fetch): {e}")
    existing_chapters_list = []
    existing_questions_list = []

# ----------------- २. NEET सिलॅबस -----------------
syllabus = [
    # --- PHYSICS ---
    {"subject": "Physics", "chapter": "Physics and Measurement", "topics": "Units of measurements, System of Units, SI Units, fundamental and derived units, least count, significant figures, Errors in measurements, Dimensions of Physics quantities, dimensional analysis."},
    {"subject": "Physics", "chapter": "Kinematics", "topics": "Frame of reference, motion in a straight line, Position-time graph, speed, velocity, Uniform and non-uniform motion, average speed, instantaneous velocity, uniformly accelerated motion, Scalars and Vectors, Relative Velocity, Motion in a plane, Projectile Motion, Uniform Circular Motion."},
    {"subject": "Physics", "chapter": "Laws of Motion", "topics": "Force and inertia, Newton's First, Second and Third Law of motion, Momentum, Impulses, Law of conservation of linear momentum, Equilibrium of concurrent forces, Static and Kinetic friction, rolling friction, Dynamics of uniform circular motion."},
    {"subject": "Physics", "chapter": "Work, Energy and Power", "topics": "Work done by a constant/variable force, kinetic and potential energies, work-energy theorem, power, Potential energy of spring, conservative and non-conservative forces, Elastic and inelastic collisions."},
    {"subject": "Physics", "chapter": "System of Particles and Rotational Motion", "topics": "Centre of mass, moment of a force, torque, angular momentum, conservation of angular momentum, Moment of inertia, radius of gyration, parallel and perpendicular axes theorems, Equilibrium of rigid bodies."},
    {"subject": "Physics", "chapter": "Gravitation", "topics": "Universal law of gravitation, Acceleration due to gravity, Kepler's law, Gravitational potential energy, Escape velocity, Motion of a satellite, orbital velocity, time period and energy of satellite."},
    {"subject": "Physics", "chapter": "Properties of Solids and Liquids", "topics": "Elastic behaviour, Stress-strain relationship, Hooke's Law, Young's modulus, Pascal's law, Viscosity, Stokes' law, terminal velocity, Bernoulli's principle, Surface energy and tension, Heat transfer (conduction, convection, radiation)."},
    {"subject": "Physics", "chapter": "Thermodynamics", "topics": "Thermal equilibrium, zeroth, first and second law of thermodynamics, Heat, work, internal energy, isothermal and adiabatic processes, reversible and irreversible processes."},
    {"subject": "Physics", "chapter": "Kinetic Theory of Gases", "topics": "Equation of state of a perfect gas, work done on compressing a gas, Kinetic interpretation of temperature, RMS speed, Degrees of freedom, Law of equipartition of energy, Mean free path."},
    {"subject": "Physics", "chapter": "Oscillations", "topics": "Periodic motion, time period, frequency, Simple harmonic motion (S.H.M.) and its equation, phase, restoring force, Simple pendulum."},
    {"subject": "Physics", "chapter": "Waves", "topics": "Wave motion, Longitudinal and transverse waves, speed of travelling wave, Principle of superposition of waves, Standing waves in strings and organ pipes, fundamental mode and harmonics, Beats."},
    {"subject": "Physics", "chapter": "Electrostatics", "topics": "Electric charges, Coulomb's law, Electric field, Electric dipole, Electric flux, Gauss's law, Electric potential, Equipotential surfaces, Conductors and insulators, Dielectrics and polarization, capacitors and capacitances, energy stored."},
    {"subject": "Physics", "chapter": "Current Electricity", "topics": "Electric current, Drift velocity, mobility, Ohm's law, Electrical resistance, V-I characteristics, Electrical energy and power, Series and parallel combinations of resistors, Kirchhoff's laws, Wheatstone bridge, Metre Bridge."},
    {"subject": "Physics", "chapter": "Magnetic Effects of Current and Magnetism", "topics": "Biot Savart law, Ampere's law, Force on a moving charge, Force on a current-carrying conductor, Torque experienced by a current loop, Moving coil galvanometer, Magnetic dipole, Para-, dia- and ferromagnetic substances."},
    {"subject": "Physics", "chapter": "Electromagnetic Induction and Alternating Currents", "topics": "Faraday's law, Induced emf, Lenz's Law, Eddy currents, Self and mutual inductance, Alternating currents, LCR series circuit, resonance, power in AC circuits, AC generator and transformer."},
    {"subject": "Physics", "chapter": "Electromagnetic Waves", "topics": "Displacement current, Electromagnetic waves characteristics, Transverse nature, Electromagnetic spectrum (radio waves, microwaves, IR, visible, UV, X-rays, Gamma rays)."},
    {"subject": "Physics", "chapter": "Optics (Ray Optics and Wave Optics)", "topics": "Reflection, refraction, spherical mirrors, lenses, Total internal reflection, Prism, Microscope and Telescope, Wave optics, Huygens' principle, Interference, Young's double-slit, Diffraction, Polarization."},
    {"subject": "Physics", "chapter": "Dual Nature of Matter and Radiation", "topics": "Dual nature of radiation, Photoelectric effect, Einstein's photoelectric equation, Matter waves, de Broglie relation."},
    {"subject": "Physics", "chapter": "Atoms and Nuclei", "topics": "Alpha-particle scattering experiment, Rutherford's model, Bohr model, hydrogen spectrum, Composition of nucleus, mass defect, binding energy per nucleon, nuclear fission, and fusion."},
    {"subject": "Physics", "chapter": "Electronic Devices (Semiconductor Electronics)", "topics": "Semiconductors, p-n junction diode in forward and reverse bias, LED, photodiode, solar cell, Zener diode, Logic gates (OR, AND, NOT, NAND, NOR)."},
    {"subject": "Physics", "chapter": "Experimental Skills", "topics": "Vernier calipers, Screw gauge, Simple Pendulum, Metre Scale, Young's modulus, Surface tension, Viscosity, Speed of sound, Specific heat capacity, Resistivity, Ohm's law, Focal length of mirrors/lenses."},

    # --- CHEMISTRY ---
    {"subject": "Chemistry", "chapter": "Some Basic Concepts of Chemistry", "topics": "Dalton's atomic theory, Atomic and molecular masses, mole concept, molar mass, empirical and molecular formulae, Chemical equations and stoichiometry."},
    {"subject": "Chemistry", "chapter": "Structure of Atom", "topics": "Bohr model, Dual nature of matter, de Broglie's relationship, Heisenberg uncertainty principle, Quantum mechanics, quantum numbers, shapes of s, p, and d orbitals, Aufbau principle, Pauli's exclusion principle and Hund's rule."},
    {"subject": "Chemistry", "chapter": "Classification of Elements and Periodicity in Properties", "topics": "Modern periodic law, s, p, d and f block elements, periodic trends in properties (atomic/ionic radii, ionization enthalpy, electron gain enthalpy, valency)."},
    {"subject": "Chemistry", "chapter": "Chemical Bonding and Molecular Structure", "topics": "Ionic and covalent bonds, Fajan's rule, dipole moment, VSEPR theory, Valence bond theory, hybridization, Resonance, Molecular Orbital Theory, Hydrogen bonding."},
    {"subject": "Chemistry", "chapter": "States of Matter", "topics": "Gaseous state, gas laws (Boyle's, Charles', Graham's law), ideal gas equation, kinetic molecular theory of gases, deviation from ideal behavior, liquefaction of gases."},
    {"subject": "Chemistry", "chapter": "Thermodynamics", "topics": "System and surroundings, First law of thermodynamics, enthalpy, Hess's law, Second law of thermodynamics, Spontaneity, Standard Gibbs energy change and equilibrium constant."},
    {"subject": "Chemistry", "chapter": "Equilibrium", "topics": "Dynamic equilibrium, Law of chemical equilibrium, equilibrium constants (Kp and Kc), Le Chatelier's principle, Ionic equilibrium, ionization of acids and bases, pH scale, common ion effect, buffer solutions."},
    {"subject": "Chemistry", "chapter": "Redox Reactions", "topics": "Electronic concepts of oxidation and reduction, oxidation number, balancing of redox reactions."},
    {"subject": "Chemistry", "chapter": "Hydrogen", "topics": "Position of hydrogen in periodic table, isotopes, preparation, properties and uses of hydrogen, hydrides, water, heavy water, hydrogen peroxide."},
    {"subject": "Chemistry", "chapter": "s-Block Elements", "topics": "Group 1 and Group 2 elements, general introduction, electronic configuration, occurrence, anomalous properties of first element, important compounds."},
    {"subject": "Chemistry", "chapter": "Some p-Block Elements", "topics": "Group 13 to Group 18 Elements, Electronic configuration, general trends in physical and chemical properties, unique behaviour of the first element in each group."},
    {"subject": "Chemistry", "chapter": "Organic Chemistry – Some Basic Principles and Techniques", "topics": "Tetravalency of carbon, Isomerism, IUPAC nomenclature, Homolytic and heterolytic fission, electrophiles, nucleophiles, Inductive effect, electromeric effect, resonance, hyperconjugation."},
    {"subject": "Chemistry", "chapter": "Hydrocarbons", "topics": "Alkanes (Conformations, halogenation), Alkenes (Geometrical isomerism, Markownikoff's rule, Ozonolysis), Alkynes (Acidic character, polymerization), Aromatic hydrocarbons (Benzene, electrophilic substitution)."},
    {"subject": "Chemistry", "chapter": "Environmental Chemistry", "topics": "Environmental pollution, air, water and soil pollution, chemical reactions in atmosphere, smog, major atmospheric pollutants, acid rain, ozone depletion, green chemistry."},
    {"subject": "Chemistry", "chapter": "Solutions", "topics": "Methods for expressing concentration (molality, molarity, mole fraction), Raoult's Law, Ideal and non-ideal solutions, Colligative properties, Determination of molecular mass, van't Hoff factor."},
    {"subject": "Chemistry", "chapter": "Electrochemistry", "topics": "Electrolytic and metallic conduction, Kohlrausch's law, Electrochemical cells, Nernst equation, Relationship between cell potential and Gibbs energy change, Dry cell, lead accumulator, Fuel cells."},
    {"subject": "Chemistry", "chapter": "Chemical Kinetics", "topics": "Rate of a chemical reaction, factors affecting rate, order and molecularity, differential and integral forms of zero and first-order reactions, Arrhenius theory, activation energy."},
    {"subject": "Chemistry", "chapter": "d- and f-Block Elements", "topics": "Transition Elements, electronic configuration, characteristics, ionization enthalpy, oxidation states, colour, magnetic properties, alloys, K2Cr2O7 and KMnO4, Lanthanoids and Actinoids."},
    {"subject": "Chemistry", "chapter": "Coordination Compounds", "topics": "Werner's theory, ligands, coordination number, IUPAC nomenclature, isomerism, Valence bond approach, Crystal field theory, Importance in qualitative analysis and biology."},
    {"subject": "Chemistry", "chapter": "Haloalkanes and Haloarenes", "topics": "General methods of preparation, properties, Nature of C-X bond, Mechanisms of substitution reactions, Environmental effects of chloroform, iodoform freons, and DDT."},
    {"subject": "Chemistry", "chapter": "Alcohols, Phenols and Ethers", "topics": "Alcohols: mechanism of dehydration. Phenols: Acidic nature, electrophilic substitution reactions (halogenation, nitration). Ethers: Structure and reactivity."},
    {"subject": "Chemistry", "chapter": "Aldehydes, Ketones and Carboxylic Acids", "topics": "Nature of carbonyl group, Nucleophilic addition, Grignard reagent, oxidation, reduction, aldol condensation, Cannizzaro reaction, Carboxylic Acids (Acidic strength)."},
    {"subject": "Chemistry", "chapter": "Amines", "topics": "Nomenclature, classification, basic character, identification of primary, secondary, and tertiary amines, Diazonium Salts and their synthetic importance."},
    {"subject": "Chemistry", "chapter": "Biomolecules", "topics": "Carbohydrates (glucose, fructose, sucrose), Proteins (amino acids, peptide bond, primary/secondary/tertiary structures, enzymes), Vitamins, Nucleic Acids (DNA and RNA)."},
    {"subject": "Chemistry", "chapter": "Polymers", "topics": "Classification of polymers, natural and synthetic polymers, methods of polymerization (addition and condensation), copolymerization, important polymers like polythene, nylon, polyesters, bakelite, rubber."},
    {"subject": "Chemistry", "chapter": "Chemistry in Everyday Life", "topics": "Chemicals in medicines (analgesics, tranquilizers, antiseptics, antibiotics), chemicals in food (preservatives, artificial sweetening agents), cleansing agents (soaps and detergents)."},

    # --- BOTANY ---
    {"subject": "Botany", "chapter": "The Living World", "topics": "What is living?, Biodiversity, Taxonomy & Systematics, Concept of species, taxonomical hierarchy, Binomial nomenclature."},
    {"subject": "Botany", "chapter": "Biological Classification", "topics": "Five kingdom classification, salient features and classification of Monera, Protista and Fungi, Lichens, Viruses and Viroids."},
    {"subject": "Botany", "chapter": "Plant Kingdom", "topics": "Classification of plants into major groups: Algae, Bryophytes, Pteridophytes, Gymnosperms (salient and distinguishing features)."},
    {"subject": "Botany", "chapter": "Morphology of Flowering Plants", "topics": "Morphology and modifications, Tissues, Anatomy and functions of root, stem, leaf, inflorescence, flower, fruit and seed. Families (malvaceae, Cruciferae, leguminoceae, etc)."},
    {"subject": "Botany", "chapter": "Anatomy of Flowering Plants", "topics": "Anatomy and functions of different parts of flowering plants, plant tissues, dicot and monocot stem, root and leaves, secondary growth."},
    {"subject": "Botany", "chapter": "Cell: The Unit of Life", "topics": "Cell theory, Prokaryotic and eukaryotic cell, Cell envelope, cell membrane, cell organelles (Endoplasmic reticulum, Golgi bodies, lysosomes, mitochondria, ribosomes, plastids), Nucleus."},
    {"subject": "Botany", "chapter": "Cell Cycle and Cell Division", "topics": "Cell cycle, mitosis, meiosis and their significance in cell division."},
    {"subject": "Botany", "chapter": "Transport in Plants", "topics": "Movement of water, gases and nutrients, cell to cell transport, Diffusion, active transport, plant-water relations, Imbibition, water potential, osmosis, plasmolysis, transpiration."},
    {"subject": "Botany", "chapter": "Mineral Nutrition", "topics": "Essential minerals, macro and micronutrients and their role, deficiency symptoms, mineral toxicity, elementary idea of hydroponics, nitrogen metabolism, nitrogen cycle."},
    {"subject": "Botany", "chapter": "Photosynthesis in Higher Plants", "topics": "Site of photosynthesis, pigments involved, Photochemical and biosynthetic phases, Cyclic and non cyclic photophosphorylation, Chemiosmotic hypothesis, Photorespiration, C3 and C4 pathways, Factors affecting photosynthesis."},
    {"subject": "Botany", "chapter": "Respiration in Plants", "topics": "Cellular respiration, glycolysis, fermentation (anaerobic), TCA cycle and electron transport system (aerobic), Energy relations (ATP generation), Amphibolic pathways, Respiratory quotient."},
    {"subject": "Botany", "chapter": "Plant Growth and Development", "topics": "Seed germination, Phases of Plant growth, Differentiation, dedifferentiation and redifferentiation, Growth regulators (auxin, gibberellin, cytokinin, ethylene, ABA)."},
    {"subject": "Botany", "chapter": "Reproduction in Organisms", "topics": "Reproduction in plants, asexual reproduction (sporulation, budding, fragmentations), vegetative propagation in plants."},
    {"subject": "Botany", "chapter": "Sexual Reproduction in Flowering Plants", "topics": "Flower structure, Development of male and female gametophytes, Pollination, Outbreeding devices, Pollen-Pistil interaction, Double fertilization, Post fertilization events (endosperm, embryo, seed, fruit), apomixis, parthenocarpy, polyembryony."},
    {"subject": "Botany", "chapter": "Principles of Inheritance and Variation", "topics": "Mendelian Inheritance, Deviations from Mendelism (Incomplete dominance, Co-dominance, Multiple alleles), Polygenic inheritance, Chromosome theory, Sex determination, Linkage and crossing over."},
    {"subject": "Botany", "chapter": "Molecular Basis of Inheritance", "topics": "DNA as genetic material, Structure of DNA and RNA, DNA packaging, DNA replication, Central dogma, Transcription, genetic code, translation, Gene expression and regulation (Lac Operon), Genome and HGP, DNA finger printing."},
    {"subject": "Botany", "chapter": "Strategies for Enhancement in Food Production", "topics": "Improvement in food production, Plant breeding, tissue culture, single cell protein, Biofortification."},
    {"subject": "Botany", "chapter": "Microbes in Human Welfare", "topics": "In household food processing, industrial production, sewage treatment, energy generation and as biocontrol agents and biofertilizers."},
    {"subject": "Botany", "chapter": "Organisms and Populations", "topics": "Organisms and environment, Population interactions (mutualism, competition, predation, parasitism), Population attributes (growth, birth rate and death rate, age distribution)."},
    {"subject": "Botany", "chapter": "Ecosystem", "topics": "Patterns, components, productivity and decomposition, Energy flow, Pyramids of number, biomass, energy."},
    {"subject": "Botany", "chapter": "Biodiversity and Conservation", "topics": "Concept of Biodiversity, Patterns and Importance of Biodiversity, Loss of Biodiversity, Biodiversity conservation, Hotspots, endangered organisms, extinction, Red Data Book, biosphere reserves, National parks, Sacred Groves."},
    {"subject": "Botany", "chapter": "Environmental Issues", "topics": "Air pollution and its control, Water pollution and its control, Agrochemicals and their effects, Solid waste management, Radioactive waste management, Greenhouse effect and climate change, Ozone depletion, Deforestation."},

    # --- ZOOLOGY ---
    {"subject": "Zoology", "chapter": "Animal Kingdom", "topics": "Salient features and classification of animals: non-chordate up to phyla level and chordate up to classes level."},
    {"subject": "Zoology", "chapter": "Structural Organisation in Animals", "topics": "Animal tissues, Morphology, anatomy and functions of different systems (digestive, circulatory, respiratory, nervous and reproductive) of an insect (Frog)."},
    {"subject": "Zoology", "chapter": "Biomolecules", "topics": "Chemical constituents of living cells, structure and function of proteins, carbohydrates, lipids, nucleic acids, Enzymes (properties, action, classification)."},
    {"subject": "Zoology", "chapter": "Digestion and Absorption", "topics": "Alimentary canal and digestive glands, Role of digestive enzymes and gastrointestinal hormones, Peristalsis, digestion, absorption and assimilation of proteins, carbohydrates and fats."},
    {"subject": "Zoology", "chapter": "Breathing and Exchange of Gases", "topics": "Respiratory system in humans, Mechanism of breathing and its regulation, Exchange of gases, transport of gases, Respiratory volumes, Disorders (Asthma, Emphysema, Occupational respiratory disorders)."},
    {"subject": "Zoology", "chapter": "Body Fluids and Circulation", "topics": "Composition of blood, blood groups, coagulation, Composition of lymph, Human circulatory system, Cardiac cycle, ECG, Double circulation, Regulation of cardiac activity, Disorders (Hypertension, CAD, Heart failure)."},
    {"subject": "Zoology", "chapter": "Excretory Products and Their Elimination", "topics": "Modes of excretion, Human excretory system (urine formation, Osmoregulation), Regulation of kidney function (Renin-angiotensin, ADH), Disorders (Uraemia, Renal failure, Renal calculi, Dialysis)."},
    {"subject": "Zoology", "chapter": "Locomotion and Movement", "topics": "Types of movement (ciliary, flagellar, muscular), Skeletal muscle, contractile proteins and muscle contraction, Skeletal system, Joints, Disorders (Myasthenia gravis, Tetany, Muscular dystrophy, Arthritis, Osteoporosis, Gout)."},
    {"subject": "Zoology", "chapter": "Neural Control and Coordination", "topics": "Neuron and nerves, Nervous system in humans (CNS, PNS, visceral), Generation and conduction of nerve impulse."},
    {"subject": "Zoology", "chapter": "Chemical Coordination and Integration", "topics": "Endocrine glands and hormones, Human endocrine system (Hypothalamus, Pituitary, Thyroid, Parathyroid, Adrenal, Pancreas, Gonads), Mechanism of hormone action, Disorders (Dwarfism, Acromegaly, Cretinism, goiter, diabetes)."},
    {"subject": "Zoology", "chapter": "Human Reproduction", "topics": "Male and female reproductive systems, Microscopic anatomy of testis and ovary, Gametogenesis (spermatogenesis & oogenesis), Menstrual cycle, Fertilisation, embryo development (blastocyst, implantation), Pregnancy and placenta, Parturition, Lactation."},
    {"subject": "Zoology", "chapter": "Reproductive Health", "topics": "Need for reproductive health, prevention of sexually transmitted diseases (STD), Birth control (Need and Methods, Contraception, MTP), Amniocentesis, Infertility and assisted reproductive technologies (IVF, ZIFT, GIFT)."},
    {"subject": "Zoology", "chapter": "Evolution", "topics": "Origin of life, Biological evolution, evidences (Paleontology, comparative anatomy, embryology, molecular), Darwin's contribution, Modern Synthetic theory, Mechanism of evolution (Mutation, Recombination, Natural Selection), Gene flow, Hardy-Weinberg principle, Human evolution."},
    {"subject": "Zoology", "chapter": "Human Health and Disease", "topics": "Pathogens, parasites causing human diseases (Malaria, Filariasis, Ascariasis, Typhoid, Pneumonia, common cold, ring worm, dengue), Basic concepts of immunology (vaccines), Cancer, HIV and AIDS, Adolescence, drug and alcohol abuse."},
    {"subject": "Zoology", "chapter": "Biotechnology: Principles and Processes", "topics": "Principles and process of Biotechnology, Genetic engineering (Recombinant DNA technology)."},
    {"subject": "Zoology", "chapter": "Biotechnology and Its Applications", "topics": "Application of Biotechnology in health and agriculture, Human insulin and vaccine production, gene therapy, Genetically modified organisms (Bt crops), Transgenic Animals, Biosafety issues (Biopiracy and patents)."}
]

# ----------------- ३. स्मार्ट ट्रॅकिंग (Covered vs Remaining) -----------------
chapter_counts = Counter(existing_chapters_list) 
TARGET_QUESTIONS_PER_CHAPTER = 100 

remaining_syllabus = []
for topic in syllabus:
    chap_name = topic["chapter"]
    current_count = chapter_counts.get(chap_name, 0)
    if current_count < TARGET_QUESTIONS_PER_CHAPTER:
        remaining_syllabus.append(topic)

print(f"📊 डॅशबोर्ड अपडेट: एकूण चॅप्टर्स: {len(syllabus)} | उरलेले चॅप्टर्स (Remaining): {len(remaining_syllabus)}")

if not remaining_syllabus:
    print("🎉 अभिनंदन! सर्व चॅप्टर्सचे टार्गेट पूर्ण झाले आहे!")
    exit()

weightage_map = {
    "Molecular Basis of Inheritance": 10, "Cell Cycle and Cell Division": 9, "Principles of Inheritance and Variation": 9,
    "Biotechnology: Principles and Processes": 10, "Biomolecules": 9, "Animal Kingdom": 9,
    "Current Electricity": 9, "Electrostatics": 7, "Aldehydes, Ketones and Carboxylic Acids": 8, "Chemical Bonding and Molecular Structure": 7
}

chapter_weights = []
for topic in remaining_syllabus:
    chap_name = topic["chapter"]
    subj_name = topic["subject"]
    if chap_name in weightage_map:
        chapter_weights.append(weightage_map[chap_name])
    else:
        chapter_weights.append(5 if subj_name == "Zoology" else (4 if subj_name == "Botany" else 3))

selected_topic = random.choices(remaining_syllabus, weights=chapter_weights, k=1)[0]
subject = selected_topic["subject"]
chapter = selected_topic["chapter"]
topics = selected_topic["topics"] 

current_q_count = chapter_counts.get(chapter, 0)
print(f"आजचा विषय: {subject} - {chapter} | (आतापर्यंत {current_q_count}/{TARGET_QUESTIONS_PER_CHAPTER} प्रश्न कव्हर झाले आहेत)")

# ----------------- ४. PRIMARY PROMPT (GEMINI) -----------------
prompt = f"""Generate exactly 20 UNIQUE multiple choice questions for NEET exam on Subject: '{subject}', Chapter: '{chapter}'. 
STRICTLY base all questions ONLY on topics: {topics}. 

Return ONLY a valid JSON array of objects. 
Keys must be exactly: 'question', 'optionA', 'optionB', 'optionC', 'optionD', 'correctOption', 'explanation', 'quality_score', 'smiles_code'.

RULES FOR SCORING & FORMAT:
- 'correctOption' MUST be strictly a SINGLE LETTER: "A", "B", "C", or "D". Do not write 'Option A' or the full answer text.
- 'quality_score' MUST be an object with key 'overall_score' (0-100).
- For MATHEMATICS/SCIENCE formulas use LaTeX (double-escaped like $\\\\frac{{a}}{{b}}$).
- CHEMISTRY STRUCTURES: If the question involves an organic chemistry structure that needs to be visualized, provide its correct SMILES code in the 'smiles_code' key (e.g., "CC(=O)C"). If no structure is needed, leave it as an empty string "".
- Output strictly valid JSON without markdown formatting.
"""

# ----------------- AI CALL FUNCTIONS -----------------
def call_gemini():
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    models_data = requests.get(list_url).json()
    valid_model_name = "models/gemini-1.5-flash" 
    
    if 'models' in models_data:
        for model in models_data['models']:
            if 'generateContent' in model.get('supportedGenerationMethods', []) and 'flash' in model['name']:
                valid_model_name = model['name']
                break

    url = f"https://generativelanguage.googleapis.com/v1beta/{valid_model_name}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.7}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    data = response.json()
    if 'candidates' in data:
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API Error: {data}")

# --- Helper Function for Clean Answer Standardizing (आता फक्त एकच अक्षर देईल) ---
def standardize_option(ans_str):
    if not ans_str:
        return ""
    # "Option A", "A", किंवा "Answer is A" मधील फक्त A, B, C, D शोधून काढणे
    ans = str(ans_str).upper().replace("OPTION", "").replace(" ", "").strip()
    if "A" in ans: return "A"
    if "B" in ans: return "B"
    if "C" in ans: return "C"
    if "D" in ans: return "D"
    return ans

# ----------------- VERIFIER 2: GROQ -----------------
def verify_with_groq(q_text, optA, optB, optC, optD):
    if not GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    verify_prompt = f"""You are an expert NEET Exam Verifier. Solve this question independently.
Question: {q_text}
A) {optA}
B) {optB}
C) {optC}
D) {optD}

Which single option is correct? Return ONLY a valid JSON object strictly using a single letter: {{"correctOption": "A"}} (or B/C/D). Do not write 'Option A' or the full answer text."""
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": verify_prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            content = data['choices'][0]['message']['content']
            parsed = json.loads(content)
            return standardize_option(parsed.get('correctOption', ''))
    except Exception as e:
        print(f"⚠️ Groq verification warning: {e}")
    return None

# ----------------- VERIFIER 3: GPT (OPENAI) -----------------
def verify_with_gpt(q_text, optA, optB, optC, optD):
    if not OPENAI_API_KEY:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    
    verify_prompt = f"""You are an expert NEET Exam Verifier. Solve this question independently.
Question: {q_text}
A) {optA}
B) {optB}
C) {optC}
D) {optD}

Which single option is correct? Return ONLY a valid JSON object strictly using a single letter: {{"correctOption": "A"}} (or B/C/D). Do not write 'Option A' or the full answer text."""
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": verify_prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            content = data['choices'][0]['message']['content']
            parsed = json.loads(content)
            return standardize_option(parsed.get('correctOption', ''))
    except Exception as e:
        print(f"⚠️ GPT verification warning: {e}")
    return None

# ----------------- ५. GENERATION & MULTI-AI VERIFICATION -----------------
text_response = None

try:
    print("१. Gemini कडून प्राथमिक प्रश्न जनरेट करत आहे...")
    text_response = call_gemini()
    print("✅ Gemini कडून प्रश्न प्राप्त झाले!")
except Exception as e:
    print(f"❌ Gemini generation error: {e}")
    exit()

if text_response:
    try:
        start_idx = text_response.find('[')
        end_idx = text_response.rfind(']')
        if start_idx != -1 and end_idx != -1:
            clean_string = text_response[start_idx:end_idx+1]
            questions = ast.literal_eval(clean_string)
        else:
            raise ValueError("AI च्या उत्तरात JSON Array सापडला नाही.")

        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S")

        saved_count = 0
        duplicate_count = 0
        consensus_failed_count = 0
        rows_to_add = [] 

        print("\n🔍 --- MULTI-AI VERIFICATION STARTED (Gemini ➔ Groq ➔ GPT) ---")
        
        for idx, q in enumerate(questions, 1):
            q_text = q.get('question', '').strip()
            optA = q.get('optionA', '').strip()
            optB = q.get('optionB', '').strip()
            optC = q.get('optionC', '').strip()
            optD = q.get('optionD', '').strip()
            
            gemini_ans = standardize_option(q.get('correctOption', ''))

            if not q_text or q_text in existing_questions_list:
                duplicate_count += 1
                continue 

            # Quality Score Check (> 85)
            scores = q.get('quality_score', {})
            overall = float(scores.get('overall_score', 0)) if isinstance(scores, dict) else 0
            if overall < 85 and overall != 0:
                print(f"❌ Q{idx}: Reject (Low Quality Score: {overall})")
                continue

            # --- VERIFICATION STEP 1: GROQ ---
            groq_ans = verify_with_groq(q_text, optA, optB, optC, optD)
            
            # --- VERIFICATION STEP 2: GPT ---
            gpt_ans = verify_with_gpt(q_text, optA, optB, optC, optD)

            # --- CONSENSUS VERIFIER (3/3 AGREE REQUIREMENT) ---
            if groq_ans and gpt_ans:
                if gemini_ans == groq_ans == gpt_ans:
                    print(f"✅ Q{idx}: [3/3 MATCH!] (Gemini: {gemini_ans} | Groq: {groq_ans} | GPT: {gpt_ans}) -> APPROVED")
                else:
                    print(f"❌ Q{idx}: [REJECTED - Disagreement] (Gemini: {gemini_ans} | Groq: {groq_ans} | GPT: {gpt_ans})")
                    consensus_failed_count += 1
                    continue
            elif groq_ans:
                if gemini_ans == groq_ans:
                    print(f"✅ Q{idx}: [2/2 MATCH!] (Gemini: {gemini_ans} | Groq: {groq_ans}) -> APPROVED")
                else:
                    print(f"❌ Q{idx}: [REJECTED] (Gemini: {gemini_ans} | Groq: {groq_ans})")
                    consensus_failed_count += 1
                    continue
            else:
                print(f"⚠️ Q{idx}: Skipped Multi-AI Check (Missing Verification Keys)")

            # --- PREPARE FOR SUPABASE (डिक्शनरी फॉरमॅट) ---
            q_id = f"{subject[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
            
            # तुमच्या CSV मधील कॉलम्सनुसार डेटा मॅपिंग
            row = {
                "Question ID": q_id,
                "Subject": subject,
                "Chapter": chapter,
                "Question": q_text,
                "Option A": optA,
                "Option B": optB,
                "Option C": optC,
                "Option D": optD,
                "Correct Option": gemini_ans,
                "Detailed Explanation": q.get('explanation', ''),
                "Smiles": q.get('smiles_code', ''), 
                "Timestamp": timestamp
            }
            rows_to_add.append(row)
            saved_count += 1

        # ----------------- ६. SAVING TO SUPABASE -----------------
        if len(rows_to_add) > 0:
            try:
                # Supabase टेबलमध्ये एकाच वेळी सर्व डेटा Insert करणे
                supabase.table(TABLE_NAME).insert(rows_to_add).execute()
                print(f"\n🎉 यशस्वी! {saved_count} १००% व्हेरीफाय झालेले प्रश्न Supabase मध्ये सेव्ह झाले. (रिजेक्टेड: {consensus_failed_count}, डुप्लिकेट: {duplicate_count}).")
            except Exception as e:
                print(f"\n❌ Supabase मध्ये सेव्ह करताना एरर आला: {e}")
        else:
            print(f"\n⚠️ कोणतेही नवीन प्रश्न सेव्ह झाले नाहीत. (रिजेक्ट: {consensus_failed_count}, डुप्लिकेट: {duplicate_count}).")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        print("\n--- Raw Response ---")
        print(text_response)
