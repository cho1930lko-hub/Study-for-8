import streamlit as st
from groq import Groq
from ddgs import DDGS
import random, json, re, time
from datetime import datetime

# ════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════
st.set_page_config(
    page_title="📚 StudyMate - La Martiniere Girls",
    page_icon="🎓", layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Quicksand:wght@400;500;600;700&display=swap');
* { font-family:'Quicksand',sans-serif !important; }
h1,h2,h3,h4 { font-family:'Baloo 2',cursive !important; }
.stApp { background:#f4f6ff !important; }
.dark .stApp { background:#0f1117 !important; }
section[data-testid="stSidebar"] { background:#ffffff !important; border-right:1px solid #e0e0f0 !important; }
.main-header {
    background:linear-gradient(135deg,#667eea,#764ba2);
    padding:22px 30px; border-radius:20px; color:white;
    text-align:center; margin-bottom:25px;
    box-shadow:0 8px 30px rgba(102,126,234,0.3);
}
.main-header h1 { font-size:2.2rem; font-weight:800; margin:0; color:white !important; }
.main-header p  { font-size:1rem; opacity:0.9; margin:5px 0 0; color:white !important; }
.subject-card {
    background:#fff; border-radius:16px; padding:18px; text-align:center;
    border:3px solid transparent; box-shadow:0 4px 15px rgba(102,126,234,0.1);
    transition:all 0.3s ease; margin-bottom:10px;
}
.subject-card:hover { transform:translateY(-4px); box-shadow:0 8px 28px rgba(102,126,234,0.2); }
.english-card{border-color:#FF6B6B;} .maths-card{border-color:#4ECDC4;}
.physics-card{border-color:#45B7D1;} .chemistry-card{border-color:#96CEB4;}
.biology-card{border-color:#F6C90E;} .history-card{border-color:#DDA0DD;}
.geography-card{border-color:#98D8C8;} .computer-card{border-color:#FF9F43;}
.info-box {
    background:#667eea12; border-left:4px solid #667eea;
    border-radius:0 12px 12px 0; padding:15px 20px; margin:10px 0;
}
.question-box {
    background:#f8f9ff; border:2px solid #667eea33;
    border-radius:14px; padding:18px; margin:8px 0; font-size:1.05rem;
}
.q-number { color:#667eea; font-weight:800; font-size:1.2rem; }
.mock-correct { background:#e8f8f0; border-left:4px solid #2ecc71; padding:10px 15px; border-radius:0 10px 10px 0; margin:5px 0; }
.mock-wrong   { background:#fdecea; border-left:4px solid #e74c3c; padding:10px 15px; border-radius:0 10px 10px 0; margin:5px 0; }
.agent-tag { display:inline-block; background:#667eea; color:white; padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:700; margin:2px; }
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; margin:2px; }
.badge-icse { background:#667eea22; color:#667eea; }
.badge-c8   { background:#FF6B6B22; color:#FF6B6B; }
.pbar-bg   { background:#e0e0f0; border-radius:20px; height:10px; margin:4px 0; }
.pbar-fill { background:linear-gradient(90deg,#667eea,#764ba2); border-radius:20px; height:10px; }
.score-row { background:#fff; border:1px solid #e0e0f0; border-radius:10px; padding:10px 15px; margin:4px 0; }
.countdown { background:linear-gradient(135deg,#FF6B6B,#ee0979); color:white; border-radius:16px; padding:18px; text-align:center; margin:10px 0; }
.stButton>button { border-radius:12px !important; font-weight:700 !important; transition:all 0.2s !important; }
.stButton>button:hover { transform:translateY(-2px) !important; }
div[data-testid="stExpander"] { border-radius:12px !important; border:1px solid #e0e0f0 !important; margin-bottom:8px !important; }
</style>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# PASSWORD
# ════════════════════════════════════════════════════════
def check_password():
    pw = st.secrets.get("APP_PASSWORD","studymate123") if hasattr(st,"secrets") else "studymate123"
    if st.session_state.get("auth"): return True
    st.markdown("""<div style='max-width:400px;margin:80px auto 0;'>
    <div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:24px;
    padding:40px;text-align:center;box-shadow:0 20px 60px rgba(102,126,234,0.4);'>
    <div style='font-size:3rem;'>🎓</div>
    <h2 style='color:white;margin:10px 0 5px;'>StudyMate</h2>
    <p style='color:rgba(255,255,255,0.8);margin:0 0 25px;'>La Martiniere Girls • ICSE Class 8</p>
    </div></div>""", unsafe_allow_html=True)
    _, c2, _ = st.columns([1,2,1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        p = st.text_input("🔒 Password", type="password", placeholder="Enter password...", key="pinput")
        if st.button("🚀 Login", use_container_width=True, type="primary"):
            if p == pw:
                st.session_state.auth = True; st.rerun()
            elif p: st.error("❌ Wrong password!")
    return False

if not check_password(): st.stop()

# ════════════════════════════════════════════════════════
# SUBJECTS
# ════════════════════════════════════════════════════════
SUBJECTS = {
    "📖 English Grammar": {
        "icon":"📖","color":"#FF6B6B","card":"english-card","num":False,
        "chapters":["Parts of Speech","Tenses","Active & Passive Voice",
            "Direct & Indirect Speech","Clauses & Phrases","Determiners","Modals",
            "Prepositions","Conjunctions","Question Tags","Comprehension Skills",
            "Letter Writing","Essay Writing","Transformation of Sentences","Punctuation & Spelling"]
    },
    "➕ Mathematics": {
        "icon":"➕","color":"#4ECDC4","card":"maths-card","num":True,
        "chapters":["Rational Numbers","Exponents and Powers","Squares and Square Roots",
            "Cubes and Cube Roots","Playing with Numbers","Operations on Sets",
            "Percentage and its Applications","Simple and Compound Interest",
            "Direct and Inverse Variation","Algebraic Expressions and Identities",
            "Factorisation","Linear Equations and Inequalities in One Variable",
            "Understanding Shapes","Construction of Quadrilaterals","Circle",
            "Coordinate System and Graphs","Symmetry, Reflection and Rotation",
            "Visualising Solid Shapes","Mensuration","Data Handling"]
    },
    "⚡ Physics": {
        "icon":"⚡","color":"#45B7D1","card":"physics-card","num":True,
        "chapters":["Force & Pressure","Friction","Sound","Light – Reflection & Refraction",
            "Stars & The Solar System","Motion & Measurement of Distances",
            "Electricity & Circuits","Magnetic Effects of Current",
            "Heat","Simple Machines","Work, Energy & Power","Gravitation"]
    },
    "🧪 Chemistry": {
        "icon":"🧪","color":"#96CEB4","card":"chemistry-card","num":True,
        "chapters":["Matter in Our Surroundings","Is Matter Around Us Pure?",
            "Atoms & Molecules","Structure of Atom","Chemical Reactions",
            "Acids, Bases & Salts","Metals & Non-Metals","Carbon & Its Compounds",
            "Combustion & Flame","Materials – Metals & Non Metals","Coal & Petroleum","Water"]
    },
    "🌿 Biology": {
        "icon":"🌿","color":"#F6C90E","card":"biology-card","num":False,
        "chapters":["Transport of food and minerals in plants","Reproduction in plants",
            "Ecosystem","Endocrine System in Humans","Adolescence and Accompanying changes",
            "Circulatory System in Humans","Nervous System in Humans","Diseases and First Aid",
            "Food Production & Management","Human Body Systems","Animal Reproduction"]
    },
    "🏛️ History": {
        "icon":"🏛️","color":"#DDA0DD","card":"history-card","num":False,
        "chapters":["How, When & Where","From Trade to Territory","Ruling the Countryside",
            "Tribals, Dikus & the Vision of a Golden Age","When People Rebel – 1857",
            "Civilising the Native, Educating the Nation","Women, Caste & Reform",
            "The Making of the National Movement","India After Independence",
            "The Mughal Empire","Architecture as Power","Paintings & Cultural Developments"]
    },
    "🌍 Geography": {
        "icon":"🌍","color":"#98D8C8","card":"geography-card","num":False,
        "chapters":["Representation of Geographical Features","Population Dynamics",
            "Migration","Urbanization","Disasters and their Management",
            "SOME OTHER NATURAL DISASTERS","WHAT CAUSES THE GROUND TO SHAKE?",
            "Asia - Location and Physical Features","Asia - Climate and Natural Vegetation",
            "India - Location and Physical Features","NORTHERN PLAINS - HOW A LANDFORM AFFECTS THE WAY OF LIFE",
            "India - Climate","India - Flora and Fauna","India - Human Resources"]
    },
    "💻 Computer": {
        "icon":"💻","color":"#FF9F43","card":"computer-card","num":False,
        "chapters":["Operating System","Computer Networks","Computational and Algorithmic Thinking",
            "App Development","Formulas and Functions in Google Sheets",
            "Data Visualisation Using Google Sheets","Fundamentals of Java",
            "Conditional Statements in Java","Loops in Java","Introduction to HTML","HTML Forms"]
    }
}
TOTAL_CH = sum(len(v["chapters"]) for v in SUBJECTS.values())

# ════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════
def groq_client():
    k = st.session_state.get("groq_key","")
    return Groq(api_key=k) if k else None

def llm(prompt, temp=0.7, tokens=1500):
    c = groq_client()
    if not c: return None
    r = c.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=temp, max_tokens=tokens
    )
    return r.choices[0].message.content

def md2html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.+)$',   r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+',
                  lambda m:f'<ul style="padding-left:20px">{m.group()}</ul>',
                  text, flags=re.DOTALL)
    return text.replace('\n','<br>')

def make_html(title, subtitle, content, accent="#667eea"):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>{title}</title><style>
body{{font-family:'Segoe UI',Arial,sans-serif;max-width:820px;margin:40px auto;padding:30px;color:#333;line-height:1.8;}}
h1,h2,h3{{color:{accent};}} ul{{background:#f8f9ff;border-left:4px solid {accent};padding:10px 10px 10px 30px;border-radius:0 8px 8px 0;}}
li{{margin:6px 0;}} strong{{color:#222;}} em{{color:#555;}}
.hdr{{background:linear-gradient(135deg,{accent},#764ba2);color:white;padding:22px 28px;border-radius:14px;margin-bottom:28px;}}
.hdr h1{{color:white;border:none;margin:0;font-size:1.6rem;}}
.hdr p{{margin:6px 0 0;opacity:0.85;font-size:0.9rem;}}
.body{{background:#fff;border:1px solid #e8e8f0;border-radius:12px;padding:25px 30px;}}
.foot{{margin-top:30px;padding-top:12px;border-top:1px solid #ddd;color:#aaa;font-size:0.78rem;text-align:center;}}
</style></head><body>
<div class="hdr"><h1>📚 {title}</h1><p>{subtitle}</p></div>
<div class="body">{md2html(content)}</div>
<div class="foot">StudyMate AI | ICSE Class 8 | La Martiniere Girls | {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>
</body></html>"""

def pbar(pct, color="#667eea"):
    st.markdown(f"""<div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%;background:{color};"></div></div>""",
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# ██  8 AI AGENTS  ██
# ════════════════════════════════════════════════════════

# ── Agent 1: Orchestrator ─────────────────────────────
class Orchestrator:
    """Routes tasks to correct agents with retry logic"""
    def run(self, task, **kw):
        for attempt in range(3):
            try:
                if task=="summary":       return SummaryAgent().run(**kw)
                if task=="questions":     return QuestionAgent().run(**kw)
                if task=="mock":          return MockAgent().run(**kw)
                if task=="quality":       return QualityAgent().run(**kw)
                if task=="theory":        return TheoryAgent().run(**kw)
                if task=="performance":   return PerfAgent().analyze(**kw)
                if task=="personalize":   return PersonAgent().suggest(**kw)
                if task=="hints":         return HintsAgent().run(**kw)
            except Exception as e:
                if attempt==2: return {"error":str(e)}
                time.sleep(0.3)
        return {"error":"failed"}

ORC = Orchestrator()

# ── Agent 2: Memory / Progress ────────────────────────
class MemAgent:
    def mark(self, subj, ch, status):
        st.session_state[f"prog_{subj}_{ch}".replace(" ","_")] = status
        st.session_state[f"prog_ts_{subj}_{ch}".replace(" ","_")] = datetime.now().strftime("%d %b %I:%M %p")

    def get(self, subj, ch):
        return st.session_state.get(f"prog_{subj}_{ch}".replace(" ","_"), "pending")

    def overall(self):
        d=r=p=0
        for s,v in SUBJECTS.items():
            for c in v["chapters"]:
                st_ = self.get(s,c)
                if st_=="done": d+=1
                elif st_=="review": r+=1
                else: p+=1
        return {"done":d,"review":r,"pending":p,"total":TOTAL_CH}

    def save_note(self, subj, ch, note):
        st.session_state[f"note_{subj}_{ch}".replace(" ","_")] = note
        st.session_state[f"note_ts_{subj}_{ch}".replace(" ","_")] = datetime.now().strftime("%d %b %I:%M %p")

    def get_note(self, subj, ch):
        return st.session_state.get(f"note_{subj}_{ch}".replace(" ","_"), "")

    def all_notes(self):
        return [(k,v) for k,v in st.session_state.items()
                if k.startswith("note_") and not k.endswith("_ts") and v]

    def weak_subjects(self):
        weak=[]
        for s in SUBJECTS:
            scores = st.session_state.get(f"sscores_{s}".replace(" ","_"),[])
            if scores:
                avg = sum(scores)/len(scores)
                if avg<60: weak.append({"subject":s,"avg":round(avg,1)})
        return sorted(weak, key=lambda x:x["avg"])

MEM = MemAgent()

# ── Agent 3: Performance Tracker ─────────────────────
class PerfAgent:
    def save(self, subj, ch, score, total):
        k = f"scores_{subj}_{ch}".replace(" ","_")
        h = st.session_state.get(k,[])
        h.append({"score":score,"total":total,"pct":round(score/total*100),
                  "time":datetime.now().strftime("%d %b %I:%M %p")})
        st.session_state[k] = h[-10:]
        sk = f"sscores_{subj}".replace(" ","_")
        ss = st.session_state.get(sk,[])
        ss.append(round(score/total*100))
        st.session_state[sk] = ss[-20:]

    def history(self, subj, ch):
        return st.session_state.get(f"scores_{subj}_{ch}".replace(" ","_"),[])

    def subj_avg(self, subj):
        s = st.session_state.get(f"sscores_{subj}".replace(" ","_"),[])
        return round(sum(s)/len(s),1) if s else 0

    def analyze(self, subj, ch, **kw):
        h = self.history(subj,ch)
        if not h: return {"attempts":0}
        sc = [x["pct"] for x in h]
        trend = ("improving" if sc[-1]>sc[0] else "declining" if sc[-1]<sc[0] else "stable") if len(sc)>1 else "stable"
        return {"history":h,"best":max(sc),"latest":sc[-1],"avg":round(sum(sc)/len(sc),1),"trend":trend,"attempts":len(sc)}

PERF = PerfAgent()

# ── Agent 4: Content Quality Filter ──────────────────
class QualityAgent:
    def run(self, results, subj, ch, **kw):
        if not results: return []
        kws = ch.lower().split() + subj.lower().split()
        edu = ["topperlearning","vedantu","byjus","ncert","meritnation","studiestoday","extramarks","tiwari","icse"]
        scored=[]
        for r in results:
            t = r.get("title","").lower(); b = r.get("body","").lower()
            sc = sum(2 if w in t else 1 if w in b else 0 for w in kws if len(w)>3)
            if any(s in r.get("href","").lower() for s in edu): sc+=3
            if len(b)<50: sc-=2
            scored.append((sc,r))
        scored.sort(key=lambda x:x[0],reverse=True)
        return [r for _,r in scored[:8]]

QUAL = QualityAgent()

# ── Agent 5: Question Generator ──────────────────────
class QuestionAgent:
    def run(self, subj, ch, level, mode="ai", **kw):
        used_k = f"usedq_{subj}_{ch}".replace(" ","_")
        used   = st.session_state.get(used_k,[])
        if mode=="ai":
            avoid = f"Do NOT repeat: {used[-5:]}" if used else ""
            result = llm(f"""Expert ICSE Class 8 {subj} teacher. Generate EXACTLY 10 {level} 
numerical/practice questions for chapter: "{ch}". {avoid}
Rules: specific numbers in every question, all different, ICSE Class 8 syllabus, English only.
OUTPUT: only numbered list 1-10, nothing else.""", temp=0.95, tokens=1600)
            if result:
                qs = [l.split('.',1)[1].strip() for l in result.split('\n')
                      if l.strip() and l.strip()[0].isdigit() and '.' in l.strip()[:3]]
                qs = [q for q in qs if len(q)>10 and q not in used]
                if len(qs)>=5:
                    st.session_state[used_k] = (used+qs)[-30:]
                    return qs[:10]
        return self._local(subj, ch, level, used)

    def _local(self, subj, ch, level, used):
        n = lambda a=2,b=99: random.randint(a,b)
        r = lambda lst: random.choice(lst)
        banks = {
            "Rational Numbers":[
                f"Find: {n(1,9)}/{n(2,10)} + {n(1,9)}/{n(2,10)}",
                f"Simplify: {n(2,12)}/{n(2,12)} × {n(2,12)}/{n(2,12)}",
                f"Find x: {n(1,6)}/{n(2,8)} × x = {n(1,6)}/{n(2,8)}",
                f"Arrange ascending: {n(-5,5)}/7, {n(-5,5)}/7, {n(-5,5)}/7",
                f"Additive inverse of {n(-8,8)}/{n(2,9)}?"],
            "Squares and Square Roots":[
                f"Find √{r([144,169,196,225,256,289,324,361,400,441,484,529])}",
                f"Is {n(100,500)} a perfect square?",
                f"Square of {n(11,30)}?",
                f"√{r([529,625,784,961,1024,1296,1444,1600])} by long division",
                f"Smallest multiplier for perfect square: {r([180,252,108,1008,1620])}"],
            "Simple and Compound Interest":[
                f"P=₹{n(1,20)*500}, R={r([5,6,8,10,12])}%, T={n(2,5)}yr. SI?",
                f"CI on ₹{n(2,10)*1000} at {r([5,8,10,12])}% for {n(1,3)} years.",
                f"Sum doubles in {r([5,8,10,12,15])} years at SI. Rate?",
                f"CI-SI on ₹{n(5,20)*1000} for 2yr at {r([5,8,10,12])}%?",
                f"Amount: P=₹{n(3,15)*1000}, R={r([4,5,8,10])}%, T={n(2,4)}yr CI?"],
            "Mensuration":[
                f"Area of circle r={n(3,15)}cm. (π=3.14)",
                f"Perimeter of rect: l={n(10,30)}cm, b={n(5,15)}cm.",
                f"Volume of cuboid: {n(5,20)}×{n(3,12)}×{n(3,10)} cm",
                f"TSA of cylinder: r={n(3,10)}cm, h={n(8,20)}cm",
                f"Area of trapezium: parallel={n(8,20)}&{n(4,12)}cm, h={n(5,15)}cm"],
            "Force & Pressure":[
                f"F={n(10,100)}N, A={n(2,20)}m². Pressure?",
                f"Mass={n(5,50)}kg. Weight? (g=10)",
                f"Hydraulic: small={n(2,8)}cm², large={n(50,200)}cm², F={n(20,100)}N. Output?",
                f"Water pressure at depth {n(2,20)}m? (ρ=1000,g=10)",
                f"Pressure bottom of {n(5,20)}m mercury? (ρ=13600)"],
            "Sound":[
                f"v=340m/s, f={n(200,2000)}Hz. Wavelength?",
                f"Echo after {n(2,8)}s. Wall distance? (v=340m/s)",
                f"SONAR echo after {n(2,10)}s. Depth? (v=1500m/s)",
                f"T={r([0.01,0.02,0.05,0.1])}s. Frequency?",
                f"Sound crosses {n(1,10)}km. Time? (v=340m/s)"],
            "Work, Energy & Power":[
                f"W: F={n(10,100)}N, d={n(2,20)}m, θ=0°.",
                f"KE: m={n(5,50)}kg, v={n(2,20)}m/s.",
                f"PE: m={n(2,20)}kg, h={n(5,50)}m. (g=10)",
                f"Power: W={n(500,5000)}J, t={n(5,60)}s.",
                f"Efficiency={n(60,95)}%. Input={n(1000,5000)}J. Useful output?"],
            "Electricity & Circuits":[
                f"V={n(6,24)}V, R={n(5,100)}Ω. Current?",
                f"R1={n(5,30)}Ω, R2={n(5,30)}Ω series. Total R? I if V={n(6,24)}V?",
                f"Power: V={n(110,240)}V, I={n(1,15)}A. P?",
                f"Energy: P={n(100,2000)}W, t={n(1,10)}hr. Units consumed?",
                f"R1={n(5,20)}Ω, R2={n(5,20)}Ω parallel. Req?"],
            "Atoms & Molecules":[
                f"Molar mass of H₂O? (H=1,O=16)",
                f"Moles in {n(18,180)}g of H₂O?",
                f"Atoms in {n(1,5)} mol O₂? (6.022×10²³)",
                f"Mass of {n(2,10)} mol NaCl? (Na=23,Cl=35.5)",
                f"% Na in NaCl?"],
            "Acids, Bases & Salts":[
                f"pH={n(1,14)}. Acidic, basic or neutral?",
                f"Neutralise {n(10,50)}mL 0.1M HCl with ? mL 0.1M NaOH",
                f"Identify: {r(['HCl','NaOH','NaCl','H₂SO₄','Ca(OH)₂'])}. pH>7?",
                f"{n(10,100)}mL {r([0.1,0.5,1])}M H₂SO₄. Moles of H⁺?",
                f"Neutralisation reaction: HCl + NaOH → ?"],
            "Heat":[
                f"Q=mcΔT. m={n(1,10)}kg,c=4200J/kg°C,ΔT={n(10,80)}°C. Q?",
                f"Convert {n(0,100)}°C to Fahrenheit.",
                f"Convert {n(32,212)}°F to Celsius.",
                f"Linear expansion: L₀={n(1,10)}m,α=12×10⁻⁶/°C,ΔT={n(20,100)}°C. ΔL?",
                f"m₁={n(1,5)}kg at {n(80,100)}°C + m₂={n(1,5)}kg at {n(10,30)}°C. Final temp?"],
            "Percentage and its Applications":[
                f"Find {n(15,40)}% of ₹{n(200,1000)}",
                f"CP=₹{n(100,500)}, SP=₹{n(120,600)}. Profit%?",
                f"{n(30,80)}% passed. Total={n(50,200)}. How many passed?",
                f"CP=₹{n(300,800)}, SP=₹{n(200,700)}. Loss%?",
                f"MP=₹{n(500,2000)}, Discount={n(10,30)}%. SP?"],
        }
        pool = banks.get(ch,[])
        if not pool:
            pool = [
                f"[{ch}] Solve: {n()}x + {n()} = {n()*3}",
                f"[{ch}] If a={n()}, b={n()}: (a+b)² - (a-b)²?",
                f"[{ch}] Area with dimensions {n()}×{n()}?",
                f"[{ch}] Ratio {n()}:{n()}, sum={n()*5}. Each part?",
                f"[{ch}] Rate={n()} units/hr. Work in {n()} hrs?",
                f"[{ch}] Distance={n()*10}m, Speed={n()*2}m/s. Time?",
                f"[{ch}] P=₹{n()*50}, R={r([5,8,10,12])}%, T={n(1,5)}yr. Interest?",
                f"[{ch}] Volume of cube side {n()}cm?",
                f"[{ch}] Mean of {n()},{n()},{n()},{n()},{n()}?",
                f"[{ch}] {n()} out of {n()*4} as percentage?",
            ]
        fresh = [q for q in pool if q not in used]
        if len(fresh)<10: fresh = pool.copy()
        return random.sample(fresh, min(10, len(fresh)))

QAGENT = QuestionAgent()

# ── Agent 6: Mock Test ────────────────────────────────
class MockAgent:
    def run(self, subj, ch, difficulty="Medium", **kw):
        result = llm(f"""ICSE Class 8 {subj} teacher. Chapter: {ch}. Difficulty: {difficulty}.
Generate EXACTLY 10 MCQ. Return ONLY valid JSON array, no extra text:
[{{"q":"Question?","options":["A) opt1","B) opt2","C) opt3","D) opt4"],"answer":"A","explanation":"Why A."}}]
Rules: {ch} only, English, one correct answer, difficulty={difficulty}""",
            temp=0.7, tokens=2000)
        if not result: return []
        try:
            raw = result.replace("```json","").replace("```","").strip()
            return json.loads(raw)[:10]
        except:
            return []

MOCK = MockAgent()

# ── Agent 7: Theory Practice ─────────────────────────
class TheoryAgent:
    def run(self, subj, ch, level="basic", **kw):
        result = llm(f"""ICSE Class 8 {subj} teacher. Chapter: "{ch}". Level: {level}.
Generate EXACTLY 10 theory/descriptive questions. Mix: define, explain, give examples,
compare, why/how, diagram-based. English only.
OUTPUT: only numbered list 1-10.""", temp=0.85, tokens=1200)
        if result:
            qs = [l.split('.',1)[1].strip() for l in result.split('\n')
                  if l.strip() and l.strip()[0].isdigit() and '.' in l.strip()[:3]]
            qs = [q for q in qs if len(q)>10]
            if len(qs)>=5: return qs[:10]
        return [
            f"Define the main concept of '{ch}' in your own words.",
            f"List 4 important facts about {ch}.",
            f"Give 2 real-life examples of {ch}.",
            f"Compare two key elements of {ch}.",
            f"Why is {ch} important in {subj}?",
            f"Draw and label a diagram related to {ch}.",
            f"What are causes and effects in {ch}?",
            f"Write a short note (5-6 lines) on {ch}.",
            f"Give 3 examples illustrating {ch}.",
            f"Most important fact about {ch} (one sentence)?",
        ]

THEORY = TheoryAgent()

# ── Agent 8: Personalization ──────────────────────────
class PersonAgent:
    def suggest(self, **kw):
        prog  = MEM.overall()
        weak  = MEM.weak_subjects()
        tips  = []
        if weak: tips.append(f"⚠️ Focus on **{weak[0]['subject'].split(' ',1)[1]}** — avg score {weak[0]['avg']}%")
        unstarted = [s for s in SUBJECTS if PERF.subj_avg(s)==0]
        if unstarted: tips.append(f"📚 Haven't tested **{unstarted[0].split(' ',1)[1]}** yet!")
        if prog["done"]<5: tips.append("🎯 Mark chapters as Done after studying!")
        ai_tip = llm(f"ICSE Class 8 student. Progress: {prog['done']}/{prog['total']} chapters done. "
                     f"Weak: {[w['subject'] for w in weak[:2]]}. Give 3 quick study tips in English. "
                     f"Be specific and encouraging. Max 2 lines each.", temp=0.7, tokens=300)
        return {"suggestions":tips,"ai_tip":ai_tip,"progress":prog,"weak":weak}

PERSON = PersonAgent()

# ── Summary Agent ─────────────────────────────────────
class SummaryAgent:
    def run(self, subj, ch, **kw):
        return llm(f"""Expert ICSE Class 8 English-medium teacher. Topic: {ch}. Subject: {subj}.
Write student-friendly study note ENTIRELY IN ENGLISH:
1. 📌 Key Concepts (4-5 bullets)
2. 📚 Important Definitions (2-3, simple)
3. 💡 Memory Tips / Mnemonics
4. ⭐ Most Important for ICSE Exam
5. 📝 2-3 Sample Questions with Answers
ENGLISH ONLY. Simple, exam-focused.""", temp=0.7, tokens=1500)

SUMM = SummaryAgent()

# ── Hints Agent ───────────────────────────────────────
class HintsAgent:
    def run(self, subj, questions, **kw):
        q_text = "\n".join([f"Q{i+1}. {q}" for i,q in enumerate(questions)])
        return llm(f"""ICSE Class 8 {subj} teacher. Solve step-by-step. ENGLISH ONLY.
{q_text}
Format each: Q1. Formula:[x] Working:[steps] Answer:[final with unit]""",
            temp=0.3, tokens=2000)

HINTS = HintsAgent()

# ════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════
_defs = {
    "auth":False,"dark":False,"show_tt":False,"pomo_run":False,"pomo_end":None,
    "sel_subj":None,"sel_ch":None,"text_res":[],"vid_res":[],"img_res":[],
    "ex_qs":[],"ai_sum":None,"ai_sum_ch":None,"ex_ch":None,"ex_lv":None,
    "ex_ts":None,"ex_hints":None,"mock_qs":None,"mock_ans":{},"mock_done":False,
    "mock_t0":None,"mock_tlim":600,"groq_key":"","tg_link":"","exam_date":None,
    "show_ai_dash":False,"theory_qs":[],
}
for k,v in _defs.items():
    if k not in st.session_state: st.session_state[k]=v

# ════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style='background:linear-gradient(135deg,#667eea,#764ba2);
        padding:15px;border-radius:12px;color:white;text-align:center;margin-bottom:15px;'>
        <h3 style='margin:0;font-size:1.1rem;font-family:"Baloo 2",cursive;'>🎓 La Martiniere Girls</h3>
        <p style='margin:4px 0 0;font-size:0.8rem;opacity:0.85;'>ICSE Board • Class 8</p>
    </div>""", unsafe_allow_html=True)

    # Dark Mode
    dark = st.toggle("🌙 Night Mode", value=st.session_state.dark)
    st.session_state.dark = dark
    if dark:
        st.markdown("""<style>
        .stApp,section[data-testid="stSidebar"]{background-color:#0f1117 !important;}
        .stApp *{color:#e8eaf6 !important;}
        .question-box{background:#1e2140 !important;}
        .info-box{background:#7c8ef720 !important;}
        .subject-card,.score-row{background:#1a1d2e !important;}
        </style>""", unsafe_allow_html=True)

    st.header("⚙️ Settings")

    # API Key
    _sk = st.secrets.get("GROQ_API_KEY","") if hasattr(st,"secrets") else ""
    if _sk:
        st.session_state.groq_key = _sk
        groq_api_key = _sk
        st.success("🔐 API Key auto-loaded ✅")
    else:
        groq_api_key = st.text_input("🔑 Groq API Key", type="password",
            value=st.session_state.groq_key, help="console.groq.com/keys")
        if groq_api_key: st.session_state.groq_key = groq_api_key
        st.info("💡 Free: console.groq.com/keys")

    st.divider()

    # Exam Countdown
    st.markdown("**📅 Exam Countdown**")
    ed = st.date_input("Exam Date:", value=None, min_value=datetime.now().date(), key="exam_di")
    if ed: st.session_state.exam_date = str(ed)
    if st.session_state.exam_date:
        try:
            days = max(0,(datetime.strptime(st.session_state.exam_date,"%Y-%m-%d")-datetime.now()).days)
            col = "#e74c3c" if days<30 else "#f39c12" if days<60 else "#2ecc71"
            st.markdown(f"""<div class="countdown" style="background:linear-gradient(135deg,{col},{col}bb);">
                <div style="font-size:2rem;font-weight:800;font-family:'Baloo 2',cursive;">{days}</div>
                <div style="font-size:0.9rem;opacity:0.9;">Days to Exam!</div>
            </div>""", unsafe_allow_html=True)
            prog = MEM.overall()
            cov  = round(prog["done"]/prog["total"]*100) if prog["total"] else 0
            st.caption(f"Syllabus covered: {cov}%")
            pbar(cov)
        except: pass

    st.divider()

    # Overall Progress
    st.markdown("**📊 Progress**")
    p = MEM.overall()
    pc1,pc2,pc3 = st.columns(3)
    pc1.metric("✅",p["done"]); pc2.metric("🔄",p["review"]); pc3.metric("📖",p["pending"])
    pbar(round(p["done"]/p["total"]*100) if p["total"] else 0)

    st.divider()

    # Telegram
    st.markdown("**📲 Telegram** *(Optional)*")
    tg = st.text_input("Channel link", placeholder="https://t.me/...",
        value=st.session_state.tg_link, label_visibility="collapsed")
    if tg: st.session_state.tg_link = tg; st.success("✅ Linked!")

    st.divider()

    # Pomodoro
    st.markdown("**⏱️ Pomodoro Timer**")
    pm = st.selectbox("Study time:", [25,30,45,50], key="pomo_mins")
    pp1,pp2 = st.columns(2)
    with pp1:
        if st.button("▶️ Start",key="ps",use_container_width=True):
            st.session_state.pomo_end = time.time()+pm*60
            st.session_state.pomo_run = True
    with pp2:
        if st.button("⏹ Stop",key="pp",use_container_width=True):
            st.session_state.pomo_run = False
            st.session_state.pomo_end = None

    if st.session_state.pomo_run and st.session_state.pomo_end:
        rem = int(st.session_state.pomo_end - time.time())
        if rem>0:
            m,s = divmod(rem,60)
            st.markdown(f"""<div style='background:linear-gradient(135deg,#667eea,#764ba2);
                color:white;border-radius:12px;padding:10px;text-align:center;
                font-size:1.6rem;font-weight:800;font-family:"Baloo 2",cursive;'>
                ⏱️ {m:02d}:{s:02d}</div>""", unsafe_allow_html=True)
        else:
            st.success("🎉 Break time!")
            st.session_state.pomo_run = False

    st.divider()
    if st.button("🤖 AI Study Suggestions",use_container_width=True):
        st.session_state.show_ai_dash = not st.session_state.show_ai_dash
    st.divider()
    if st.button("📅 Generate Timetable",use_container_width=True):
        st.session_state.show_tt = True
    st.divider()
    if st.button("🔓 Logout",use_container_width=True):
        st.session_state.auth = False; st.rerun()

# ════════════════════════════════════════════════════════
# MAIN HEADER
# ════════════════════════════════════════════════════════
st.markdown("""<div class='main-header'>
    <h1>📚 StudyMate Dashboard</h1>
    <p>ICSE Class 8 • English Medium • La Martiniere Girls College</p>
    <span class='badge badge-icse'>ICSE Board</span>
    <span class='badge badge-c8'>Class 8</span>
    <span class='agent-tag'>8 AI Agents Active 🤖</span>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# AI PERSONALIZATION DASHBOARD
# ════════════════════════════════════════════════════════
if st.session_state.show_ai_dash:
    st.markdown("## 🤖 AI Personalization Dashboard")
    with st.spinner("Analyzing your study pattern..."):
        res = ORC.run("personalize")
    if res and not res.get("error"):
        prog = res.get("progress",{})
        weak = res.get("weak",[])
        da,db,dc = st.columns(3)
        da.markdown(f"""<div style='background:#2ecc7122;border:2px solid #2ecc71;border-radius:14px;
            padding:15px;text-align:center;'><div style='font-size:2rem;font-weight:800;color:#2ecc71;'>
            {prog.get('done',0)}</div><div>✅ Done</div></div>""", unsafe_allow_html=True)
        db.markdown(f"""<div style='background:#f39c1222;border:2px solid #f39c12;border-radius:14px;
            padding:15px;text-align:center;'><div style='font-size:2rem;font-weight:800;color:#f39c12;'>
            {prog.get('review',0)}</div><div>🔄 Review</div></div>""", unsafe_allow_html=True)
        dc.markdown(f"""<div style='background:#e74c3c22;border:2px solid #e74c3c;border-radius:14px;
            padding:15px;text-align:center;'><div style='font-size:2rem;font-weight:800;color:#e74c3c;'>
            {prog.get('pending',0)}</div><div>📖 Left</div></div>""", unsafe_allow_html=True)
        for s in res.get("suggestions",[]): st.info(s)
        if weak:
            st.markdown("### ⚠️ Weak Subjects")
            for w in weak:
                wc1,wc2 = st.columns([3,1])
                with wc1:
                    st.write(f"**{w['subject'].split(' ',1)[1]}**")
                    pbar(int(w["avg"]), "#e74c3c" if w["avg"]<40 else "#f39c12")
                wc2.metric("Avg",f"{w['avg']}%")
        if res.get("ai_tip"):
            st.markdown("### 🧠 AI Tips")
            st.markdown(f"<div class='info-box'>{res['ai_tip']}</div>", unsafe_allow_html=True)
    if st.button("❌ Close"):
        st.session_state.show_ai_dash = False; st.rerun()
    st.divider()

# ════════════════════════════════════════════════════════
# TIMETABLE
# ════════════════════════════════════════════════════════
if st.session_state.show_tt:
    st.markdown("## 📅 Study Timetable")
    days  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    slots = ["7:00-8:00","9:00-10:00","10:30-11:30","3:00-4:00","4:00-5:00","6:00-7:00"]
    colors= {"Monday":"#FF6B6B","Tuesday":"#4ECDC4","Wednesday":"#45B7D1",
             "Thursday":"#96CEB4","Friday":"#FFEAA7","Saturday":"#DDA0DD"}
    cols  = st.columns(3)
    for i,day in enumerate(days):
        with cols[i%3]:
            c = colors[day]
            st.markdown(f"""<div style='background:white;border-radius:14px;padding:15px;
                border-top:4px solid {c};box-shadow:0 3px 12px rgba(0,0,0,0.08);margin-bottom:12px;'>
                <h4 style='color:{c};margin:0 0 10px;'>📆 {day}</h4>""", unsafe_allow_html=True)
            for subj in random.sample(list(SUBJECTS.keys()), 3):
                act = random.choice(["Study","Revision","Mock Test","Practice Q"])
                st.markdown(f"⏰ **{random.choice(slots)}** — {subj.split()[-1]} _{act}_")
            st.markdown("</div>", unsafe_allow_html=True)
    tt1,tt2 = st.columns(2)
    with tt1:
        if st.button("🔄 Regenerate"): st.rerun()
    with tt2:
        if st.button("❌ Close"):
            st.session_state.show_tt = False; st.rerun()
    st.divider()

# ════════════════════════════════════════════════════════
# SUBJECT SELECTION
# ════════════════════════════════════════════════════════
st.markdown("## 📚 Choose Your Subject")
st.markdown("किस subject पर पढ़ना है? नीचे click करो 👇")

cols = st.columns(4)
for i,(sn,sd) in enumerate(SUBJECTS.items()):
    with cols[i%4]:
        done  = sum(1 for c in sd["chapters"] if MEM.get(sn,c)=="done")
        total = len(sd["chapters"])
        avg   = PERF.subj_avg(sn)
        if st.button(f"{sd['icon']} {sn.split(' ',1)[1]}", key=f"s{i}", use_container_width=True):
            st.session_state.sel_subj = sn
            st.session_state.sel_ch   = None
            st.session_state.ex_qs    = []
            st.session_state.ai_sum   = None
            st.rerun()
        st.caption(f"✅{done}/{total}" + (f" | 📊{avg}%" if avg else ""))

# ════════════════════════════════════════════════════════
# CHAPTER LIST
# ════════════════════════════════════════════════════════
if st.session_state.sel_subj:
    sn = st.session_state.sel_subj
    sd = SUBJECTS[sn]
    st.divider()
    st.markdown(f"### {sd['icon']} {sn} — Chapters")
    done_c = sum(1 for c in sd["chapters"] if MEM.get(sn,c)=="done")
    pbar(round(done_c/len(sd["chapters"])*100))
    st.caption(f"{done_c}/{len(sd['chapters'])} chapters done")
    cols = st.columns(4)
    for i,ch in enumerate(sd["chapters"]):
        st_ = MEM.get(sn,ch)
        icon = "✅" if st_=="done" else "🔄" if st_=="review" else "📌"
        with cols[i%4]:
            if st.button(f"{icon} {ch}", key=f"c{i}_{ch}", use_container_width=True):
                st.session_state.sel_ch   = ch
                st.session_state.ex_qs    = []
                st.session_state.ex_hints = None
                st.session_state.ai_sum   = None
                st.session_state.mock_qs  = None
                st.session_state.mock_done= False
                st.session_state.theory_qs= []
                st.rerun()

# ════════════════════════════════════════════════════════
# CHAPTER CONTENT
# ════════════════════════════════════════════════════════
if st.session_state.sel_ch and st.session_state.sel_subj:
    ch = st.session_state.sel_ch
    sn = st.session_state.sel_subj
    sd = SUBJECTS[sn]
    st.divider()

    # Header + Progress Buttons
    h1,h2 = st.columns([3,2])
    with h1:
        st.markdown(f"## {sd['icon']} {ch}")
        perf = PERF.analyze(sn,ch)
        if perf.get("attempts",0)>0:
            ti = "📈" if perf["trend"]=="improving" else "📉" if perf["trend"]=="declining" else "➡️"
            st.caption(f"{ti} {perf['attempts']} tests | Best:{perf['best']}% | Latest:{perf['latest']}% | Avg:{perf['avg']}%")
    with h2:
        st.markdown("**Mark Progress:**")
        b1,b2,b3 = st.columns(3)
        with b1:
            if st.button("✅ Done",key="md",use_container_width=True):
                MEM.mark(sn,ch,"done"); st.rerun()
        with b2:
            if st.button("🔄 Review",key="mr",use_container_width=True):
                MEM.mark(sn,ch,"review"); st.rerun()
        with b3:
            if st.button("↩️ Reset",key="mrst",use_container_width=True):
                MEM.mark(sn,ch,"pending"); st.rerun()

    # Build tabs
    tab_labels = ["📝 Study Material","🎥 Videos","🖼️ Diagrams","📓 My Notes"]
    tab_labels += ["🧮 Exercises"] if sd["num"] else ["📋 Theory Practice"]
    tab_labels += ["🧠 Mock Test","📊 Score History"]
    tabs = st.tabs(tab_labels)

    # ── TAB 0: STUDY MATERIAL ────────────────────────
    with tabs[0]:
        c1,c2 = st.columns([3,2])
        with c1:
            st.markdown("### 🌐 Web Search Results")
            st.markdown(f"<span class='agent-tag'>🔍 Quality Agent</span>", unsafe_allow_html=True)
            if st.button(f"🔍 Load Material for '{ch}'",key="lm"):
                with st.spinner("Searching & filtering..."):
                    try:
                        ddgs = DDGS(timeout=15)
                        raw  = list(ddgs.text(
                            query=f"ICSE class 8 {sn.split(' ',1)[1]} {ch} notes India",
                            region="in-en", safesearch="moderate", max_results=15))
                        filt = QUAL.run(raw, sn.split(' ',1)[1], ch)
                        st.session_state.text_res = filt
                        st.caption(f"Filtered: {len(raw)} → {len(filt)} results")
                    except Exception as e:
                        st.error(str(e))

            for i,r in enumerate(st.session_state.text_res[:8],1):
                ttl = r.get("title","")[:70]; body = r.get("body","")[:280]
                lnk = r.get("href","#")
                st.markdown(f"""<div style='background:#fff;border:1.5px solid #667eea33;
                    border-radius:12px;padding:14px 18px;margin-bottom:10px;
                    box-shadow:0 2px 8px rgba(102,126,234,0.08);'>
                    <div style='font-weight:700;font-size:0.95rem;color:#667eea;margin-bottom:6px;'>
                        {i}. {ttl}</div>
                    <div style='font-size:0.88rem;color:#555;line-height:1.6;'>{body}...</div>
                    <a href='{lnk}' target='_blank' style='display:inline-block;margin-top:8px;
                        font-size:0.82rem;color:#764ba2;font-weight:600;text-decoration:none;'>
                        🔗 Full Article ↗</a>
                </div>""", unsafe_allow_html=True)
                st.download_button(f"⬇️ Save #{i}", key=f"dl{i}",
                    data=f"Chapter:{ch}\nSubject:{sn}\n\nTitle:{r.get('title','')}\n\n{r.get('body','')}\n\nSource:{lnk}",
                    file_name=f"{ch.replace(' ','_')}_{i}.txt", mime="text/plain")

        with c2:
            st.markdown("### 🤖 AI Summary")
            st.markdown(f"<span class='agent-tag'>🤖 Summary Agent</span>", unsafe_allow_html=True)
            if st.session_state.ai_sum_ch != ch:
                st.session_state.ai_sum = None
            if not groq_api_key:
                st.warning("⚠️ API Key needed")
            else:
                if st.button("✨ Get AI Summary",key="asb"):
                    st.session_state.ai_sum = None
                    with st.spinner("AI thinking..."):
                        res = ORC.run("summary", subj=sn.split(' ',1)[1], ch=ch)
                        if isinstance(res,str):
                            st.session_state.ai_sum = res
                            st.session_state.ai_sum_ch = ch
                        else: st.error("Try again.")

            if st.session_state.ai_sum and st.session_state.ai_sum_ch==ch:
                st.markdown(f"<div class='info-box' style='white-space:pre-wrap;'>{st.session_state.ai_sum}</div>",
                            unsafe_allow_html=True)
                # HTML Download (Update #1)
                html = make_html(f"{ch} — AI Study Notes",
                    f"Subject: {sn.split(' ',1)[1]} | ICSE Class 8 | La Martiniere Girls",
                    st.session_state.ai_sum)
                st.download_button("⬇️ Download Summary (HTML)",
                    data=html, file_name=f"AI_Summary_{ch.replace(' ','_')}.html",
                    mime="text/html", key="dlsum")
                st.caption("💡 Opens in browser with full formatting")

            if st.session_state.tg_link:
                st.markdown(f"[📲 Share on Telegram](https://t.me/share/url?url={st.session_state.tg_link}&text=Check {ch} notes!)")

    # ── TAB 1: VIDEOS ─────────────────────────────────
    with tabs[1]:
        st.markdown("### 🎥 Video Lessons")
        if st.button("🔍 Find Videos",key="fv"):
            with st.spinner("Searching..."):
                try:
                    ddgs = DDGS(timeout=15)
                    st.session_state.vid_res = list(ddgs.videos(
                        query=f"ICSE class 8 {ch} {sn.split(' ',1)[1]} explanation",
                        region="in-en", safesearch="moderate", max_results=8))
                except Exception as e: st.error(str(e))

        for vid in st.session_state.vid_res:
            url = vid.get("content","")
            v1,v2 = st.columns([2,3])
            with v1:
                if url:
                    try: st.video(url)
                    except: st.markdown(f"[▶️ Watch]({url})")
            with v2:
                st.markdown(f"**{vid.get('title','')[:80]}**")
                if vid.get("duration"): st.caption(f"⏱️ {vid['duration']}")
                if vid.get("publisher"): st.caption(f"📺 {vid['publisher']}")
                if url: st.markdown(f"[🔗 YouTube]({url})")
            st.divider()

    # ── TAB 2: IMAGES ─────────────────────────────────
    with tabs[2]:
        st.markdown("### 🖼️ Diagrams & Images")
        if st.button("🔍 Find Diagrams",key="fi"):
            with st.spinner("Searching..."):
                try:
                    ddgs = DDGS(timeout=15)
                    st.session_state.img_res = list(ddgs.images(
                        query=f"ICSE class 8 {ch} diagram India",
                        region="in-en", safesearch="moderate", max_results=9))
                except Exception as e: st.error(str(e))

        if st.session_state.img_res:
            ic = st.columns(3)
            for idx,img in enumerate(st.session_state.img_res):
                with ic[idx%3]:
                    try:
                        st.image(img.get("image"), caption=img.get("title","")[:50], use_container_width=True)
                        st.markdown(f"[Source]({img.get('url','#')})")
                    except: st.markdown(f"[🖼️ View]({img.get('image','#')})")

    # ── TAB 3: MY NOTES ───────────────────────────────
    with tabs[3]:
        st.markdown("### 📓 My Personal Notes")
        existing = MEM.get_note(sn,ch)
        note = st.text_area(f"✏️ Notes — {ch}", value=existing, height=280,
            placeholder="• Key points\n• Formulas\n• Things to remember",
            key=f"note_{sn}_{ch}".replace(" ","_"))

        n1,n2,n3 = st.columns(3)
        with n1:
            if st.button("💾 Save",key="sn",use_container_width=True):
                MEM.save_note(sn,ch,note); st.success("✅ Saved!")
        with n2:
            if note:
                note_html = make_html(f"My Notes — {ch}",
                    f"{sn.split(' ',1)[1]} | ICSE Class 8", note, "#F6C90E")
                st.download_button("⬇️ Download Notes",
                    data=note_html, file_name=f"Notes_{ch.replace(' ','_')}.html",
                    mime="text/html", use_container_width=True, key="dln")
        with n3:
            if st.button("🗑️ Clear",key="cn",use_container_width=True):
                MEM.save_note(sn,ch,""); st.rerun()

        # Print-friendly complete sheet (Update #8)
        st.divider()
        st.markdown("**🖨️ Complete Study Sheet**")
        st.caption("AI Summary + Your Notes + Practice Questions — all in one HTML file")
        if st.button("📄 Generate & Download Complete Sheet",key="gs",use_container_width=True):
            if not groq_api_key:
                st.warning("API Key needed"); 
            else:
                with st.spinner("Building complete sheet..."):
                    summ = ORC.run("summary",subj=sn.split(' ',1)[1],ch=ch)
                    sheet = f"# {ch} — Complete Study Sheet\n\n"
                    sheet += "## AI Summary\n\n"
                    sheet += (summ if isinstance(summ,str) else "See resources") + "\n\n"
                    if note: sheet += f"## My Notes\n\n{note}\n\n"
                    if sd["num"]:
                        qs = ORC.run("questions",subj=sn.split(' ',1)[1],ch=ch,level="basic",mode="ai")
                        if isinstance(qs,list) and qs:
                            sheet += "## Practice Questions\n\n"
                            for i,q in enumerate(qs[:10],1): sheet += f"Q{i}. {q}\n\nAnswer: ____________________\n\n"
                    sheet_html = make_html(f"Complete Sheet — {ch}",
                        f"{sn.split(' ',1)[1]} | ICSE Class 8 | La Martiniere Girls", sheet)
                    st.download_button("⬇️ Download Complete Sheet",
                        data=sheet_html, file_name=f"Sheet_{ch.replace(' ','_')}.html",
                        mime="text/html", use_container_width=True, key="dls")
                    st.success("✅ Ready!")

        saved_notes = MEM.all_notes()
        if saved_notes: st.caption(f"📌 {len(saved_notes)} chapters have notes this session")

    # ── TAB 4: EXERCISES or THEORY ────────────────────
    if sd["num"]:
        with tabs[4]:
            st.markdown(f"### 🧮 Practice Exercises — {ch}")
            st.markdown(f"<span class='agent-tag'>🎯 Question Agent</span> Fresh unique questions every time", unsafe_allow_html=True)
            e1,e2 = st.columns(2)
            with e1:
                lc = st.radio("Level:",["🟢 Basic","🔴 Advanced"],key="elr")
                lv = "basic" if "Basic" in lc else "advanced"
            with e2:
                gm = st.radio("Mode:",["🤖 AI (Best)","⚡ Instant"],key="gmr")

            st.markdown(f"""<div class='info-box'>
                <b>{sn.split(' ',1)[1]} — {ch}</b> | Level: <b>{'Basic' if lv=='basic' else 'Advanced'}</b> | 10 fresh questions
            </div>""", unsafe_allow_html=True)

            if st.button("🎲 Generate 10 Questions",key="gex",type="primary"):
                st.session_state.ex_qs = []; st.session_state.ex_hints = None
                st.session_state.ex_ch = ch; st.session_state.ex_lv = lv
                st.session_state.ex_ts = datetime.now().strftime("%H:%M:%S")
                mode = "ai" if "AI" in gm else "local"
                with st.spinner("🤖 Generating..."):
                    qs = ORC.run("questions",subj=sn.split(' ',1)[1],ch=ch,level=lv,mode=mode)
                    st.session_state.ex_qs = qs if isinstance(qs,list) and qs else \
                        QAGENT._local(sn,ch,lv,[])

            if st.session_state.ex_qs and st.session_state.ex_ch==ch:
                qs = st.session_state.ex_qs
                lv_ = st.session_state.ex_lv or lv
                st.success(f"✅ {len(qs)} Questions [{lv_.capitalize()} — {st.session_state.ex_ts}]")
                ex_txt = f"Chapter:{ch}\nSubject:{sn}\nLevel:{lv_}\n\nPRACTICE QUESTIONS\n{'='*40}\n\n"
                for i,q in enumerate(qs,1):
                    st.markdown(f"<div class='question-box'><span class='q-number'>Q{i}.</span> {q}</div>",
                                unsafe_allow_html=True)
                    ex_txt += f"Q{i}. {q}\n\nAnswer: ____________________\n\n"

                st.divider()
                if groq_api_key and st.button("💡 Show Step-by-Step Solutions",key="shb"):
                    st.session_state.ex_hints = None
                    with st.spinner("Solving..."):
                        res = ORC.run("hints",subj=sn.split(' ',1)[1],questions=qs)
                        if isinstance(res,str): st.session_state.ex_hints = res
                        else: st.error("Try again")

                if st.session_state.ex_hints:
                    st.markdown("### 💡 Step-by-Step Solutions")
                    st.markdown(f"<div class='info-box' style='white-space:pre-wrap;font-size:0.9rem;'>{st.session_state.ex_hints}</div>",
                                unsafe_allow_html=True)
                    ex_txt += "\n\nSOLUTIONS\n" + "="*40 + "\n" + st.session_state.ex_hints

                st.divider()
                d1,d2,d3 = st.columns(3)
                with d1:
                    ex_html = make_html(f"Exercises — {ch}",
                        f"{sn.split(' ',1)[1]} | {lv_.capitalize()} | ICSE Class 8", ex_txt)
                    st.download_button("⬇️ Download HTML", data=ex_html,
                        file_name=f"Ex_{ch.replace(' ','_')}.html", mime="text/html",
                        use_container_width=True, key="dlex")
                with d2:
                    csv = "Q No,Question,Answer\n" + "\n".join(
                        [f'{i},"{q.replace(chr(34),chr(34)*2)}",""' for i,q in enumerate(qs,1)])
                    st.download_button("📊 Google Sheets CSV", data=csv,
                        file_name=f"{ch.replace(' ','_')}_{lv_}.csv", mime="text/csv",
                        use_container_width=True, key="dlcsv")
                with d3:
                    if st.session_state.tg_link:
                        prev = "\n".join([f"Q{i+1}. {q[:55]}..." for i,q in enumerate(qs[:3])])
                        st.link_button("📲 Telegram",
                            f"https://t.me/share/url?url={st.session_state.tg_link}&text=📚 {ch}\n{prev}",
                            use_container_width=True)
                    else:
                        st.button("📲 Telegram (set in sidebar)",disabled=True,use_container_width=True)
    else:
        with tabs[4]:
            st.markdown(f"### 📋 Theory Practice — {ch}")
            st.markdown(f"<span class='agent-tag'>📝 Theory Agent</span>", unsafe_allow_html=True)
            tl = st.radio("Level:",["📗 Basic","📕 Advanced"],key="tlr")
            tlv = "basic" if "Basic" in tl else "advanced"
            if st.button("🎯 Generate Theory Questions",key="gth",type="primary"):
                st.session_state.theory_qs = []
                with st.spinner("Generating..."):
                    res = ORC.run("theory",subj=sn.split(' ',1)[1],ch=ch,level=tlv)
                    st.session_state.theory_qs = res if isinstance(res,list) else []
                    st.session_state.ex_ch = ch

            if st.session_state.theory_qs and st.session_state.ex_ch==ch:
                qs = st.session_state.theory_qs
                th_txt = f"Chapter:{ch}\nSubject:{sn}\n\nTHEORY QUESTIONS\n{'='*40}\n\n"
                for i,q in enumerate(qs,1):
                    st.markdown(f"<div class='question-box'><span class='q-number'>Q{i}.</span> {q}</div>",
                                unsafe_allow_html=True)
                    th_txt += f"Q{i}. {q}\n\nAnswer: ____________________\n\n"
                th_html = make_html(f"Theory — {ch}", f"{sn.split(' ',1)[1]} | ICSE Class 8", th_txt)
                st.download_button("⬇️ Download Questions",data=th_html,
                    file_name=f"Theory_{ch.replace(' ','_')}.html",mime="text/html",key="dlth")

    # ── TAB 5: MOCK TEST ──────────────────────────────
    with tabs[5]:
        st.markdown("### 🧠 Mock Test — MCQ")
        st.markdown(f"<span class='agent-tag'>🧠 Mock Test Agent</span> AI-powered MCQ with scoring", unsafe_allow_html=True)
        m1,m2 = st.columns(2)
        with m1: mtime = st.selectbox("⏱️ Time:",  [5,10,15,20],index=1,key="mts")
        with m2: mdiff = st.selectbox("Difficulty:",["Easy","Medium","Hard"],index=1,key="mds")

        if st.button("🎯 Start Mock Test",key="smk",type="primary"):
            if not groq_api_key:
                st.error("❌ API Key needed!")
            else:
                st.session_state.mock_qs   = None
                st.session_state.mock_ans  = {}
                st.session_state.mock_done = False
                st.session_state.mock_t0   = time.time()
                st.session_state.mock_tlim = mtime*60
                with st.spinner("🤖 Generating MCQ test..."):
                    res = ORC.run("mock",subj=sn.split(' ',1)[1],ch=ch,difficulty=mdiff)
                    if isinstance(res,list) and res: st.session_state.mock_qs = res
                    else: st.error("❌ Failed. Try again.")

        if st.session_state.mock_qs and not st.session_state.mock_done:
            mcqs = st.session_state.mock_qs
            if st.session_state.mock_t0:
                left = max(0,int(st.session_state.mock_tlim-(time.time()-st.session_state.mock_t0)))
                ml,ms = divmod(left,60)
                tc = "#e74c3c" if left<60 else "#2ecc71"
                st.markdown(f"""<div style='background:{tc};color:white;border-radius:10px;
                    padding:10px;text-align:center;font-size:1.4rem;font-weight:800;
                    font-family:"Baloo 2",cursive;margin-bottom:15px;'>
                    ⏱️ {ml:02d}:{ms:02d}</div>""", unsafe_allow_html=True)
                if left==0: st.session_state.mock_done=True; st.rerun()
            st.markdown("---")
            for i,mcq in enumerate(mcqs):
                st.markdown(f"<div class='question-box'><span class='q-number'>Q{i+1}.</span> {mcq.get('q','')}</div>",
                            unsafe_allow_html=True)
                ch_ = st.radio(f"Q{i+1}",mcq.get("options",[]),key=f"mq{i}",label_visibility="collapsed")
                st.session_state.mock_ans[i] = ch_[0] if ch_ else ""
            st.divider()
            if st.button("✅ Submit Test",key="subm",type="primary",use_container_width=True):
                st.session_state.mock_done=True; st.rerun()

        if st.session_state.mock_done and st.session_state.mock_qs:
            mcqs = st.session_state.mock_qs
            ans  = st.session_state.mock_ans
            score= 0
            st.markdown("## 📊 Results")
            for i,mcq in enumerate(mcqs):
                ua  = ans.get(i,"")
                ca  = mcq.get("answer","").strip().upper()
                ok  = ua.strip().upper().startswith(ca)
                if ok: score+=1
                css = "mock-correct" if ok else "mock-wrong"
                st.markdown(f"""<div class='{css}'>
                    {'✅' if ok else '❌'} <b>Q{i+1}.</b> {mcq.get('q','')}<br>
                    Your: <b>{ua}</b>{'' if ok else f' | Correct: <b>{ca}</b>'}<br>
                    <small>{mcq.get('explanation','')}</small>
                </div>""", unsafe_allow_html=True)

            pct = round(score/len(mcqs)*100)
            grade = "🏆 Excellent!" if pct>=80 else "👍 Good!" if pct>=60 else "📚 Keep Practicing!" if pct>=40 else "💪 Needs Study"
            gc = "#2ecc71" if pct>=80 else "#f39c12" if pct>=60 else "#e74c3c"
            st.markdown(f"""<div style='background:{gc};color:white;border-radius:16px;
                padding:22px;text-align:center;margin:20px 0;font-family:"Baloo 2",cursive;'>
                <div style='font-size:2.5rem;font-weight:800;'>{score}/{len(mcqs)}</div>
                <div style='font-size:1.2rem;'>{pct}% — {grade}</div>
            </div>""", unsafe_allow_html=True)

            # Save to Performance Agent
            PERF.save(sn,ch,score,len(mcqs))
            MEM.mark(sn,ch,"review" if pct<60 else "done")
            st.markdown(f"<span class='agent-tag'>📊 Performance Agent</span> Score saved!", unsafe_allow_html=True)

            ra,rb = st.columns(2)
            with ra:
                if st.button("🔄 Try Again",key="rtry",use_container_width=True):
                    st.session_state.mock_qs=None; st.session_state.mock_done=False
                    st.session_state.mock_ans={}; st.rerun()
            with rb:
                if pct<60 and groq_api_key:
                    if st.button("🤖 Explain Weak Areas",key="ewa",use_container_width=True):
                        wrong = [mcqs[i].get('q','') for i,m in enumerate(mcqs)
                                 if not ans.get(i,"").upper().startswith(m.get("answer","").upper())]
                        with st.spinner("AI explaining..."):
                            res = llm(f"ICSE Class 8 student got these wrong: {wrong[:5]}. "
                                      f"Explain each concept clearly in simple English. Chapter: {ch}",
                                      temp=0.5, tokens=1000)
                            if res:
                                st.markdown("### 🧠 AI Explanation")
                                st.markdown(f"<div class='info-box'>{res}</div>",unsafe_allow_html=True)

    # ── TAB 6: SCORE HISTORY ──────────────────────────
    with tabs[6]:
        st.markdown("### 📊 Score History")
        st.markdown(f"<span class='agent-tag'>📊 Performance Agent</span>", unsafe_allow_html=True)
        perf = PERF.analyze(sn,ch)

        if perf.get("attempts",0)==0:
            st.info("📝 No mock tests yet. Take a test to see history!")
        else:
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("Attempts",   perf["attempts"])
            s2.metric("Best",       f"{perf['best']}%")
            s3.metric("Latest",     f"{perf['latest']}%")
            s4.metric("Average",    f"{perf['avg']}%")

            ti = "📈 Improving!" if perf["trend"]=="improving" else "📉 Declining" if perf["trend"]=="declining" else "➡️ Stable"
            st.info(f"Trend: {ti}")

            st.markdown("**All Attempts:**")
            for i,h in enumerate(reversed(perf["history"]),1):
                pct = h.get("pct",0)
                bc  = "#2ecc71" if pct>=80 else "#f39c12" if pct>=60 else "#e74c3c"
                st.markdown(f"""<div class='score-row' style='display:flex;justify-content:space-between;'>
                    <span>Attempt {perf['attempts']-i+1} — {h.get('time','')}</span>
                    <span style='color:{bc};font-weight:700;'>{h.get('score',0)}/{h.get('total',10)} ({pct}%)</span>
                </div>""", unsafe_allow_html=True)

            if len(perf["history"])>1:
                st.markdown("**Score Trend:**")
                scores = [h.get("pct",0) for h in perf["history"]]
                mx = max(scores) or 1
                bars = "<div style='display:flex;align-items:flex-end;gap:4px;height:80px;padding:4px;'>"
                for s in scores:
                    h_ = max(8,int(s/mx*100))
                    bc = "#2ecc71" if s>=80 else "#f39c12" if s>=60 else "#e74c3c"
                    bars += f"<div style='flex:1;background:{bc};height:{h_}%;border-radius:4px 4px 0 0;' title='{s}%'></div>"
                bars += "</div>"
                st.markdown(bars, unsafe_allow_html=True)
                st.caption("Bars: oldest → latest attempt")

# ════════════════════════════════════════════════════════
# WELCOME SCREEN
# ════════════════════════════════════════════════════════
if not st.session_state.sel_subj:
    st.divider()
    c1,c2,c3,c4 = st.columns(4)
    wdata = [
        (c1,"english-card","📖 English Grammar","Tenses, Voice, Speech","15 ch"),
        (c1,"history-card","🏛️ History","ICSE India & World","12 ch"),
        (c2,"maths-card","➕ Mathematics","Algebra, Geometry + Exercises","20 ch"),
        (c2,"geography-card","🌍 Geography","India, World, Resources","12 ch"),
        (c3,"physics-card","⚡ Physics","Force, Sound, Light + Exercises","12 ch"),
        (c3,"chemistry-card","🧪 Chemistry","Atoms, Reactions, Acids","12 ch"),
        (c4,"biology-card","🌿 Biology","Cells, Body, Ecosystem","11 ch"),
        (c4,"computer-card","💻 Computer","Java, HTML, Networks","11 ch"),
    ]
    for col,cls,ttl,desc,cnt in wdata:
        with col:
            st.markdown(f"""<div class='subject-card {cls}'>
                <h3 style='margin:0 0 5px;'>{ttl}</h3>
                <p style='font-size:0.85rem;margin:0 0 5px;color:#555;'>{desc}</p>
                <small style='color:#888;'>{cnt}</small>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div style='background:linear-gradient(135deg,#667eea15,#764ba215);
        border-radius:16px;padding:22px;margin-top:20px;text-align:center;border:2px dashed #667eea44;'>
        <h3 style='font-family:"Baloo 2",cursive;'>🚀 How to Use StudyMate</h3>
        <p>1️⃣ <b>Subject चुनो</b> → 2️⃣ <b>Chapter click करो</b> → 3️⃣ <b>Study, Practice & Test!</b></p>
        <p>🤖 <b>8 AI Agents</b> — Quality filter, smart questions, performance tracking & personalization</p>
        <p>📊 Score History | 📓 Notes | ⏱️ Pomodoro | 📅 Exam Countdown | 🖨️ Print Sheets | 🧠 Mock Test</p>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""<div style='text-align:center;color:#888;font-size:0.85rem;padding:10px;'>
    Made with ❤️ for <b>La Martiniere Girls College</b> | ICSE Class 8 |
    Powered by <b>Groq llama-3.3-70b + 8 AI Agents + ddgs</b> 🚀<br>
    <small>📌 Free Resources:
    <a href='https://console.groq.com/keys' target='_blank'>Groq API</a> |
    <a href='https://www.topperlearning.com' target='_blank'>TopperLearning</a> |
    <a href='https://www.vedantu.com' target='_blank'>Vedantu</a></small>
</div>""", unsafe_allow_html=True)
