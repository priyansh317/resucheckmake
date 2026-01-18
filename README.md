# RESUCHECKMAKE 🚀  
### AI Resume Checker & Resume Builder (ATS-Optimized)

RESUCHECKMAKE is a full-stack AI-powered web application that helps job seekers analyze, improve, and build professional resumes that are optimized for Applicant Tracking Systems (ATS).

This platform combines **resume analysis**, **job matching**, and **resume creation** into a single, easy-to-use tool—similar to real-world products like Novoresume and Enhancv.

---

## ✨ Features

### 🔍 AI Resume Checker
- Upload resume in **PDF format**
- Automatic text extraction from resume
- Match resume skills with job description
- Calculate **ATS Match Score**
- Display:
  - ✅ Matched Skills  
  - ❌ Missing Skills  

---

### 📝 Resume Builder
- Build resume from scratch
- Structured inputs for:
  - Personal details
  - Skills
  - Education
  - Experience
  - Projects
  - Extra-curricular activities
- Live resume preview
- Download resume as **professional PDF**

---

### 🎨 Resume Templates
Choose from multiple ATS-friendly templates:

- **Classic**  
  Best for freshers, corporate roles, and traditional industries  

- **Modern**  
  Ideal for tech roles, startups, and creative professionals  

- **Minimal**  
  Clean, focused, and highly ATS-optimized design  

Each template provides:
- Accurate preview & PDF output
- Professional fonts, spacing, and colors
- Clear section separation for recruiters

---

### 🔐 Authentication & Security
- Email & password authentication
- Password hashing using **bcrypt**
- SQLite database for users
- Google OAuth login support
- Secure sessions and CORS protection

---

## 🧠 Tech Stack

### Frontend
- HTML5  
- CSS3  
- JavaScript (Vanilla)  
- LocalStorage  

### Backend
- Python  
- FastAPI  
- ReportLab (PDF generation)  
- PyPDF2 (PDF text extraction)  
- SQLite  

### Security
- Passlib (bcrypt hashing)  
- Google OAuth (Authlib)  
- Session Middleware  
- CORS Middleware  

---

## 📂 Project Structure


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/resucheckmake.git
cd resucheckmake
2️⃣ Backend Setup
cd backend
pip install -r requirements.txt


Create a .env file:

SESSION_SECRET=your_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/login/google/callback
```
---

## 🔁 Application Flow
- User logs in (Email / Google)
- Selects a resume template
- Enters resume details
- Live resume preview is generated
- PDF resume is created via backend
- Resume is downloaded
- Resume is matched against job description

---

## 🔐 Security Highlights
- Passwords are never stored in plain text
- Bcrypt hashing ensures irreversible encryption
- Secure API communication
- Session-based authentication

---

## 🔐 Authentication & Security
- Email & password authentication
- Password hashing using **bcrypt**
- SQLite database for user storage
- Google OAuth login support
- Secure sessions and CORS protection

---

## 🚀 Features
- ATS resume score calculation
- Job description keyword matching
- Missing & matched skills analysis
- Live resume preview
- Professional PDF resume generation
- Multiple resume templates:
  - Classic
  - Modern
  - Minimal

---

## 🔮 Future Improvements
- AI-based resume suggestions
- Multiple experience & project blocks
- User dashboard
- Resume version history
- Cloud deployment

---

## 👨‍💻 Author
**Priyansh**  
📧 Email: [support@resucheckmake.com](mailto:support@resucheckmake.com)

---

## 📜 License
This project is created for **educational and portfolio purposes only**.  
© 2026 **RESUCHECKMAKE**. All rights reserved.

