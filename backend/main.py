########PASSWORD KO DIRECT JESE USER DE RHA H WESW SAVE NHI KR SKTE RISKY H ISLIYE USSE HASING FORM ME SAVE KRTA H JESE sdhf9834hfsd9f8sd.. ISSE REVERSE NHI KR SKTE ISLIYE EK LIBRARY INSTALL KRTE H PASSLIB[BCRYPT]

from fastapi import FastAPI, File, UploadFile  #uploadfile is similarly as string jo file ko handle krti h or isse hee hme file.filename bgera milta h and file wo h jha se file jayegi apne api me
import os
from PyPDF2 import PdfReader     # isse pdf ko text me convert kr skenge
from typing import List, Optional    #python se datatype clear nhi hota laken fastapi k iye ye bhut jroori h isliye iska use krte h ki list h or kis datatypre ki h
from pydantic import BaseModel    #BaseModel ek rule-maker hai  Jo bolta hai:“API ko jo data milega, wo aisa hi hona chahiye”
import difflib  #ye string ya text me similarty check krta h ki konsa word aapas me kitna match ho rha h 
import re   # ye text ko todne and clean krne me use hota h
from fastapi.responses import FileResponse  #pdf bnane k baad browser ko pdf isi se bhejte h
from fastapi.middleware.cors import CORSMiddleware    #actually hota ye h ki frontend call krta h backend ko laken backend permission dega tbhi procedure aage bdega
# or ye sb browser ki CORS security k andar aata h islie hm fastapi se CORSMIDDLEWARE ko import krte h jo ki browser se aane wali hr request ko allow krta h
from starlette.middleware.sessions import SessionMiddleware

# PIP SE REPORTLAB INSTALL KIYA H TB YE BEECHE KI LIBRABY IMPORT HUII H 
# YE SB RESUME MAKER K LIYE KR RHE H
from reportlab.lib.pagesizes import A4   #isse A4 size paper aata h
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle # isse hme readymade text style milti h jese title, heading,normal etc
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,HRFlowable  #SimpleDocTemplat iske bina toh pdf ban hee nhi skti h isse ek khali notebook ki trah assume krlo, or pdf me space and paragraph likhne k liye paragraph and spacer ko import kiya h, HRFlowable isse hee pdf me lining bgera aati h 
from reportlab.lib.enums import TA_LEFT, TA_CENTER  #isse text alingnment hota h center me left, right me
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.colors import black,HexColor
from reportlab.platypus import Table, TableStyle

#ye sb importing login me data store krne k liye database bnane k liye kr rhe h
import sqlite3
from passlib.context import CryptContext   #isse hee password encrypt hota h

#for login
from fastapi import Body
from fastapi import Request

#For google login
from dotenv import load_dotenv   #env me google k password bgera rehte h unhe python ko pdne k liye ye library import krte h
from authlib.integrations.starlette_client import OAuth #isi k through hm google se baat krte h
from fastapi.responses import RedirectResponse  #google ko ek url se duusre url pr bhejne kakaam krta h


app = FastAPI()
LAST_RESUME_SKILLS = []   #ye ek global variable banya h jo last upload resume k skills ko store krega jisko hm job description se compare krenge

load_dotenv()  #isse python ne env file pdli h
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500",
        "https://your-frontend-domain.com"],        # sab origins allow (development) means kisi website se request aaye toh allow krde
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, etc.
    allow_headers=["*"],
)



class JobMatchRequest(BaseModel):   #ye basemodel h jo batata h ki fastapi me only kis datatype ka input jayega
    job_description: str



def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)
    pages_text = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            clean_text = text.replace("\n", " ").strip()
            pages_text.append(clean_text)

    return "\n\n".join(pages_text)



SECTION_TITLES = [
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "extra curricular and achievements"
]
def extract_sections(resume_text: str):    #isse hme sections ki ek dictionary mil gyi
    lower_text = resume_text.lower()
    sections = {}
    indexes = {}

    for title in SECTION_TITLES:
        idx = lower_text.find(title)
        if idx != -1:
            indexes[title] = idx

    sorted_sections = sorted(indexes.items(), key=lambda x: x[1])

    for i in range(len(sorted_sections)):
        title, start = sorted_sections[i]

        if i + 1 < len(sorted_sections):
            end = sorted_sections[i + 1][1]
        else:
            end = len(resume_text)

        sections[title] = resume_text[start:end].strip()

    return sections



def parse_skills(skills_text: str):
    if not skills_text:
        return []

    skills = []

    # Remove heading word
    text = skills_text.replace("Skills", "").replace("skills", "")

    # Step 1: Bullet based split (if exists)
    parts = text.split("•") if "•" in text else [text]

    for part in parts:
        # Step 2: Dash based split (if exists)
        if "—" in part:
            part = part.split("—", 1)[1]

        # Step 3: Comma based split
        for skill in part.split(","):
            clean = skill.strip()

            # safety filters
            if 1 < len(clean) < 40:
                skills.append(clean)

    # remove duplicates
    return list(set(skills))




def parse_experience(exp_text: str):
    if not exp_text:
        return []

    experiences = []

    # Clean heading
    text = exp_text.replace("EXPERIENCE", "").replace("Experience", "")

    # Split on bullet-like separators
    parts = text.split("−")

    for part in parts:
        part = part.strip()

        # Look for Role — Company pattern
        if "—" in part:
            role_part, rest = part.split("—", 1)

            role = role_part.strip()

            # Company may include date, so clean it
            company = rest.split("(")[0].strip()

            if len(role) > 2 and len(company) > 2:
                experiences.append({
                    "role": role,
                    "company": company
                })

    # Fallback safety
    if not experiences:
        return [{"raw_experience": exp_text}]

    return experiences




def parse_education(edu_text: str):
    if not edu_text:
        return {}

    lines = [l.strip() for l in edu_text.split("\n") if l.strip()]

    if len(lines) >= 2:
        return {
            "degree": lines[1],
            "institute": lines[2] if len(lines) > 2 else ""
        }

    return {"raw_education": edu_text}



def parse_other_section(text: str):
    if not text:
        return ""

    clean = text.replace("\n", " ").strip()
    return clean



def extract_skills_from_jd(job_description: str):
    text = job_description.lower()

    # Replace separators with space
    text = re.sub(r"[,\n;/•\-]", " ", text)

    words = text.split()

    stop_words = {
        "looking", "for", "an", "a", "the", "with", "and", "or",
        "intern", "developer", "engineer", "required", "skills",
        "skill", "role", "position", "experience", "knowledge",
        "in", "of", "to", "is", "are"
    }

    skills = []

    for word in words:
        clean = word.strip()

        # filters
        if (
            clean not in stop_words and
            len(clean) > 2 and
            not clean.isdigit()
        ):
            skills.append(clean)

    return list(set(skills))



def normalize_skill(text: str):
    text = text.lower().strip()

    # common normalizations (NO hard assumptions)
    replacements = {
        "c plus plus": "c++",
        "cpp": "c++",
        "js": "javascript",
        "nodejs": "node",
        "node.js": "node",
        "machine learning": "ml",
        "deep learning": "dl"
    }
    for k, v in replacements.items():
        if text == k:
            return v

    return text



def is_similar(a: str, b: str, threshold: float = 0.75) -> bool:
    return difflib.SequenceMatcher(None, a, b).ratio() >= threshold   #sequencemaker difflib ka ek code h jo ki 2 string ko compare krta h and ratio ko match krta h mene isme ye kiya h ki agar ratio, thresold se jyada hoga tbhi return krega



UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):  #isse upload wale folder ka path check hoga ki wo backend k andar exist krta h ya nhi
    os.makedirs(UPLOAD_DIR)         # agar nhi krta hoga toh iss line of code se wo folder ban jayega



@app.get("/")         #ye toh apna whi kaam krta h ki apna backened chl rha h ya nhi
def root():
    return {"status": "Backend is running"}



#ye hmne ek API bnaya h jisse hm resume ko upload kr rhe h and usme se data ko extract krk clean kr rhe h
@app.post("/upload-resume/")       # isse file post k through upload huii
async def upload_resume(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":      # isse pta chlta h ki file kis type ki h pdf jpg etc agr pdf ko chodkar kisi or type ki h toh function aagre run nhi krega
        return {"error": "Only PDF files are allowed"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)     #ab apna file type check ho gya uske baad file.filename se file ka name and UPLOAD_DIR se uploads me and os.path.join se path ban gya h ki backened/uploads/file chli jaye

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    text = extract_text_from_pdf(file_path)  #isse jo upper pdf ko text me convert krne ka function banaya h usko call kiya h
    

    sections = extract_sections(text)    #iss wale function se apne paas jo data ek string me tha wo ab divide ho gya h sectionss me jese skill, experience etc.

    parsed_data = {}

    for section, content in sections.items():
        if section == "skills":
            parsed_data["skills"] = parse_skills(content)

        elif section == "experience":
            parsed_data["experience"] = parse_experience(content)

        elif section == "education":
            parsed_data["education"] = parse_education(content)

        else:
            parsed_data[section] = parse_other_section(content)
    global LAST_RESUME_SKILLS
    LAST_RESUME_SKILLS = parsed_data.get("skills", [])

    
    return {
    "message": "Resume processed successfully",
    "filename": file.filename,
    "sections": sections,
    "parsed_data": parsed_data
}



@app.post("/match-job/")   #isse hmne ek or API banay h jisse hum job description and resume me jop skills h unhe compare kr rhe h
async def match_job(data: JobMatchRequest):    #isse hee hm job description le rhe h via basemodel
   
    global LAST_RESUME_SKILLS

    if not LAST_RESUME_SKILLS:
        return {"error": "No resume uploaded yet"}

    job_desc = data.job_description.strip()

    if not job_desc or len(job_desc) < 10:
        return {"error": "Please provide a valid job description (minimum 10 characters)"}

    jd_skills = [normalize_skill(s) for s in extract_skills_from_jd(data.job_description)] #isse function call ho rha h jisme jo job description h usme jo skill h wo hmare paas aa jaati h
    
    if not jd_skills:
        return {
            "match_score": None,
            "message": "Job description does not specify required skills clearly"
        }
    
    resume_skills = [normalize_skill(s) for s in LAST_RESUME_SKILLS]

    matched = []
    missing = []

    for jd_skill in jd_skills:
        found = False

        for res_skill in resume_skills:
            if jd_skill == res_skill or is_similar(jd_skill, res_skill):
                matched.append(jd_skill)
                found = True
                break

        if not found:
            missing.append(jd_skill)



    raw_score = (len(matched) / len(jd_skills)) * 100

    if raw_score > 0 and raw_score < 30:
        match_score = 30
    else:
        match_score = int(raw_score)

    if len(matched) >= 3:
        match_score = min(match_score + 10, 100)


    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
    }


# YHA SE RESUME MAKER KA KAAM SHURU HOTA H API BNANE KA

class ExperienceItem(BaseModel):
    title: str
    company: str
    duration: str
    points: List[str]

class ProjectItem(BaseModel):
    title: str
    points: List[str]

class ResumeCreateRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    skills: List[str]
    education: List[str]
    experience: Optional[List[ExperienceItem]] = []
    projects: Optional[List[ProjectItem]] = []
    extra: Optional[str] = ""
    template: str 


#YE PUURE FUNCTION SE CLASSIC RESUME PDF FORM ME BNEGA
def create_resume_pdf(data: ResumeCreateRequest, file_path: str):
    doc = SimpleDocTemplate(  # simpledoctemplate ek empty pdf file h
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    # NAME
    name_style = styles["Title"]
    name_style.alignment = TA_CENTER
    content.append(Paragraph(data.full_name, name_style))
    content.append(Spacer(1, 12))

    # CONTACT
    contact = f"{data.email} | {data.phone} | {data.location}"
    content.append(Paragraph(contact, styles["Normal"]))
    content.append(Spacer(1, 16))

    # SKILLS
    content.append(Paragraph("<b>SKILLS</b>", styles["Heading2"]))

    content.append(HRFlowable(
        width="100%",
        thickness=1.5,
        color="#7adae1",
        spaceBefore=6,
        spaceAfter=10
    ))

    skill_bullets = [
        Paragraph(skill, styles["Normal"])
        for skill in data.skills
    ]

    content.append(
        ListFlowable(
            skill_bullets,
            bulletType="bullet",
            start="circle",
            leftIndent=20
        )
    )

    content.append(Spacer(1, 14))

    # EDUCATION
    content.append(Paragraph("<b>EDUCATION</b>", styles["Heading2"]))
    content.append(HRFlowable(width="100%", thickness=1.5, color="#7adae1"))     # isse hee pdf me skills, experience k neeche blue line aati h
    for edu in data.education:
        content.append(Paragraph(f"- {edu}", styles["Normal"]))
    content.append(Spacer(1, 14))

    # EXPERIENCE
    if data.experience:
        content.append(Paragraph("<b>EXPERIENCE</b>", styles["Heading2"]))
        content.append(HRFlowable(width="100%", thickness=1.5, color="#7adae1"))     # isse hee pdf me skills, experience k neeche blue line aati h

        for exp in data.experience:
         # Title bold
            header = f"<b>{exp.title}</b> — {exp.company} ({exp.duration})"
            content.append(Paragraph(header, styles["Normal"]))
            content.append(Spacer(1, 6))

            bullets = [
                Paragraph(point, styles["Normal"])
                for point in exp.points
            ]

            content.append(
                ListFlowable(
                    bullets,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=20
                )
            )

            content.append(Spacer(1, 12))

    # PROJECTS
    if data.projects:
        content.append(Paragraph("<b>PROJECTS</b>", styles["Heading2"]))
        content.append(HRFlowable(width="100%", thickness=1.5, color="#7adae1"))     # isse hee pdf me skills, experience k neeche blue line aati h

        for proj in data.projects:
            content.append(
                Paragraph(f"<b>{proj.title}</b>", styles["Normal"])
            )
            content.append(Spacer(1, 6))

            bullets = [
                Paragraph(p, styles["Normal"])
                for p in proj.points
            ]

            content.append(
                ListFlowable(
                    bullets,
                    bulletType="bullet",
                    leftIndent=20
                )
            )

            content.append(Spacer(1, 12))

    # EXTRA
    if data.extra:
        content.append(Paragraph("<b>EXTRA-CURRICULAR & ACHIEVEMENTS</b>", styles["Heading2"]))
        content.append(HRFlowable(width="100%", thickness=1.5, color="#7adae1"))
        content.append(Paragraph(data.extra, styles["Normal"]))

    doc.build(content)  #content ek list h jisme puura information h or doc.build se hee final pdf banti h (ReportLab imports PDF banane ke tools dete hain, create_resume_pdf() resume data ko Paragraphs aur Spacers me tod kar ek list banata hai, aur doc.build() us list ko real PDF file me convert kar deta hai)

#ISSE MODERN TEMPLATE ME PDF BNEGA 
def create_modern_resume_pdf(data: ResumeCreateRequest, file_path: str):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    content = []

    # COLORS
    HEADER_BG = HexColor("#dbe9ea")
    ACCENT = HexColor("#2f7f86")
    TEXT = HexColor("#333333")

    # ---------------- HEADER ----------------
    name_style = ParagraphStyle(
        "name",
        fontSize=26,
        leading=30,
        spaceAfter=6,
        textColor=TEXT,
        fontName="Helvetica-Bold"
    )

    sub_style = ParagraphStyle(
        "sub",
        fontSize=10,
        leading=14,
        textColor=TEXT
    )

    header = Table(
        [[
            Paragraph(data.full_name, name_style),
        ]],
        colWidths=[doc.width],
        rowHeights=[55]   # 🔥 FIXES OVERLAP
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ]))

    content.append(header)

    # CONTACT LINE
    contact = f"{data.email} | {data.phone} | {data.location}"
    content.append(Spacer(1, 8))
    content.append(Paragraph(contact, sub_style))
    content.append(Spacer(1, 20))

    # ---------- SECTION STYLE ----------
    section_style = ParagraphStyle(
        "section",
        fontSize=13,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    normal = ParagraphStyle(
        "normal",
        fontSize=10,
        leading=14,
        textColor=TEXT
    )

    # ---------------- PROFILE ----------------
    content.append(Paragraph("PROFILE", section_style))
    content.append(
    HRFlowable(
        width="100%",
        thickness=1.2,
        color=ACCENT,
        spaceBefore=4,
        spaceAfter=8
    )
)
    content.append(Paragraph(data.extra or "Professional summary", normal))

    # ---------------- EXPERIENCE ----------------
    if data.experience:
        content.append(Paragraph("PROFESSIONAL EXPERIENCE", section_style))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
        for exp in data.experience:
            content.append(
                Paragraph(
                    f"<b>{exp.title}</b> — {exp.company} ({exp.duration})",
                    normal
                )
            )
            bullets = [Paragraph(p, normal) for p in exp.points]
            content.append(ListFlowable(bullets, leftIndent=14))
            content.append(Spacer(1, 8))

    # ---------------- PROJECTS ----------------
    if data.projects:
        content.append(Paragraph("PROJECTS", section_style))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
        for proj in data.projects:
            content.append(
                Paragraph(f"<b>{proj.title}</b>", normal)
            )
            bullets = [Paragraph(p, normal) for p in proj.points]
            content.append(ListFlowable(bullets, leftIndent=14))
            content.append(Spacer(1, 6))

    # ---------------- EDUCATION ----------------
    content.append(Paragraph("EDUCATION", section_style))
    content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
    for edu in data.education:
        content.append(Paragraph(edu, normal))

    # ---------------- SKILLS ----------------
    content.append(Paragraph("SKILLS", section_style))
    content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
    content.append(
        Paragraph(" | ".join(data.skills), normal)
    )

    doc.build(content)



#ISSE PUURA MINIMAL FORM ME PDF BNEGA
def create_minimal_resume_pdf(data: ResumeCreateRequest, file_path: str):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=40,
        bottomMargin=40
    )

    # COLORS
    name_color = HexColor("#3a3a3a")
    heading_color = HexColor("#2f7f86")
    text_color = HexColor("#555555")
    line_color = HexColor("#dbe9ea")
    ACCENT = HexColor("#2f7f86")

    styles = getSampleStyleSheet()

    # CUSTOM STYLES
    styles.add(ParagraphStyle(
        name="NameStyle",
        fontSize=24,
        leading=28,
        textColor=name_color,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="ContactStyle",
        fontSize=10,
        textColor=text_color,
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="HeadingStyle",
        fontSize=13,
        textColor=heading_color,
        spaceBefore=18,
        spaceAfter=6,
        letterSpacing=1,
        leading=16
    ))

    styles.add(ParagraphStyle(
        name="BodyStyle",
        fontSize=10.5,
        textColor=text_color,
        leading=15,
        spaceAfter=6
    ))

    content = []

    # =========================
    # NAME
    # =========================
    content.append(Paragraph(data.full_name.upper(), styles["NameStyle"]))

    # CONTACT 
    contact_line = f"{data.email} | {data.phone} | {data.location}"
    content.append(Paragraph(contact_line, styles["ContactStyle"]))
    content.append(HRFlowable(
        width="100%",
        thickness=1,
        color=ACCENT,
        spaceAfter=16
    ))

    # =========================
    # SKILLS
    # =========================
    content.append(Paragraph("SKILLS", styles["HeadingStyle"]))
    content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                 color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
    skills_text = ", ".join(data.skills)
    content.append(Paragraph(skills_text, styles["BodyStyle"]))

    # =========================
    # EXPERIENCE
    # =========================
    if data.experience:
        content.append(Paragraph("EXPERIENCE", styles["HeadingStyle"]))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
        for exp in data.experience:
            title = f"<b>{exp.title}</b> — {exp.company}"
            content.append(Paragraph(title, styles["BodyStyle"]))
            
            content.append(Paragraph(exp.duration, styles["BodyStyle"]))

            bullets = [
                Paragraph("• " + point, styles["BodyStyle"])
                for point in exp.points
            ]

            for b in bullets:
                content.append(b)

    # =========================
    # PROJECTS
    # =========================
    if data.projects:
        content.append(Paragraph("PROJECTS", styles["HeadingStyle"]))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )

        for proj in data.projects:
            content.append(
                Paragraph(f"<b>{proj.title}</b>", styles["BodyStyle"])
            )
            for p in proj.points:
                content.append(
                    Paragraph("• " + p, styles["BodyStyle"])
                )

    # =========================
    # EDUCATION
    # =========================
    if data.education:
        content.append(Paragraph("EDUCATION", styles["HeadingStyle"]))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
        for edu in data.education:
            content.append(Paragraph(edu, styles["BodyStyle"]))

    # =========================
    # EXTRA
    # =========================
    if data.extra:
        content.append(Paragraph(
            "EXTRA CURRICULAR & ACHIEVEMENTS",
            styles["HeadingStyle"]
        ))
        content.append(
            HRFlowable(
                width="100%",
                thickness=1.2,
                color=ACCENT,
                spaceBefore=4,
                spaceAfter=8
            )
        )
        content.append(Paragraph(data.extra, styles["BodyStyle"]))

    # BUILD PDF
    doc.build(content)



@app.post("/generate-resume/")
def generate_resume(data: ResumeCreateRequest):
    filename = f"resume_{data.full_name.replace(' ', '_')}.pdf"
    file_path = f"uploads/{filename}"

#isse template k according pdf bnegi

    if data.template == "classic":             # isse pdf file disk pr bn jaati h laken user tk pauchti nhi h kyuki ye function kuch bhi return nhi kr rh ah
        create_resume_pdf(data, file_path)

    elif data.template == "modern":
        create_modern_resume_pdf(data, file_path)

    elif data.template == "minimal":
        create_minimal_resume_pdf(data, file_path)

    return FileResponse(  #pdf file path ki wjah se yha exist krti h toh usko user tk pauchane ka kaamfileresponse ka hota h (Disk se file read karta hai,Usko binary data me convert karta hai,HTTP headers set karta hai:Content-Type: application/pdf)
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )



#YHA SE PUURA LOGIN with email and password KA CODE SHURU HOTA H 


conn = sqlite3.connect("users.db", check_same_thread=False)#sqlite3.connect connection bnane k liye use krte h agar user.db exist krta h toh theek agar nhi krta toh bna dega
cursor = conn.cursor() #conn.cursor database k andar command chlane wala like table bnana, data insert krna

#isse agar table nhi bn rhi h toh bna dega
cursor.execute("""            
CREATE TABLE IF NOT EXISTS users (         
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
#UPPER KI LINES KA EXPLANATION
# id INTEGER PRIMARY KEY AUTOINCREMENT :- isse har user ko alag alag number milenge 1,2,3...
#email TEXT UNIQUE NOT NULL:- unique se duplicate id nhi aayegi and not null se emil empty nhi rhega
#password TEXT NOT NULL:- password encrypted form me save hoga and empty nhi hoga


conn.commit()      #ye database ko bolta h ki jo changes kiye h unhe permanent save krdo

# PASSWORD HASHING
pwd_context = CryptContext(
    schemes=["bcrypt"],        #industry based standard hasing algo
    deprecated="auto"      # agar future me better algo aaye auto upgrade
)
def hash_password(password: str) -> str:        #user ka original password lega and hashed password return krega and database me sirf ye save hoga
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:  #login time pr user password and hased password ko compare krega 
    return pwd_context.verify(plain_password, hashed_password)


#login API BNI H YHA
# login me user ka password register k through already hota h isme hm uss password ko verify krte h
@app.post("/login/email")
def email_login(data: dict = Body(...)):
    email = data.get("email")
    password = data.get("password")

    cursor.execute(     #register se table me password hash form me store ho gya h and isse wo iss email ka password le lega hash form me yha pr
        "SELECT password FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()  #agar email nhi h toh isse none mil jayega nhi toh password isme store ho jayega

    if not user:
        return {"success": False, "message": "User not found or register first"}

    hashed_password = user[0]

    if verify_password(password, hashed_password):
        return {
            "success": True,
            "user": {"email": email}
        }

    return {"success": False, "message": "Invalid password"}



#register me password database me enter hota h isme verify nhi hota h
#REGISTER API HERE
@app.post("/register")
def register_user(data: dict = Body(...)):
    email = data.get("email")
    password = data.get("password")

#ye  correct gmail format check krne k liye
    def is_valid_email(email: str) -> bool:
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        return re.match(pattern, email) is not None


    if not email or not password:
        return {"success": False, "message": "Email and password required"}

    if not is_valid_email(email):
        return {
            "success": False,
            "message": "Invalid email format"
        }

    if len(password) > 50:
        return {
            "success": False,
            "message": "Password too long (max 50 characters)"
        }

    hashed_password = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()
        return {"success": True, "message": "User registered successfully"}

    except sqlite3.IntegrityError:
        return {"success": False, "message": "Email already registered"}



#for google login

oauth = OAuth()  #ab ye google ko request bhej sktah h isi se google se baat kr payenge
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",  #is url se authlib ko pta chlta h login url, token url
    client_kwargs={"scope": "openid email profile"}, #google se hm ye data maang rhe h
)


@app.get("/login/google")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")  #ye wo url h jispr user wapis aayega login k baad
    return await oauth.google.authorize_redirect(request, redirect_uri) #user ko login page pr bhejta h and browser me google ka screen khul jaata h and email select krna ka option isi ki wjah se aata h


@app.get("/login/google/callback") #google login successful hone k baad khud is url pr aa jta h
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request) #ye google se acess token leta h ki ye user verified h
    user_info = token.get("userinfo")

    if not user_info:
        return {"success": False, "message": "Google login failed"}

    email = user_info["email"]

    #CHECK DB    
    cursor.execute(      #isne db me check kiya ki ye email pehle se toh nhi h
        "SELECT email FROM users WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        # AUTO REGISTER
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, "GOOGLE_LOGIN")
        )
        conn.commit()

    # Frontend redirect
    return RedirectResponse(
        url=f"http://127.0.0.1:5500/frontend/index.html?google_login_success=true&email={email}"
)
