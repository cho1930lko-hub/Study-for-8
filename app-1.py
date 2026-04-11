import streamlit as st
from groq import Groq
from ddgs import DDGS
import random
import json
from datetime import datetime, timedelta
import time

# ========================================
# PAGE CONFIG
# ========================================
st.set_page_config(
    page_title="📚 StudyMate - La Martiniere Girls",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CUSTOM CSS - Student Friendly Colors
# ========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Nunito', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 50%, #f093fb15 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    }
    
    .main-header h1 { font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .main-header p { font-size: 1rem; opacity: 0.9; margin: 5px 0 0 0; }
    
    .subject-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        cursor: pointer;
        border: 3px solid transparent;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    
    .subject-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .english-card { border-color: #FF6B6B; background: linear-gradient(135deg, #fff5f5, #fff); }
    .maths-card   { border-color: #4ECDC4; background: linear-gradient(135deg, #f0fffe, #fff); }
    .physics-card { border-color: #45B7D1; background: linear-gradient(135deg, #f0f8ff, #fff); }
    .chemistry-card { border-color: #96CEB4; background: linear-gradient(135deg, #f0fff4, #fff); }
    .biology-card { border-color: #FFEAA7; background: linear-gradient(135deg, #fffdf0, #fff); }
    .history-card { border-color: #DDA0DD; background: linear-gradient(135deg, #fdf0ff, #fff); }
    .geography-card { border-color: #98D8C8; background: linear-gradient(135deg, #f0fffa, #fff); }
    
    .chapter-btn {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 18px;
        margin: 5px;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(102,126,234,0.3);
        transition: all 0.2s;
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border-left: 4px solid #667eea;
        border-radius: 0 12px 12px 0;
        padding: 15px 20px;
        margin: 10px 0;
    }
    
    .exercise-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        border-left: 5px solid #4ECDC4;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        margin: 10px 0;
    }
    
    .timetable-grid {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin: 2px;
    }
    
    .badge-icsc { background: #667eea22; color: #667eea; }
    .badge-class8 { background: #FF6B6B22; color: #FF6B6B; }
    
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-family: 'Nunito', sans-serif !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button:hover { transform: translateY(-2px) !important; }
    
    div[data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        margin-bottom: 8px !important;
    }
    
    .question-box {
        background: linear-gradient(135deg, #f8f9ff, #fff);
        border: 2px solid #667eea33;
        border-radius: 14px;
        padding: 18px;
        margin: 8px 0;
        font-size: 1.05rem;
    }
    
    .q-number {
        color: #667eea;
        font-weight: 800;
        font-size: 1.2rem;
    }
    
    .download-section {
        background: linear-gradient(135deg, #11998e22, #38ef7d22);
        border-radius: 14px;
        padding: 18px;
        border: 2px dashed #11998e;
        text-align: center;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATA: ICSC Class 8 Chapters
# ========================================
SUBJECTS = {
    "📖 English Grammar": {
        "icon": "📖",
        "color": "#FF6B6B",
        "card_class": "english-card",
        "has_numericals": False,
        "chapters": [
            "Parts of Speech", "Tenses", "Active & Passive Voice",
            "Direct & Indirect Speech", "Clauses & Phrases", "Determiners",
            "Modals", "Prepositions", "Conjunctions", "Question Tags",
            "Comprehension Skills", "Letter Writing", "Essay Writing",
            "Transformation of Sentences", "Punctuation & Spelling"
        ]
    },
    "➕ Mathematics": {
        "icon": "➕",
        "color": "#4ECDC4",
        "card_class": "maths-card",
        "has_numericals": True,
        "chapters": [
            "Rational Numbers", "Squares & Square Roots", "Cubes & Cube Roots",
            "Exponents & Powers", "Algebraic Expressions", "Linear Equations in One Variable",
            "Factorisation", "Understanding Quadrilaterals", "Practical Geometry",
            "Mensuration", "Data Handling & Graphs", "Introduction to Graphs",
            "Percentage & its Applications", "Profit, Loss & Discount", "Simple & Compound Interest",
            "Ratio & Proportion", "Geometry – Lines & Angles", "Congruence of Triangles"
        ]
    },
    "⚡ Physics": {
        "icon": "⚡",
        "color": "#45B7D1",
        "card_class": "physics-card",
        "has_numericals": True,
        "chapters": [
            "Force & Pressure", "Friction", "Sound", "Light – Reflection & Refraction",
            "Stars & The Solar System", "Motion & Measurement of Distances",
            "Electricity & Circuits", "Magnetic Effects of Current",
            "Heat", "Simple Machines", "Work, Energy & Power", "Gravitation"
        ]
    },
    "🧪 Chemistry": {
        "icon": "🧪",
        "color": "#96CEB4",
        "card_class": "chemistry-card",
        "has_numericals": True,
        "chapters": [
            "Matter in Our Surroundings", "Is Matter Around Us Pure?",
            "Atoms & Molecules", "Structure of Atom",
            "Chemical Reactions", "Acids, Bases & Salts",
            "Metals & Non-Metals", "Carbon & Its Compounds",
            "Combustion & Flame", "Materials – Metals & Non Metals",
            "Coal & Petroleum", "Water"
        ]
    },
    "🌿 Biology": {
        "icon": "🌿",
        "color": "#FFEAA7",
        "card_class": "biology-card",
        "has_numericals": False,
        "chapters": [
            "Cell – Structure & Functions", "Microorganisms: Friend & Foe",
            "Crop Production & Management", "Conservation of Plants & Animals",
            "Reproduction in Plants", "Reaching the Age of Adolescence",
            "Force & Pressure (Life Science)", "Pollution of Air & Water",
            "Food Production & Management", "Human Body Systems",
            "Animal Reproduction", "Heredity & Evolution (Intro)"
        ]
    },
    "🏛️ History": {
        "icon": "🏛️",
        "color": "#DDA0DD",
        "card_class": "history-card",
        "has_numericals": False,
        "chapters": [
            "How, When & Where (Sources of History)", "From Trade to Territory",
            "Ruling the Countryside", "Tribals, Dikus & the Vision of a Golden Age",
            "When People Rebel – 1857", "Civilising the 'Native', Educating the Nation",
            "Women, Caste & Reform", "The Making of the National Movement",
            "India After Independence", "The Mughal Empire",
            "Architecture as Power", "Paintings & Cultural Developments"
        ]
    },
    "🌍 Geography": {
        "icon": "🌍",
        "color": "#98D8C8",
        "card_class": "geography-card",
        "has_numericals": False,
        "chapters": [
            "Resources", "Land, Soil, Water, Natural Vegetation & Wildlife",
            "Agriculture", "Industries", "Human Resources",
            "The Earth & Its Movements", "Latitude & Longitude",
            "Major Landforms of the Earth", "Our Country India",
            "India – Climate, Vegetation & Wildlife",
            "Natural Disasters & Their Management",
            "Map Skills & Globe"
        ]
    }
}

# ========================================
# NUMERICAL QUESTION GENERATORS
# ========================================
def generate_maths_questions(chapter: str, level: str) -> list:
    """Generate 10 unique practice questions for Maths chapters"""
    questions_bank = {
        "Rational Numbers": {
            "basic": [
                ("Find: {a}/{b} + {c}/{d}", lambda: {"a": random.randint(1,9), "b": random.randint(2,10), "c": random.randint(1,9), "d": random.randint(2,10)}),
                ("Simplify: {a}/{b} × {c}/{d}", lambda: {"a": random.randint(2,12), "b": random.randint(2,12), "c": random.randint(2,12), "d": random.randint(2,12)}),
                ("Is {a}/{b} a rational number? Justify.", lambda: {"a": random.randint(-10,10), "b": random.choice([2,3,4,5,6,7,8,9,10])}),
            ],
            "advanced": [
                ("Find x: {a}/{b} × x = {c}/{d}", lambda: {"a": random.randint(1,6), "b": random.randint(2,8), "c": random.randint(1,6), "d": random.randint(2,8)}),
                ("Arrange in ascending order: {a}/7, {b}/7, {c}/7", lambda: {"a": random.randint(-5,5), "b": random.randint(-5,5), "c": random.randint(-5,5)}),
            ]
        },
        "Squares & Square Roots": {
            "basic": [
                ("Find √{n}", lambda: {"n": random.choice([4,9,16,25,36,49,64,81,100,121,144,169,196,225])}),
                ("Is {n} a perfect square?", lambda: {"n": random.randint(100,500)}),
                ("Find the square of {n}", lambda: {"n": random.randint(11,25)}),
            ],
            "advanced": [
                ("Using long division, find √{n}", lambda: {"n": random.choice([529,625,784,961,1024,1156,1296,1444,1600])}),
                ("Find the smallest number by which {n} must be multiplied to get a perfect square", lambda: {"n": random.choice([180,252,108,2028,1008,1620])}),
            ]
        },
        "Simple & Compound Interest": {
            "basic": [
                ("P=₹{p}, R={r}%, T={t} yr. Find SI.", lambda: {"p": random.randint(1,20)*500, "r": random.choice([5,6,8,10,12]), "t": random.randint(2,5)}),
                ("Find CI on ₹{p} at {r}% for {t} years (annually)", lambda: {"p": random.randint(2,10)*1000, "r": random.choice([5,8,10,12]), "t": random.randint(1,3)}),
            ],
            "advanced": [
                ("A sum doubles in {t} years at SI. Find rate.", lambda: {"t": random.choice([5,8,10,12,15,20])}),
                ("CI-SI on ₹{p} for 2 years at {r}% = ?", lambda: {"p": random.randint(5,20)*1000, "r": random.choice([5,8,10,12])}),
            ]
        }
    }
    
    # Generic question generator for chapters not in bank
    def generic_maths_questions(chapter, level, count=10):
        templates_basic = [
            f"Solve the following from {chapter}: Find the value of x when 3x + {random.randint(2,15)} = {random.randint(20,50)}",
            f"[{chapter}] A rectangle has length {random.randint(8,20)} cm and breadth {random.randint(4,10)} cm. Find its area and perimeter.",
            f"[{chapter}] Simplify: {random.randint(2,9)}² + {random.randint(2,9)}² - {random.randint(1,5)} × {random.randint(2,8)}",
            f"[{chapter}] If a = {random.randint(2,8)} and b = {random.randint(2,8)}, find (a+b)² and a²+b².",
            f"[{chapter}] Find the LCM and HCF of {random.randint(12,30)} and {random.randint(12,30)}.",
            f"[{chapter}] Solve: {random.randint(2,9)}x - {random.randint(5,20)} = {random.randint(10,40)}",
            f"[{chapter}] A train travels {random.randint(200,500)} km in {random.randint(2,8)} hours. Find its speed.",
            f"[{chapter}] Find {random.randint(15,40)}% of {random.randint(200,1000)}",
            f"[{chapter}] If {random.randint(10,30)} workers build a wall in {random.randint(5,20)} days, how many days for {random.randint(5,25)} workers?",
            f"[{chapter}] A circle has radius {random.randint(3,14)} cm. Find its area and circumference. (π = 3.14)",
        ]
        templates_advanced = [
            f"[{chapter} - Advanced] Prove that the sum of angles in a quadrilateral is 360°. Verify with a shape where angles are in ratio {random.randint(1,3)}:{random.randint(1,3)}:{random.randint(1,3)}:{random.randint(1,3)}",
            f"[{chapter} - Advanced] A shopkeeper buys {random.randint(50,200)} items at ₹{random.randint(20,100)} each and sells at {random.randint(10,40)}% profit. Find total profit.",
            f"[{chapter} - Advanced] Using factorisation, simplify: x² + {random.randint(3,12)}x + {random.randint(6,20)}",
            f"[{chapter} - Advanced] A tank can be filled by pipe A in {random.randint(4,15)} hours and pipe B in {random.randint(4,15)} hours. Together, when full?",
            f"[{chapter} - Advanced] In a class, {random.randint(30,60)}% are girls. If there are {random.randint(18,30)} girls, find total students and boys.",
            f"[{chapter} - Advanced] Find the area of trapezium with parallel sides {random.randint(8,20)} cm and {random.randint(4,12)} cm, height {random.randint(5,15)} cm.",
            f"[{chapter} - Advanced] Solve: (x + {random.randint(2,8)})(x - {random.randint(2,8)}) = x² - ?",
            f"[{chapter} - Advanced] The mean of {random.randint(5,8)} numbers is {random.randint(20,50)}. If one number {random.randint(10,40)} is removed, find new mean.",
            f"[{chapter} - Advanced] A cylinder has r={random.randint(3,10)} cm, h={random.randint(10,25)} cm. Find TSA and Volume.",
            f"[{chapter} - Advanced] Two numbers are in ratio {random.randint(2,5)}:{random.randint(2,5)}. Their LCM is {random.randint(60,300)}. Find the numbers.",
        ]
        pool = templates_advanced if level == "advanced" else templates_basic
        return random.sample(pool, min(10, len(pool)))
    
    if chapter in questions_bank:
        bank = questions_bank[chapter][level if level in questions_bank[chapter] else "basic"]
        questions = []
        used = []
        attempts = 0
        while len(questions) < 10 and attempts < 50:
            template, param_gen = random.choice(bank)
            params = param_gen()
            q = template.format(**params)
            if q not in used:
                questions.append(q)
                used.append(q)
            attempts += 1
        while len(questions) < 10:
            questions.append(generic_maths_questions(chapter, level, 1)[0])
        return questions[:10]
    else:
        return generic_maths_questions(chapter, level)

def generate_physics_questions(chapter: str, level: str) -> list:
    banks = {
        "Force & Pressure": {
            "basic": [
                f"A force of {random.randint(10,100)} N acts on area {random.randint(2,20)} m². Find pressure.",
                f"Convert {random.randint(1,10)} atm to Pa. (1 atm = 101325 Pa)",
                f"A block of mass {random.randint(2,20)} kg is pushed. Weight in N? (g=10 m/s²)",
                f"Two forces {random.randint(5,20)} N and {random.randint(5,20)} N act in same direction. Net force?",
                f"Area = {random.randint(5,50)} cm². Force = {random.randint(20,200)} N. Find pressure in Pa.",
                f"Water pressure at depth {random.randint(2,15)} m? (density=1000 kg/m³, g=10)",
                f"Mass = {random.randint(50,200)} g. Weight on moon? (g_moon = 1.6 m/s²)",
                f"A syringe has area {random.randint(2,8)} cm². Force {random.randint(10,50)} N applied. Pressure?",
                f"Balanced forces on a {random.randint(5,20)} kg book resting on table. Explain with values.",
                f"Net force on {random.randint(10,50)} kg object accelerating at {random.randint(2,8)} m/s²?",
            ],
            "advanced": [
                f"A hydraulic press has small piston area {random.randint(2,10)} cm² and large {random.randint(50,200)} cm². Force of {random.randint(20,100)} N gives output force?",
                f"Atmospheric pressure = 10⁵ Pa. Area of classroom window {random.randint(2,8)} m². Force on it?",
                f"A nail (tip area 0.01 cm²) hit with {random.randint(10,50)} N. Pressure at tip vs thumb (area {random.randint(5,15)} cm²)?",
                f"Two objects: m₁={random.randint(2,10)} kg, m₂={random.randint(2,10)} kg. Net force {random.randint(5,30)} N. Acceleration of system?",
                f"Pressure at bottom of {random.randint(5,20)} m column of mercury? (density=13600 kg/m³)",
                f"Sucker area {random.randint(10,50)} cm². Atmospheric pressure 10⁵ Pa. Max weight it can hold?",
                f"Dam wall depth {random.randint(10,30)} m. Water pressure at base? Compare with surface.",
                f"Explain why pressure in liquids increases with depth. Calculate for {random.randint(5,25)} m depth in oil (density 800 kg/m³).",
                f"A box {random.randint(20,60)} cm × {random.randint(20,60)} cm × {random.randint(20,60)} cm, mass {random.randint(5,30)} kg. Min & max pressure on floor?",
                f"Rocket ejects gas at {random.randint(500,2000)} m/s, mass flow {random.randint(10,50)} kg/s. Thrust force?",
            ]
        },
        "Sound": {
            "basic": [
                f"Speed of sound = 340 m/s. Wavelength if frequency = {random.randint(200,2000)} Hz?",
                f"A sound takes {random.randint(2,10)} s to reflect back. Distance of wall? (v=340 m/s)",
                f"Frequency {random.randint(50,500)} Hz, wavelength {random.choice([0.5,1,2,0.68,0.8])} m. Find speed.",
                f"Human ear range: 20 Hz to 20 kHz. Convert {random.randint(5,20)} kHz to Hz.",
                f"Echo heard after {random.randint(1,5)} s. Speed of sound 330 m/s. Distance?",
                f"Sound travels {random.randint(300,340)} m/s in air. Time to cross {random.randint(1,10)} km?",
                f"SONAR sends pulse, echo after {random.randint(2,10)} s. Depth? (v=1500 m/s in water)",
                f"A bat uses ultrasound at {random.randint(50000,100000)} Hz. Is this audible to humans? Why?",
                f"Amplitude doubles. What happens to loudness?",
                f"Time period = {random.choice([0.01, 0.02, 0.05, 0.1])} s. Find frequency."
            ]
        }
    }
    
    def generic_physics(chapter, level):
        Qs = [
            f"[{chapter}] A body travels {random.randint(100,1000)} m in {random.randint(10,100)} s. Find speed.",
            f"[{chapter}] Define {chapter.split()[0]} and give 2 real-life examples with numerical values.",
            f"[{chapter} - {level}] Mass = {random.randint(5,50)} kg, velocity = {random.randint(2,20)} m/s. KE = ?",
            f"[{chapter}] Work done = Force × Distance = {random.randint(10,100)} N × {random.randint(2,20)} m = ?",
            f"[{chapter}] Power = Work/Time. W={random.randint(500,5000)} J, t={random.randint(5,60)} s. P=?",
            f"[{chapter}] Height = {random.randint(5,50)} m, mass = {random.randint(2,20)} kg. PE = mgh (g=10) = ?",
            f"[{chapter}] Efficiency = {random.randint(60,95)}%. Input = {random.randint(1000,5000)} J. Output = ?",
            f"[{chapter}] Resistance = {random.randint(5,100)} Ω, Voltage = {random.randint(6,24)} V. Current (Ohm's law)?",
            f"[{chapter}] Frequency = {random.randint(50,1000)} Hz. Time period = ?",
            f"[{chapter} - {level}] Solve: A machine lifts {random.randint(100,500)} kg to height {random.randint(2,10)} m in {random.randint(10,60)} s. Power?",
        ]
        return random.sample(Qs, 10)
    
    if chapter in banks:
        pool = banks[chapter].get(level, banks[chapter]["basic"])
        return random.sample(pool, min(10, len(pool)))
    return generic_physics(chapter, level)

def generate_chemistry_questions(chapter: str, level: str) -> list:
    banks = {
        "Atoms & Molecules": {
            "basic": [
                f"Find molar mass of H₂O (H=1, O=16)",
                f"Molar mass of CO₂? (C=12, O=16)",
                f"Atoms in {random.randint(1,5)} mole of O₂? (Avogadro = 6.022×10²³)",
                f"Mass of {random.randint(2,10)} moles of NaCl? (Na=23, Cl=35.5)",
                f"Moles in {random.randint(18,180)} g of H₂O?",
                f"Molar mass of H₂SO₄? (H=1, S=32, O=16)",
                f"Molecules in {random.randint(1,5)} g of H₂? (H=1)",
                f"Moles of CO₂ in {random.randint(44,440)} g?",
                f"Atoms in {random.randint(23,230)} g of Na? (Na=23)",
                f"Empirical formula mass of CH₂O?",
            ],
            "advanced": [
                f"Find empirical formula: C={random.randint(40,60)}%, H={random.randint(6,10)}%, O=rest",
                f"Moles of H₂ needed to react with {random.randint(14,56)} g of N₂? (N₂+3H₂→2NH₃)",
                f"Molar mass of CaCO₃ (Ca=40,C=12,O=16). Mass of {random.randint(2,5)} moles?",
                f"Percentage of O in H₂SO₄? (H=1,S=32,O=16)",
                f"If {random.randint(2,10)} g of H₂ reacts with O₂, what volume of H₂O formed at STP?",
                f"Avogadro number = 6.022×10²³. Molecules in {random.randint(2,8)} moles of NH₃?",
                f"Law of conservation of mass: Reactants = {random.randint(10,50)}g. Products = {random.randint(5,49)}g + ?",
                f"Molecular formula given empirical CH₂ and molar mass {random.choice([42,56,70,84])} g/mol?",
                f"Compare masses: {random.randint(1,5)} mole of Fe vs {random.randint(1,5)} mole of Al (Fe=56, Al=27)",
                f"% composition of Na in NaCl (Na=23, Cl=35.5)?",
            ]
        }
    }
    
    def generic_chemistry(chapter, level):
        Qs = [
            f"[{chapter}] Balance: H₂ + O₂ → H₂O and find mole ratio",
            f"[{chapter}] Identify acid, base or salt: {random.choice(['HCl','NaOH','NaCl','H₂SO₄','Ca(OH)₂','CH₃COOH'])}. pH > or < 7?",
            f"[{chapter} - {level}] {random.randint(10,50)} g of reactant A and {random.randint(5,30)} g of B react. Product = {random.randint(10,60)} g. Leftover?",
            f"[{chapter}] Name the products when Zn + HCl react. Write balanced equation.",
            f"[{chapter}] Describe {chapter} with a chemical equation example from ICSC class 8.",
            f"[{chapter}] pH of solution = {random.randint(1,14)}. Acidic, basic or neutral?",
            f"[{chapter}] Rate of reaction doubles every 10°C rise. At {random.randint(30,50)}°C it's 1 unit. Rate at {random.randint(50,80)}°C?",
            f"[{chapter} - {level}] A solution has {random.randint(2,10)} g solute in {random.randint(50,200)} mL. Find concentration in g/L.",
            f"[{chapter}] Neutralisation: {random.randint(10,50)} mL of {random.choice([0.1,0.2,0.5,1])} M HCl neutralises ? mL of same M NaOH",
            f"[{chapter}] Identify the type of reaction (combination/decomposition/displacement/double displacement) and explain with {chapter}.",
        ]
        return random.sample(Qs, 10)
    
    if chapter in banks:
        pool = banks[chapter].get(level, banks[chapter]["basic"])
        return random.sample(pool, min(10, len(pool)))
    return generic_chemistry(chapter, level)

# ========================================
# TIMETABLE GENERATOR
# ========================================
def generate_timetable():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    subjects_list = list(SUBJECTS.keys())
    time_slots = ["7:00-8:00", "8:00-9:00", "9:00-10:00", "10:30-11:30", 
                  "11:30-12:30", "3:00-4:00", "4:00-5:00", "6:00-7:00"]
    
    timetable = {}
    for day in days:
        daily = []
        shuffled = random.sample(subjects_list, min(4, len(subjects_list)))
        slots = random.sample(time_slots, 4)
        for i, subj in enumerate(shuffled):
            daily.append({"time": slots[i], "subject": subj, "activity": random.choice(["Study", "Revision", "Practice Q", "Notes"])})
        timetable[day] = sorted(daily, key=lambda x: x["time"])
    return timetable

# ========================================
# SIDEBAR
# ========================================
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(135deg,#667eea,#764ba2); padding:15px; border-radius:12px; color:white; text-align:center; margin-bottom:15px;'>
        <h3 style='margin:0; font-size:1.1rem;'>🎓 La Martiniere Girls</h3>
        <p style='margin:4px 0 0 0; font-size:0.8rem; opacity:0.85;'>ICSC Board • Class 8</p>
    </div>
    """, unsafe_allow_html=True)

    st.header("⚙️ Settings")

    # ── Secrets से auto-load, नहीं तो sidebar input ──
    _secret_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    if _secret_key:
        groq_api_key = _secret_key
        st.session_state.groq_key = _secret_key
        st.success("🔐 API Key: Secrets से auto-load ✅")
    else:
        groq_api_key = st.text_input(
            "🔑 Groq API Key",
            type="password",
            value=st.session_state.get("groq_key", ""),
            help="Free key: https://console.groq.com/keys"
        )
        if groq_api_key:
            st.session_state.groq_key = groq_api_key
        st.info("💡 **Free Groq API**: console.groq.com/keys\nया Streamlit Secrets में डालो")
    
    st.divider()
    st.markdown("**📲 Telegram Channel**")
    telegram_link = st.text_input("Telegram Channel Link", placeholder="https://t.me/yourchannel", value=st.session_state.get("telegram_link",""))
    if telegram_link:
        st.session_state.telegram_link = telegram_link
        st.success("✅ Linked!")
    
    st.divider()
    st.markdown("**🌍 Search Region**")
    selected_region = "in-en"
    st.caption("India (in-en) - NCERT, PhysicsWallah, Vedantu")
    
    st.divider()
    if st.button("📅 Generate Study Timetable", use_container_width=True):
        st.session_state.show_timetable = True

# ========================================
# MAIN HEADER
# ========================================
st.markdown("""
<div class='main-header'>
    <h1>📚 StudyMate Dashboard</h1>
    <p>ICSC Class 8 • English Medium • La Martiniere Girls College</p>
    <span class='badge badge-icsc'>ICSC Board</span>
    <span class='badge badge-class8'>Class 8</span>
</div>
""", unsafe_allow_html=True)

# ========================================
# TIMETABLE DISPLAY
# ========================================
if st.session_state.get("show_timetable"):
    st.markdown("## 📅 Your Personalized Study Timetable")
    tt = generate_timetable()
    colors = {"Monday":"#FF6B6B","Tuesday":"#4ECDC4","Wednesday":"#45B7D1",
               "Thursday":"#96CEB4","Friday":"#FFEAA7","Saturday":"#DDA0DD"}
    cols = st.columns(3)
    for i, (day, sessions) in enumerate(tt.items()):
        with cols[i % 3]:
            color = colors.get(day, "#667eea")
            st.markdown(f"""<div style='background:white; border-radius:14px; padding:15px; border-top:4px solid {color}; box-shadow:0 3px 12px rgba(0,0,0,0.08); margin-bottom:12px;'>
                <h4 style='color:{color}; margin:0 0 10px 0;'>📆 {day}</h4>""", unsafe_allow_html=True)
            for s in sessions:
                subj_short = s['subject'].split()[-1]
                st.markdown(f"⏰ **{s['time']}** — {subj_short} _{s['activity']}_")
            st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate Timetable"):
            st.rerun()
    with col2:
        if st.button("❌ Close Timetable"):
            st.session_state.show_timetable = False
            st.rerun()
    st.divider()

# ========================================
# SUBJECT SELECTION
# ========================================
st.markdown("## 📚 Choose Your Subject")
st.markdown("किस subject पर पढ़ना है? नीचे click करो 👇")

cols = st.columns(4)
subject_keys = list(SUBJECTS.keys())

for i, subj_name in enumerate(subject_keys):
    with cols[i % 4]:
        subj = SUBJECTS[subj_name]
        if st.button(f"{subj['icon']} {subj_name.split(' ',1)[1]}", key=f"subj_{i}", use_container_width=True):
            st.session_state.selected_subject = subj_name
            st.session_state.selected_chapter = None
            st.session_state.exercise_questions = []
            st.rerun()

# ========================================
# CHAPTER DISPLAY
# ========================================
if st.session_state.get("selected_subject"):
    subj_name = st.session_state.selected_subject
    subj_data = SUBJECTS[subj_name]
    
    st.divider()
    st.markdown(f"### {subj_data['icon']} {subj_name} — Chapters (ICSC Class 8)")
    
    # Chapter buttons in rows of 4
    chapters = subj_data["chapters"]
    cols = st.columns(4)
    for i, chap in enumerate(chapters):
        with cols[i % 4]:
            btn_label = f"📌 {chap}"
            if st.button(btn_label, key=f"chap_{i}_{chap}", use_container_width=True):
                st.session_state.selected_chapter = chap
                st.session_state.exercise_questions = []
                st.session_state.exercise_level = None
                st.rerun()

# ========================================
# CHAPTER CONTENT
# ========================================
if st.session_state.get("selected_chapter") and st.session_state.get("selected_subject"):
    chapter = st.session_state.selected_chapter
    subj_name = st.session_state.selected_subject
    subj_data = SUBJECTS[subj_name]
    
    st.divider()
    st.markdown(f"## 📖 {chapter} — {subj_name}")
    
    # Main Tabs
    main_tab_labels = ["📝 Study Material", "🎥 Videos", "🖼️ Diagrams"]
    if subj_data["has_numericals"]:
        main_tab_labels.append("🧮 Practice Exercises")
    
    tabs = st.tabs(main_tab_labels)
    
    # ==================== TAB 1: STUDY MATERIAL ====================
    with tabs[0]:
        search_query = f"ICSC class 8 {subj_name.split(' ',1)[1]} {chapter} notes explanation India"
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### 🌐 Web Search Results")
            if st.button(f"🔍 Load Material for '{chapter}'", key="load_material"):
                with st.spinner("Searching web..."):
                    try:
                        ddgs = DDGS(timeout=15)
                        results = ddgs.text(
                            query=search_query,
                            region="in-en",
                            safesearch="moderate",
                            max_results=10
                        )
                        st.session_state.text_results = list(results)
                    except Exception as e:
                        st.error(f"Search error: {e}")
                        st.session_state.text_results = []
            
            if st.session_state.get("text_results"):
                for i, r in enumerate(st.session_state.text_results[:8], 1):
                    with st.expander(f"{i}. {r.get('title','')[:65]}..."):
                        st.write(r.get('body','')[:300])
                        link = r.get('href','#')
                        st.markdown(f"[🔗 Full Article]({link})")
                        
                        # Download option
                        content_text = f"Chapter: {chapter}\nSubject: {subj_name}\n\nTitle: {r.get('title','')}\n\n{r.get('body','')}\n\nSource: {link}"
                        st.download_button(
                            label="⬇️ Save as TXT",
                            data=content_text,
                            file_name=f"{chapter.replace(' ','_')}_{i}.txt",
                            mime="text/plain",
                            key=f"dl_{i}"
                        )
        
        with col2:
            st.markdown("### 🤖 AI Summary")
            if groq_api_key and st.button("✨ Get AI Summary", key="ai_summary"):
                with st.spinner("AI analysis..."):
                    try:
                        client = Groq(api_key=groq_api_key)
                        context = ""
                        if st.session_state.get("text_results"):
                            context = "\n".join([f"{r.get('title','')}: {r.get('body','')[:200]}" 
                                               for r in st.session_state.text_results[:5]])
                        
                        prompt = f"""You are an expert ICSC Class 8 teacher in India.
Topic: {chapter} (Subject: {subj_name.split(' ',1)[1]})

Give a student-friendly explanation:
1. 📌 Key Concepts (3-4 bullet points)
2. 📚 Important Definitions (2-3)
3. 💡 Memory Tips / Tricks
4. ⭐ Most Important Points for ICSC Exam
5. 🔗 Best Free Resources (NCERT, PhysicsWallah, Vedantu etc.)

Context from web: {context[:800]}

Keep it clear, simple and exam-focused for Class 8 students."""
                        
                        completion = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.6,
                            max_tokens=1200
                        )
                        ai_text = completion.choices[0].message.content
                        st.session_state.ai_summary = ai_text
                    except Exception as e:
                        st.error(f"AI Error: {e}")
            
            if st.session_state.get("ai_summary"):
                st.markdown(f"""<div class='info-box'>{st.session_state.ai_summary}</div>""", unsafe_allow_html=True)
                
                # Download AI Summary
                st.download_button(
                    "⬇️ Download AI Summary",
                    data=st.session_state.ai_summary,
                    file_name=f"AI_Summary_{chapter.replace(' ','_')}.txt",
                    mime="text/plain"
                )
            
            if not groq_api_key:
                st.warning("⚠️ Sidebar में Groq API Key डालो → AI Summary मिलेगी")
            
            # Telegram Share
            if st.session_state.get("telegram_link"):
                telegram_url = f"https://t.me/share/url?url={st.session_state.telegram_link}&text=Check out {chapter} notes!"
                st.markdown(f"[📲 Share on Telegram]({telegram_url})")
    
    # ==================== TAB 2: VIDEOS ====================
    with tabs[1]:
        st.markdown("### 🎥 Video Lessons")
        yt_query = f"ICSC class 8 {chapter} {subj_name.split(' ',1)[1]} explanation"
        
        if st.button("🔍 Find Videos", key="find_videos"):
            with st.spinner("Searching videos..."):
                try:
                    ddgs = DDGS(timeout=15)
                    vid_results = ddgs.videos(
                        query=yt_query,
                        region="in-en",
                        safesearch="moderate",
                        max_results=8
                    )
                    st.session_state.video_results = list(vid_results)
                except Exception as e:
                    st.error(f"Video search error: {e}")
                    st.session_state.video_results = []
        
        if st.session_state.get("video_results"):
            for vid in st.session_state.video_results:
                url = vid.get("content", "")
                title = vid.get("title", "Video")
                duration = vid.get("duration", "")
                publisher = vid.get("publisher", "")
                
                col_v1, col_v2 = st.columns([2, 3])
                with col_v1:
                    if url:
                        try:
                            st.video(url)
                        except:
                            st.markdown(f"[▶️ Watch Video]({url})")
                with col_v2:
                    st.markdown(f"**{title[:80]}**")
                    if duration:
                        st.caption(f"⏱️ Duration: {duration}")
                    if publisher:
                        st.caption(f"📺 {publisher}")
                    if url:
                        st.markdown(f"[🔗 Open on YouTube]({url})")
                st.divider()
        else:
            st.info(f"'Find Videos' button दबाओ → {chapter} के YouTube videos आएंगे")
    
    # ==================== TAB 3: IMAGES ====================
    with tabs[2]:
        st.markdown("### 🖼️ Diagrams & Images")
        img_query = f"ICSC class 8 {chapter} diagram textbook India"
        
        if st.button("🔍 Find Diagrams", key="find_images"):
            with st.spinner("Searching images..."):
                try:
                    ddgs = DDGS(timeout=15)
                    img_results = ddgs.images(
                        query=img_query,
                        region="in-en",
                        safesearch="moderate",
                        max_results=9
                    )
                    st.session_state.image_results = list(img_results)
                except Exception as e:
                    st.error(f"Image search error: {e}")
                    st.session_state.image_results = []
        
        if st.session_state.get("image_results"):
            img_cols = st.columns(3)
            for idx, img in enumerate(st.session_state.image_results):
                with img_cols[idx % 3]:
                    try:
                        st.image(img.get("image"), caption=img.get("title","")[:50], use_container_width=True)
                        st.markdown(f"[Source]({img.get('url','#')})")
                    except:
                        st.markdown(f"[🖼️ View Image]({img.get('image','#')})")
    
    # ==================== TAB 4: EXERCISES (Math/Physics/Chem) ====================
    if subj_data["has_numericals"] and len(tabs) > 3:
        with tabs[3]:
            st.markdown(f"### 🧮 Practice Exercises — {chapter}")
            st.markdown("**10 fresh questions** हर बार generate होंगे (same day में अलग-अलग questions)")
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                level_choice = st.radio(
                    "Exercise Level चुनो:",
                    ["🟢 Basic (Pre-Level)", "🔴 Advanced"],
                    key="exercise_level_radio"
                )
                level = "basic" if "Basic" in level_choice else "advanced"
            
            with col_e2:
                st.markdown(f"""<div class='info-box'>
                    <b>📌 {subj_name.split(' ',1)[1]} — {chapter}</b><br>
                    Level: {'Basic Practice' if level=='basic' else 'Advanced Challenge'}<br>
                    Questions: 10 (Fresh every time)
                </div>""", unsafe_allow_html=True)
            
            if st.button(f"🎲 Generate 10 Fresh Questions", key="gen_exercise", type="primary"):
                with st.spinner("Questions generate हो रहे हैं..."):
                    time.sleep(0.5)  # Small delay for randomness
                    
                    subj_short = subj_name.split()[1] if len(subj_name.split()) > 1 else subj_name
                    
                    if "Math" in subj_name or "math" in subj_name.lower():
                        questions = generate_maths_questions(chapter, level)
                    elif "Physics" in subj_name:
                        questions = generate_physics_questions(chapter, level)
                    elif "Chemistry" in subj_name:
                        questions = generate_chemistry_questions(chapter, level)
                    else:
                        questions = generate_maths_questions(chapter, level)  # fallback
                    
                    # Add timestamp to ensure uniqueness tracking
                    st.session_state.exercise_questions = questions
                    st.session_state.exercise_chapter = chapter
                    st.session_state.exercise_level = level
                    st.session_state.exercise_timestamp = datetime.now().strftime("%H:%M:%S")
            
            if st.session_state.get("exercise_questions") and st.session_state.get("exercise_chapter") == chapter:
                st.success(f"✅ Generated at {st.session_state.get('exercise_timestamp','')} — {'Basic' if level=='basic' else 'Advanced'} Level")
                
                # Display questions
                exercise_text = f"Chapter: {chapter}\nSubject: {subj_name}\nLevel: {level.capitalize()}\nGenerated: {st.session_state.get('exercise_timestamp','')}\n\n"
                exercise_text += "PRACTICE QUESTIONS\n" + "="*40 + "\n\n"
                
                for i, q in enumerate(st.session_state.exercise_questions, 1):
                    st.markdown(f"""<div class='question-box'>
                        <span class='q-number'>Q{i}.</span> {q}
                    </div>""", unsafe_allow_html=True)
                    exercise_text += f"Q{i}. {q}\n\n"
                
                exercise_text += "\n" + "="*40 + "\n[Space for answers below]\n"
                for i in range(1, 11):
                    exercise_text += f"\nQ{i}: _______________\n"
                
                st.divider()
                
                # Download & Share options
                col_d1, col_d2, col_d3 = st.columns(3)
                
                with col_d1:
                    st.download_button(
                        label="⬇️ Download as TXT",
                        data=exercise_text,
                        file_name=f"{chapter.replace(' ','_')}_{level}_exercises.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col_d2:
                    # Create CSV format for Google Sheets
                    csv_text = "Q No,Question,Answer\n"
                    for i, q in enumerate(st.session_state.exercise_questions, 1):
                        q_clean = q.replace('"','""').replace(',',';')
                        csv_text += f'{i},"{q_clean}",""\n'
                    
                    st.download_button(
                        label="📊 Download for Google Sheets",
                        data=csv_text,
                        file_name=f"{chapter.replace(' ','_')}_{level}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="CSV format → Google Sheets में import करो"
                    )
                
                with col_d3:
                    if st.session_state.get("telegram_link"):
                        first_3_q = "\n".join([f"Q{i+1}. {q[:80]}..." for i,q in enumerate(st.session_state.exercise_questions[:3])])
                        tg_msg = f"📚 {chapter} Practice Questions\n\n{first_3_q}\n\n...and 7 more! Full sheet downloaded ✅"
                        tg_url = f"https://t.me/share/url?url={st.session_state.telegram_link}&text={tg_msg}"
                        st.link_button("📲 Share on Telegram", tg_url, use_container_width=True)
                    else:
                        st.button("📲 Telegram (Set in Sidebar)", disabled=True, use_container_width=True)
                
                # AI Solutions hint
                if groq_api_key and st.button("💡 Get AI Hints/Solutions", key="ai_hints"):
                    with st.spinner("AI hints generate हो रहे हैं..."):
                        try:
                            client = Groq(api_key=groq_api_key)
                            q_text = "\n".join([f"Q{i+1}. {q}" for i,q in enumerate(st.session_state.exercise_questions)])
                            
                            hint_prompt = f"""You are an expert ICSC Class 8 {subj_name.split(' ',1)[1]} teacher.
Provide brief hints (not full solutions) for these questions so students can practice:

{q_text}

For each question:
- Give a 1-line hint/approach
- Mention relevant formula if applicable
- Don't give the full answer

Format: Q1. Hint: [hint]"""
                            
                            completion = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=[{"role":"user","content":hint_prompt}],
                                temperature=0.5,
                                max_tokens=1000
                            )
                            st.markdown("### 💡 AI Hints")
                            st.markdown(f"""<div class='info-box'>{completion.choices[0].message.content}</div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"AI Error: {e}")

# ========================================
# WELCOME SCREEN (no subject selected)
# ========================================
if not st.session_state.get("selected_subject"):
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class='subject-card english-card'>
            <h3>📖 English Grammar</h3>
            <p>Tenses, Voice, Speech, Comprehension & more</p>
            <small>15 Chapters</small>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class='subject-card history-card'>
            <h3>🏛️ History</h3>
            <p>ICSC Class 8 India & World History</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class='subject-card maths-card'>
            <h3>➕ Mathematics</h3>
            <p>Algebra, Geometry, Statistics & Numericals</p>
            <small>18 Chapters + Exercises</small>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class='subject-card geography-card'>
            <h3>🌍 Geography</h3>
            <p>India, World Geography, Resources</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""<div class='subject-card physics-card'>
            <h3>⚡ Physics</h3>
            <p>Force, Sound, Light, Electricity + Numericals</p>
            <small>12 Chapters + Exercises</small>
        </div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class='subject-card chemistry-card'>
            <h3>🧪 Chemistry</h3>
            <p>Atoms, Reactions, Acids & Numericals</p>
            <small>12 Chapters + Exercises</small>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg,#667eea15,#764ba215); border-radius:16px; padding:20px; margin-top:20px; text-align:center; border: 2px dashed #667eea44;'>
        <h3>🚀 How to Use</h3>
        <p>1️⃣ <b>Subject चुनो</b> → 2️⃣ <b>Chapter select करो</b> → 3️⃣ <b>Material, Videos & Exercises देखो</b></p>
        <p>💡 Maths, Physics, Chemistry में <b>Practice Exercises</b> भी generate होते हैं!</p>
        <p>📥 <b>Download</b> करो TXT या CSV में | 📲 <b>Telegram</b> से जोड़ो</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================
# SESSION STATE INIT
# ========================================
for key in ["selected_subject", "selected_chapter", "text_results", "video_results",
            "image_results", "exercise_questions", "ai_summary", "show_timetable",
            "exercise_chapter", "exercise_level", "exercise_timestamp"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "show_timetable" else False

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; font-size:0.85rem; padding:10px;'>
    Made with ❤️ for <b>La Martiniere Girls College</b> | ICSC Class 8 | 
    Powered by <b>Groq AI + ddgs</b> | Streamlit Cloud Ready 🚀<br>
    <small>📌 Free Resources: <a href='https://console.groq.com/keys' target='_blank'>Groq API</a> | 
    <a href='https://www.topperlearning.com' target='_blank'>TopperLearning</a> | 
    <a href='https://www.vedantu.com' target='_blank'>Vedantu</a></small>
</div>
""", unsafe_allow_html=True)
