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
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Quicksand:wght@400;500;600;700&display=swap');

    /* ── DAY MODE (default) ── */
    :root {
        --bg:        #f4f6ff;
        --card-bg:   #ffffff;
        --text:      #2d2d2d;
        --text-soft: #666;
        --border:    #e0e0f0;
        --accent1:   #667eea;
        --accent2:   #764ba2;
        --info-bg:   #667eea12;
        --q-bg:      #f8f9ff;
        --shadow:    rgba(102,126,234,0.12);
        --font-head: 'Baloo 2', cursive;
        --font-body: 'Quicksand', sans-serif;
    }

    /* ── NIGHT MODE ── */
    [data-theme="dark"] {
        --bg:        #0f1117;
        --card-bg:   #1a1d2e;
        --text:      #e8eaf6;
        --text-soft: #9fa8c7;
        --border:    #2e3150;
        --accent1:   #7c8ef7;
        --accent2:   #a78bfa;
        --info-bg:   #7c8ef720;
        --q-bg:      #1e2140;
        --shadow:    rgba(0,0,0,0.4);
        --font-head: 'Baloo 2', cursive;
        --font-body: 'Quicksand', sans-serif;
    }

    * { font-family: var(--font-body) !important; color: var(--text); }
    h1,h2,h3 { font-family: var(--font-head) !important; }

    .stApp { background: var(--bg) !important; }

    /* Sidebar dark */
    section[data-testid="stSidebar"] {
        background: var(--card-bg) !important;
        border-right: 1px solid var(--border) !important;
    }

    .main-header {
        background: linear-gradient(135deg, var(--accent1) 0%, var(--accent2) 100%);
        padding: 22px 30px; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 8px 30px var(--shadow);
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 800; margin: 0; color: white !important; }
    .main-header p  { font-size: 1rem; opacity: 0.9; margin: 5px 0 0 0; color: white !important; }

    .subject-card {
        background: var(--card-bg);
        border-radius: 16px; padding: 18px; text-align: center;
        border: 3px solid transparent;
        box-shadow: 0 4px 15px var(--shadow);
        transition: all 0.3s ease; margin-bottom: 10px;
    }
    .subject-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px var(--shadow); }

    .english-card    { border-color: #FF6B6B; }
    .maths-card      { border-color: #4ECDC4; }
    .physics-card    { border-color: #45B7D1; }
    .chemistry-card  { border-color: #96CEB4; }
    .biology-card    { border-color: #F6C90E; }
    .history-card    { border-color: #DDA0DD; }
    .geography-card  { border-color: #98D8C8; }
    .computer-card   { border-color: #FF9F43; }

    .info-box {
        background: var(--info-bg);
        border-left: 4px solid var(--accent1);
        border-radius: 0 12px 12px 0;
        padding: 15px 20px; margin: 10px 0;
    }

    .question-box {
        background: var(--q-bg);
        border: 2px solid var(--accent1)33;
        border-radius: 14px; padding: 18px;
        margin: 8px 0; font-size: 1.05rem;
    }
    .q-number { color: var(--accent1); font-weight: 800; font-size: 1.2rem; }

    .notes-box {
        background: var(--card-bg);
        border: 2px solid #F6C90E;
        border-radius: 14px; padding: 16px;
        margin: 8px 0;
        box-shadow: 0 3px 12px var(--shadow);
    }

    .mock-correct { background:#e8f8f0; border-left:4px solid #2ecc71; padding:10px 15px; border-radius:0 10px 10px 0; margin:5px 0; }
    .mock-wrong   { background:#fdecea; border-left:4px solid #e74c3c; padding:10px 15px; border-radius:0 10px 10px 0; margin:5px 0; }

    .badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; margin:2px; }
    .badge-icsc   { background: var(--accent1)22; color: var(--accent1); }
    .badge-class8 { background: #FF6B6B22; color: #FF6B6B; }

    .stButton>button {
        border-radius: 12px !important; font-weight: 700 !important;
        font-family: var(--font-body) !important; transition: all 0.2s !important;
    }
    .stButton>button:hover { transform: translateY(-2px) !important; }

    div[data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        margin-bottom: 8px !important;
        background: var(--card-bg) !important;
    }
    .timetable-grid { background: var(--card-bg); border-radius:16px; padding:20px; box-shadow:0 4px 20px var(--shadow); }
           [data-testid="stExpanderIcon"] { display: none !important; }
    
    /* यहाँ से नया जोड़ें */
    [data-testid="stExpander"] summary { font-size: 0 !important; }
    [data-testid="stExpander"] summary span { font-size: 16px !important; }
    /* यहाँ तक */

    .stExpander summary::before {
        content: "➤";
        font-size: 18px;
        margin-right: 10px;
        color: #764ba2;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# PASSWORD PROTECTION
# ========================================
def check_password():
    """Returns True if password is correct"""
    correct_password = st.secrets.get("APP_PASSWORD", "studymate123")

    if st.session_state.get("authenticated"):
        return True

    # Login Screen
    st.markdown("""
    <div style='max-width:420px; margin:80px auto 0 auto;'>
        <div style='background: linear-gradient(135deg,#667eea,#764ba2);
                    border-radius:24px; padding:40px 35px; text-align:center;
                    box-shadow: 0 20px 60px rgba(102,126,234,0.4);'>
            <div style='font-size:3.5rem; margin-bottom:10px;'>🎓</div>
            <h2 style='color:white; margin:0 0 5px 0; font-size:1.6rem;'>StudyMate Dashboard</h2>
            <p style='color:rgba(255,255,255,0.8); font-size:0.9rem; margin:0 0 30px 0;'>
                La Martiniere Girls College<br>ICSC Board • Class 8
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        password_input = st.text_input(
            "🔒 Password डालो",
            type="password",
            placeholder="अपना password यहाँ डालो...",
            key="password_input"
        )
        login_btn = st.button("🚀 Login करो", use_container_width=True, type="primary")

        if login_btn or (password_input and st.session_state.get("try_login")):
            if password_input == correct_password:
                st.session_state.authenticated = True
                st.session_state.try_login = False
                st.rerun()
            elif password_input:
                st.error("❌ गलत Password! दोबारा try करो।")
                st.session_state.try_login = False

        st.markdown("""
        <div style='text-align:center; margin-top:20px; color:#888; font-size:0.8rem;'>
            🔐 Only for authorized students
        </div>
        """, unsafe_allow_html=True)

    return False

if not check_password():
    st.stop()

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
    },
    "💻 Computer": {
        "icon": "💻",
        "color": "#FF9F43",
        "card_class": "computer-card",
        "has_numericals": False,
        "chapters": [
            "Introduction to Computers", "Hardware & Software",
            "Operating System", "Microsoft Word – Advanced",
            "Microsoft Excel – Spreadsheet Basics",
            "Microsoft PowerPoint – Presentations",
            "Internet & Email", "HTML Basics – Web Pages",
            "Scratch / Logo Programming", "Cyber Safety & Ethics",
            "Number Systems (Binary, Decimal, Octal, Hexadecimal)",
            "Data & Information", "Memory & Storage Devices",
            "Input & Output Devices", "Introduction to Networking"
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
        <h3 style='margin:0; font-size:1.1rem; font-family:"Baloo 2",cursive;'>🎓 La Martiniere Girls</h3>
        <p style='margin:4px 0 0 0; font-size:0.8rem; opacity:0.85;'>ICSC Board • Class 8</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Dark Mode Toggle ──
    dark_mode = st.toggle("🌙 Night Mode (Dark)", value=st.session_state.get("dark_mode", False))
    st.session_state.dark_mode = dark_mode
    if dark_mode:
        st.markdown("""<script>
        document.querySelector('[data-testid="stAppViewContainer"]').setAttribute('data-theme','dark');
        document.querySelector('body').setAttribute('data-theme','dark');
        </script>""", unsafe_allow_html=True)
        # Inject dark background via style override
        st.markdown("""<style>
        .stApp, section[data-testid="stSidebar"] { background-color: #0f1117 !important; }
        .stApp * { color: #e8eaf6 !important; }
        div[data-testid="stExpander"] { background: #1a1d2e !important; border-color: #2e3150 !important; }
        .question-box { background: #1e2140 !important; border-color: #7c8ef733 !important; }
        .info-box { background: #7c8ef720 !important; border-color: #7c8ef7 !important; }
        .subject-card { background: #1a1d2e !important; }
        .stButton>button { background: #1e2140 !important; }
        </style>""", unsafe_allow_html=True)
    else:
        st.markdown("""<style>
        .stApp { background: #f4f6ff !important; }
        </style>""", unsafe_allow_html=True)

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
    st.markdown("**📲 Telegram Channel** *(Optional)*")
    st.caption("अगर आपका Telegram channel है तो link डालो — notes share कर सकते हो। नहीं है तो खाली छोड़ दो।")
    telegram_link = st.text_input("Channel Link", placeholder="https://t.me/yourchannel", value=st.session_state.get("telegram_link",""), label_visibility="collapsed")
    if telegram_link:
        st.session_state.telegram_link = telegram_link
        st.success("✅ Linked!")

    st.divider()
    st.markdown("**🌍 Search Region**")
    selected_region = "in-en"
    st.caption("India (in-en) - NCERT, PhysicsWallah, Vedantu")

    st.divider()

    # ── Pomodoro Timer ──
    st.markdown("**⏱️ Pomodoro Study Timer**")
    pomo_mins = st.selectbox("Study time:", [25, 30, 45, 50], index=0, key="pomo_mins")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("▶️ Start", key="pomo_start", use_container_width=True):
            st.session_state.pomo_end = time.time() + pomo_mins * 60
            st.session_state.pomo_running = True
    with col_p2:
        if st.button("⏹ Stop", key="pomo_stop", use_container_width=True):
            st.session_state.pomo_running = False
            st.session_state.pomo_end = None

    if st.session_state.get("pomo_running") and st.session_state.get("pomo_end"):
        remaining = int(st.session_state.pomo_end - time.time())
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(f"""<div style='background:linear-gradient(135deg,#667eea,#764ba2);
                color:white; border-radius:12px; padding:12px; text-align:center; font-size:1.6rem; font-weight:800;
                font-family:"Baloo 2",cursive;'>⏱️ {mins:02d}:{secs:02d}</div>""", unsafe_allow_html=True)
            st.caption("Focus! 📚 Take a break after timer ends.")
        else:
            st.success("🎉 Time up! Take a 5-min break!")
            st.session_state.pomo_running = False

    st.divider()
    if st.button("📅 Generate Study Timetable", use_container_width=True):
        st.session_state.show_timetable = True

    st.divider()
    if st.button("🔓 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

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
    main_tab_labels = ["📝 Study Material", "🎥 Videos", "🖼️ Diagrams", "📓 My Notes"]
    if subj_data["has_numericals"]:
        main_tab_labels.append("🧮 Practice Exercises")
    main_tab_labels.append("🧠 Mock Test")

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
                    clean_title = r.get('title','').replace("_arrow_right", "").strip()
                    with st.expander(f"➤ {i}. {clean_title[:55]}..."):

                        st.write(r.get('body','')[:300])
                        link = r.get('href','#')
                        st.markdown(f"[🔗 Full Article]({link})")
                            
                            # Download option
                            content_text = f"Chapter: {chapter}\nSubject: {subj_name}\n\nTitle: {r.get('title','')}\n\n{r.get('body','')}\n\nSource: {link}"
                            
                            st.download_button(
                                label="⬇ Save as TXT",
                                data=content_text,
                                file_name=f"{chapter.replace(' ', '_')}_{i}.txt",
                                mime="text/plain",
                                key=f"dl_{i}"
                            )
        
        with col2:
            st.markdown("### 🤖 AI Summary")

            # Clear old summary if chapter changed
            if st.session_state.get("ai_summary_chapter") != chapter:
                st.session_state.ai_summary = None

            if not groq_api_key:
                st.warning("⚠️ Groq API Key नहीं मिली — Secrets check करो")
            else:
                if st.button("✨ Get AI Summary", key="ai_summary_btn"):
                    st.session_state.ai_summary = None
                    st.session_state.ai_summary_chapter = chapter
                    with st.spinner("🤖 AI is thinking..."):
                        try:
                            client = Groq(api_key=groq_api_key)
                            prompt = f"""You are an expert ICSC Class 8 English-medium teacher in India.
Topic: {chapter}
Subject: {subj_name.split(' ',1)[1]}

Write a clear, student-friendly study note ENTIRELY IN ENGLISH for Class 8 ICSC students:

1. 📌 Key Concepts (4-5 bullet points, simple language)
2. 📚 Important Definitions (2-3 definitions, easy to understand)
3. 💡 Memory Tips / Mnemonics (to remember easily)
4. ⭐ Most Important Points for ICSC Exam
5. 📝 2-3 Sample Exam Questions (with answers)

IMPORTANT: Write everything in ENGLISH ONLY. Simple, clear, exam-focused."""

                            completion = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.7,
                                max_tokens=1500
                            )
                            st.session_state.ai_summary = completion.choices[0].message.content
                            st.session_state.ai_summary_chapter = chapter
                        except Exception as e:
                            st.error(f"❌ Groq Error: {str(e)}")
                            st.info("💡 API key सही है? console.groq.com/keys पर check करो")

            if st.session_state.get("ai_summary") and st.session_state.get("ai_summary_chapter") == chapter:
                st.markdown(
                    f"<div class='info-box' style='white-space:pre-wrap;'>{st.session_state.ai_summary}</div>",
                    unsafe_allow_html=True
                )
                st.download_button(
                    "⬇️ Download AI Summary",
                    data=st.session_state.ai_summary,
                    file_name=f"AI_Summary_{chapter.replace(' ','_')}.txt",
                    mime="text/plain",
                    key="dl_ai_summary"
                )
            
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

    # ==================== TAB 4: MY NOTES PAD ====================
    with tabs[3]:
        st.markdown("### 📓 My Personal Notes")
        st.caption("यहाँ अपने notes लिखो — हर chapter के लिए अलग save रहेंगे")

        note_key = f"note_{subj_name}_{chapter}".replace(" ","_")

        existing_note = st.session_state.get(note_key, "")
        user_note = st.text_area(
            f"✏️ Notes for: {chapter}",
            value=existing_note,
            height=280,
            placeholder="यहाँ लिखो...\n• Key points\n• Formulas\n• Things to remember\n• Questions to ask teacher",
            key=f"textarea_{note_key}"
        )

        col_n1, col_n2, col_n3 = st.columns(3)
        with col_n1:
            if st.button("💾 Save Notes", key="save_note", use_container_width=True):
                st.session_state[note_key] = user_note
                st.success("✅ Saved!")

        with col_n2:
            if user_note:
                note_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>My Notes – {chapter}</title>
<style>
body {{ font-family:'Segoe UI',sans-serif; max-width:750px; margin:40px auto; padding:25px; color:#333; line-height:1.8; }}
.header {{ background:linear-gradient(135deg,#F6C90E,#f39c12); color:white; padding:18px 24px; border-radius:12px; margin-bottom:22px; }}
.header h1 {{ margin:0; font-size:1.4rem; color:white; }}
.header p  {{ margin:4px 0 0 0; opacity:0.85; font-size:0.85rem; }}
.notes {{ background:#fffef0; border:2px solid #F6C90E; border-radius:12px; padding:22px; white-space:pre-wrap; font-size:1rem; }}
.footer {{ margin-top:25px; color:#aaa; font-size:0.75rem; text-align:center; }}
</style></head><body>
<div class="header">
  <h1>📓 My Notes — {chapter}</h1>
  <p>Subject: {subj_name.split(' ',1)[1]} | ICSC Class 8 | La Martiniere Girls</p>
</div>
<div class="notes">{user_note}</div>
<div class="footer">Saved on {datetime.now().strftime("%d %b %Y, %I:%M %p")} | StudyMate</div>
</body></html>"""
                st.download_button(
                    "⬇️ Download Notes (HTML)",
                    data=note_html,
                    file_name=f"Notes_{chapter.replace(' ','_')}.html",
                    mime="text/html",
                    use_container_width=True,
                    key="dl_note"
                )

        with col_n3:
            if st.button("🗑️ Clear Notes", key="clear_note", use_container_width=True):
                st.session_state[note_key] = ""
                st.rerun()

        # Show all saved notes count
        saved = [k for k in st.session_state if k.startswith("note_") and st.session_state[k]]
        if saved:
            st.caption(f"📌 आपके पास कुल {len(saved)} chapters के notes saved हैं इस session में")

    # ==================== TAB 5: EXERCISES (Math/Physics/Chem) ====================
    if subj_data["has_numericals"]:
        ex_tab_idx = 4
        with tabs[ex_tab_idx]:
            st.markdown(f"### 🧮 Practice Exercises — {chapter}")

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                level_choice = st.radio(
                    "Exercise Level चुनो:",
                    ["🟢 Basic (Pre-Level)", "🔴 Advanced"],
                    key="exercise_level_radio"
                )
                level = "basic" if "Basic" in level_choice else "advanced"
            with col_e2:
                gen_mode = st.radio(
                    "Questions कैसे बनाएं?",
                    ["🤖 AI से (Groq — Best Quality)", "⚡ Instant (Local Generator)"],
                    key="gen_mode_radio"
                )

            st.markdown(f"""<div class='info-box'>
                <b>📌 {subj_name.split(' ',1)[1]} — {chapter}</b> &nbsp;|&nbsp;
                Level: <b>{'Basic' if level=='basic' else 'Advanced'}</b> &nbsp;|&nbsp;
                हर बार 10 अलग-अलग fresh questions
            </div>""", unsafe_allow_html=True)

            if st.button("🎲 Generate 10 Fresh Questions", key="gen_exercise", type="primary"):
                st.session_state.exercise_questions = []
                st.session_state.exercise_chapter = chapter
                st.session_state.exercise_level = level
                st.session_state.exercise_timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.exercise_hints = None

                def local_questions():
                    if "Math" in subj_name:
                        return generate_maths_questions(chapter, level)
                    elif "Physics" in subj_name:
                        return generate_physics_questions(chapter, level)
                    else:
                        return generate_chemistry_questions(chapter, level)

                if "AI" in gen_mode and groq_api_key:
                    with st.spinner("🤖 AI नए सवाल बना रहा है... (5-10 sec)"):
                        try:
                            client = Groq(api_key=groq_api_key)
                            level_desc = (
                                "basic numerical problems (straightforward, one-step)"
                                if level == "basic"
                                else "advanced numerical problems (multi-step, challenging)"
                            )
                            prompt = f"""You are an expert ICSC Class 8 {subj_name.split(' ',1)[1]} teacher in India.

Generate EXACTLY 10 {level_desc} for chapter: "{chapter}"

STRICT RULES:
- Every question MUST have specific numbers/values (e.g. 45N, ₹500, 20cm)
- Numerical/calculation based only — NO theory questions
- All 10 must be different from each other
- ICSC Class 8 syllabus appropriate
- Use proper units (m, cm, kg, N, ₹, Hz, mol, etc.)

OUTPUT FORMAT — only a numbered list, nothing else:
1. [question]
2. [question]
3. [question]
4. [question]
5. [question]
6. [question]
7. [question]
8. [question]
9. [question]
10. [question]"""

                            completion = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.95,
                                max_tokens=1600
                            )
                            raw = completion.choices[0].message.content.strip()
                            lines = [l.strip() for l in raw.split('\n') if l.strip()]
                            questions = []
                            for line in lines:
                                if line and line[0].isdigit() and '.' in line[:3]:
                                    q = line.split('.', 1)[1].strip()
                                    if len(q) > 10:
                                        questions.append(q)
                            if len(questions) >= 5:
                                st.session_state.exercise_questions = questions[:10]
                            else:
                                st.warning("⚠️ AI response ठीक नहीं आया — Local generator से दे रहे हैं")
                                st.session_state.exercise_questions = local_questions()
                        except Exception as e:
                            st.error(f"❌ Groq Error: {str(e)}")
                            st.session_state.exercise_questions = local_questions()
                else:
                    with st.spinner("⚡ Questions तैयार हो रहे हैं..."):
                        time.sleep(0.3)
                        st.session_state.exercise_questions = local_questions()

            # ── Show Questions ──
            if st.session_state.get("exercise_questions") and st.session_state.get("exercise_chapter") == chapter:
                questions = st.session_state.exercise_questions
                ts = st.session_state.get("exercise_timestamp", "")
                lv = st.session_state.get("exercise_level", level)
                st.success(f"✅ {len(questions)} Questions ready! [{lv.capitalize()} Level — {ts}]")

                exercise_text = f"Chapter: {chapter}\nSubject: {subj_name}\nLevel: {lv.capitalize()}\nTime: {ts}\n\n"
                exercise_text += "PRACTICE QUESTIONS\n" + "="*40 + "\n\n"

                for i, q in enumerate(questions, 1):
                    st.markdown(
                        f"<div class='question-box'><span class='q-number'>Q{i}.</span> {q}</div>",
                        unsafe_allow_html=True
                    )
                    exercise_text += f"Q{i}. {q}\n\n"

                exercise_text += "\n" + "="*40 + "\nANSWER SPACE\n"
                for i in range(1, len(questions)+1):
                    exercise_text += f"\nQ{i}: _______________________________________________\n"

                st.divider()

                # ── Hints button ──
                if groq_api_key:
                    if st.button("💡 Show AI Hints + Step-by-Step Answers", key="ai_hints_btn"):
                        st.session_state.exercise_hints = None
                        with st.spinner("AI is solving step-by-step..."):
                            try:
                                client = Groq(api_key=groq_api_key)
                                q_text = "\n".join([f"Q{i+1}. {q}" for i, q in enumerate(questions)])
                                hint_prompt = f"""You are an ICSC Class 8 {subj_name.split(' ',1)[1]} teacher.
Solve these numerical problems with clear step-by-step working. Write ENTIRELY IN ENGLISH.

{q_text}

Format for each question:
Q1. Formula: [formula used]
    Working: [step by step calculation]
    Answer: [final answer with unit]

Be clear and concise. Show all steps. English only."""
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": hint_prompt}],
                                    temperature=0.3,
                                    max_tokens=2000
                                )
                                st.session_state.exercise_hints = completion.choices[0].message.content
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

                if st.session_state.get("exercise_hints"):
                    st.markdown("### 💡 AI Hints & Step-by-Step Solutions")
                    st.markdown(
                        f"<div class='info-box' style='white-space:pre-wrap; font-size:0.9rem;'>{st.session_state.exercise_hints}</div>",
                        unsafe_allow_html=True
                    )
                    exercise_text += "\n\nAI HINTS & SOLUTIONS\n" + "="*40 + "\n" + (st.session_state.exercise_hints or "")

                st.divider()

                # ── Download & Share ──
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    st.download_button(
                        label="⬇️ Download TXT",
                        data=exercise_text,
                        file_name=f"{chapter.replace(' ','_')}_{lv}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="dl_txt_ex"
                    )
                with col_d2:
                    csv_text = "Q No,Question,Answer\n"
                    for i, q in enumerate(questions, 1):
                        q_clean = q.replace('"', '""').replace(',', ';')
                        csv_text += f'{i},"{q_clean}",""\n'
                    st.download_button(
                        label="📊 Google Sheets CSV",
                        data=csv_text,
                        file_name=f"{chapter.replace(' ','_')}_{lv}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Download → Google Sheets में import करो",
                        key="dl_csv_ex"
                    )
                with col_d3:
                    if st.session_state.get("telegram_link"):
                        preview = "\n".join([f"Q{i+1}. {q[:65]}..." for i, q in enumerate(questions[:3])])
                        tg_msg = f"📚 {chapter} — {lv.capitalize()} Practice\n\n{preview}\n\n...और 7 सवाल! ✅"
                        tg_url = f"https://t.me/share/url?url={st.session_state.telegram_link}&text={tg_msg}"
                        st.link_button("📲 Telegram Share", tg_url, use_container_width=True)
                    else:
                        st.button("📲 Telegram (Sidebar में set करो)", disabled=True, use_container_width=True)

    # ==================== LAST TAB: MOCK TEST ====================
    mock_tab_idx = 5 if subj_data["has_numericals"] else 4
    with tabs[mock_tab_idx]:
        st.markdown("### 🧠 Mock Test — MCQ")
        st.caption(f"AI {chapter} पर 10 MCQ questions बनाएगा — Time limit के साथ | Score भी मिलेगा!")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mock_time = st.selectbox("⏱️ Time Limit:", [5, 10, 15, 20], index=1, key="mock_time_sel")
        with col_m2:
            mock_diff = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard"], index=1, key="mock_diff")

        if st.button("🎯 Start Mock Test", key="start_mock", type="primary"):
            if not groq_api_key:
                st.error("❌ Groq API Key चाहिए Mock Test के लिए!")
            else:
                st.session_state.mock_questions = None
                st.session_state.mock_answers = {}
                st.session_state.mock_submitted = False
                st.session_state.mock_start_time = time.time()
                st.session_state.mock_time_limit = mock_time * 60

                with st.spinner("🤖 AI MCQ questions बना रहा है..."):
                    try:
                        client = Groq(api_key=groq_api_key)
                        mock_prompt = f"""You are an ICSC Class 8 {subj_name.split(' ',1)[1]} teacher creating a mock test.

Chapter: {chapter}
Difficulty: {mock_diff}

Generate EXACTLY 10 MCQ questions. Respond ONLY with valid JSON, no extra text.

Format:
[
  {{
    "q": "Question text here?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "answer": "A",
    "explanation": "Brief explanation why A is correct."
  }}
]

Rules:
- Questions must be from {chapter} only
- All in English
- One clearly correct answer
- Plausible wrong options
- Difficulty: {mock_diff}
- Return ONLY the JSON array, nothing else"""

                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": mock_prompt}],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        raw = completion.choices[0].message.content.strip()
                        # Clean JSON
                        raw = raw.replace("```json","").replace("```","").strip()
                        import json
                        mcqs = json.loads(raw)
                        st.session_state.mock_questions = mcqs[:10]
                    except Exception as e:
                        st.error(f"❌ Error generating test: {str(e)}")

        # ── Show Mock Test ──
        if st.session_state.get("mock_questions") and not st.session_state.get("mock_submitted"):
            mcqs = st.session_state.mock_questions

            # Timer display
            if st.session_state.get("mock_start_time"):
                elapsed = time.time() - st.session_state.mock_start_time
                limit   = st.session_state.get("mock_time_limit", 600)
                left    = max(0, int(limit - elapsed))
                ml, ms  = divmod(left, 60)
                color   = "#e74c3c" if left < 60 else "#2ecc71"
                st.markdown(f"""<div style='background:{color}; color:white; border-radius:10px;
                    padding:10px; text-align:center; font-size:1.4rem; font-weight:800;
                    font-family:"Baloo 2",cursive; margin-bottom:15px;'>
                    ⏱️ Time Left: {ml:02d}:{ms:02d}</div>""", unsafe_allow_html=True)
                if left == 0:
                    st.session_state.mock_submitted = True
                    st.rerun()

            st.markdown("---")
            for i, mcq in enumerate(mcqs):
                st.markdown(f"<div class='question-box'><span class='q-number'>Q{i+1}.</span> {mcq.get('q','')}</div>",
                    unsafe_allow_html=True)
                choice = st.radio(
                    f"Q{i+1}",
                    mcq.get("options", []),
                    key=f"mock_q_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.mock_answers[i] = choice[0] if choice else ""

            st.divider()
            if st.button("✅ Submit Test", key="submit_mock", type="primary", use_container_width=True):
                st.session_state.mock_submitted = True
                st.rerun()

        # ── Show Results ──
        if st.session_state.get("mock_submitted") and st.session_state.get("mock_questions"):
            mcqs    = st.session_state.mock_questions
            answers = st.session_state.get("mock_answers", {})
            score   = 0

            st.markdown("## 📊 Your Result")

            for i, mcq in enumerate(mcqs):
                user_ans    = answers.get(i, "")
                correct_ans = mcq.get("answer", "").strip().upper()
                is_correct  = user_ans.strip().upper().startswith(correct_ans)
                if is_correct:
                    score += 1
                    st.markdown(f"""<div class='mock-correct'>
                        ✅ <b>Q{i+1}.</b> {mcq.get('q','')}<br>
                        Your answer: <b>{user_ans}</b> — Correct! 🎉<br>
                        <small>{mcq.get('explanation','')}</small>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class='mock-wrong'>
                        ❌ <b>Q{i+1}.</b> {mcq.get('q','')}<br>
                        Your answer: <b>{user_ans}</b> | Correct: <b>{correct_ans}</b><br>
                        <small>{mcq.get('explanation','')}</small>
                    </div>""", unsafe_allow_html=True)

            # Score card
            pct = int(score/len(mcqs)*100)
            grade = "🏆 Excellent!" if pct>=80 else ("👍 Good!" if pct>=60 else ("📚 Keep Practicing!" if pct>=40 else "💪 Needs More Study"))
            grade_color = "#2ecc71" if pct>=80 else ("#f39c12" if pct>=60 else "#e74c3c")
            st.markdown(f"""<div style='background:{grade_color}; color:white; border-radius:16px;
                padding:22px; text-align:center; margin:20px 0; font-family:"Baloo 2",cursive;'>
                <div style='font-size:2.5rem; font-weight:800;'>{score}/{len(mcqs)}</div>
                <div style='font-size:1.2rem;'>{pct}% — {grade}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("🔄 Try Again", key="retry_mock", use_container_width=True):
                st.session_state.mock_questions = None
                st.session_state.mock_submitted = False
                st.session_state.mock_answers = {}
                st.rerun()
if not st.session_state.get("selected_subject"):
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""<div class='subject-card english-card'>
            <h3>📖 English Grammar</h3>
            <p>Tenses, Voice, Speech, Comprehension</p>
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
            <p>Algebra, Geometry, Statistics + Exercises</p>
            <small>18 Chapters</small>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='subject-card geography-card'>
            <h3>🌍 Geography</h3>
            <p>India, World Geography, Resources</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class='subject-card physics-card'>
            <h3>⚡ Physics</h3>
            <p>Force, Sound, Light + Numericals</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='subject-card chemistry-card'>
            <h3>🧪 Chemistry</h3>
            <p>Atoms, Reactions, Acids + Numericals</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown("""<div class='subject-card biology-card'>
            <h3>🌿 Biology</h3>
            <p>Cells, Microorganisms, Human Body</p>
            <small>12 Chapters</small>
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='subject-card computer-card'>
            <h3>💻 Computer</h3>
            <p>HTML, Excel, Networking, Cyber Safety</p>
            <small>15 Chapters</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:linear-gradient(135deg,#667eea15,#764ba215);
        border-radius:16px; padding:22px; margin-top:20px; text-align:center;
        border:2px dashed #667eea44;'>
        <h3 style='font-family:"Baloo 2",cursive;'>🚀 How to Use</h3>
        <p>1️⃣ <b>Subject चुनो</b> → 2️⃣ <b>Chapter select करो</b> → 3️⃣ <b>Study Material, Videos, Notes & Mock Test देखो</b></p>
        <p>🧮 Maths, Physics, Chemistry → <b>Practice Exercises + AI Solutions</b></p>
        <p>🧠 हर chapter पर <b>Mock Test</b> दो और score देखो!</p>
        <p>📓 <b>My Notes</b> tab में खुद notes लिखो और download करो</p>
        <p>⏱️ Sidebar में <b>Pomodoro Timer</b> — Focus के साथ पढ़ो!</p>
    </div>
    """, unsafe_allow_html=True)

# ========================================
# SESSION STATE INIT
# ========================================
for key in ["selected_subject", "selected_chapter", "text_results", "video_results",
            "image_results", "exercise_questions", "ai_summary", "show_timetable",
            "exercise_chapter", "exercise_level", "exercise_timestamp",
            "mock_questions", "mock_answers", "mock_submitted", "mock_start_time",
            "pomo_running", "pomo_end", "dark_mode", "ai_summary_chapter",
            "exercise_hints", "video_results", "image_results"]:
    if key not in st.session_state:
        if key in ["show_timetable", "pomo_running", "mock_submitted", "dark_mode"]:
            st.session_state[key] = False
        elif key == "mock_answers":
            st.session_state[key] = {}
        else:
            st.session_state[key] = None

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; font-size:0.85rem; padding:10px;'>
    Made with ❤️ for <b>La Martiniere Girls College</b> | ICSC Class 8 |
    Powered by <b>Groq llama-3.3-70b + ddgs</b> | Streamlit Cloud Ready 🚀<br>
    <small>📌 Free Resources:
    <a href='https://console.groq.com/keys' target='_blank'>Groq API</a> |
    <a href='https://www.topperlearning.com' target='_blank'>TopperLearning</a> |
    <a href='https://www.vedantu.com' target='_blank'>Vedantu</a></small>
</div>
""", unsafe_allow_html=True)
