const API = "http://127.0.0.1:8000";


async function uploadResume() {
  const file = document.getElementById("resumeFile").files[0]; //isse html me jo id h usse resume is cons file me aa gya 

  if (!file) {
    alert("Please select a resume PDF");
    return;
  }

  const formData = new FormData(); // ye ek special js object h jo file+data backend ko bhejne k kaam aata h
  formData.append("file", file);  // file ko formdata se attach krta h
  //yha pr key ka name "file" isliye rka kyuki backend me async def upload_resume(file: UploadFile = File(...)):  uploadFile wala file me jaa rha h


  //FETCH KA USE URL JESO K LIYE HEE HOTA H AND USME URL AND DATA KIS TYPE ME JAYEGA WO SB DENA PDTA H
  const res = await fetch(`${API}/upload-resume/`, {  //fetch se wo backend me data bhejta h and usse jo return me milta h usko leta h jese ki isme return me mila resume processed successfully
    method: "POST",
    body: formData
  });

  const data = await res.json();   //isse jo resume se return aaya h wo data me aa gya 
  alert(data.message);  //isse user ko mssg dekta h pop up hoke
}



function displayResult(data) {
  let html = "";

  if (data.match_score === null || data.match_score === undefined) {
    html = `<p>${data.message || "Unable to calculate match score"}</p>`;
    document.getElementById("result").innerHTML = html;
    return;
  }

  html += `<p><strong>Match Score:</strong> ${data.match_score}%</p>`;

  html += `
    <div class="progress">
      <div class="progress-bar" style="width:${data.match_score}%"></div>
    </div>
  `;

  html += `<h3>Matched Skills</h3>`;
  if (data.matched_skills.length === 0) {
    html += `<p>No matched skills found</p>`;
  } else {
    data.matched_skills.forEach(skill => {
      html += `<span class="badge green">${skill}</span>`;
    });
  }

  html += `<h3>Missing Skills</h3>`;
  if (data.missing_skills.length === 0) {
    html += `<p>No missing skills </p>`;
  } else {
    data.missing_skills.forEach(skill => {
      html += `<span class="badge red">${skill}</span>`;
    });
  }

  document.getElementById("result").innerHTML = html;
}




async function matchJob() {
  const jd = document.getElementById("jobDesc").value;

  if (jd.length < 10) {
    alert("Please enter a valid job description");
    return;
  }

  const res = await fetch(`${API}/match-job/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ job_description: jd })
  });

  const data = await res.json();
  displayResult(data);
}



//RESUME MAKER KA FUNCTION

//ye jo template user ne choose kiya h uske according preview bnane k liye
//ye minimal template preview ka code h
//{data.skills.length ?  isse if else condition ki trah work krta h agar h toh hee function aage work krega
function previewMinimal(data) {
  return `
  <div class="resume minimal-resume">

    <h1 class="minimal-name">${data.full_name}</h1>

    <p class="minimal-contact">
      ${data.email}
      ${data.phone ? " | " + data.phone : ""}
      ${data.location ? " | " + data.location : ""}
    </p>

    <div class="minimal-divider"></div>

    ${data.skills.length ? `     
    <section>
      <h2>SKILLS</h2>
      <p>${data.skills.join(", ")}</p>
    </section>` : ""}

    ${data.experience?.length ? `
    <section>
      <h2>EXPERIENCE</h2>
      ${data.experience.map(exp => `
        <p><b>${exp.title}</b> — ${exp.company}</p>
        <p class="muted">${exp.duration}</p>
        <ul>
          ${exp.points.map(p => `<li>${p}</li>`).join("")}
        </ul>
      `).join("")}
    </section>` : ""}

    ${data.projects?.length ? `
    <section>
      <h2>PROJECTS</h2>
      ${data.projects.map(p => `
        <p><b>${p.title}</b></p>
        <ul>
          ${p.points.map(x => `<li>${x}</li>`).join("")}
        </ul>
      `).join("")}
    </section>` : ""}

    ${data.education.length ? `
    <section>
      <h2>EDUCATION</h2>
      ${data.education.map(e => `<p>${e}</p>`).join("")}
    </section>` : ""}

    ${data.extra ? `
    <section>
      <h2>EXTRA CURRICULAR & ACHIEVEMENTS</h2>
      <p>${data.extra}</p>
    </section>` : ""}

  </div>
  `;
}

//ye modern template preview ka code h
function previewModern(data) {
  return `
  <div class="resume modern-resume">

    <div class="modern-header">
      <h1>${data.full_name}</h1>
    </div>

    <p class="modern-contact">
      ${data.email}
      ${data.phone ? " | " + data.phone : ""}
      ${data.location ? " | " + data.location : ""}
    </p>

    <section>
      <h2>PROFILE</h2>
      <p>${data.extra || "Professional summary"}</p>
    </section>

    ${data.experience?.length ? `
    <section>
      <h2>PROFESSIONAL EXPERIENCE</h2>
      ${data.experience.map(exp => `
        <p><b>${exp.title}</b> — ${exp.company} (${exp.duration})</p>
        <ul>
          ${exp.points.map(p => `<li>${p}</li>`).join("")}
        </ul>
      `).join("")}
    </section>` : ""}

    ${data.projects?.length ? `
    <section>
      <h2>PROJECTS</h2>
      ${data.projects.map(p => `
        <p><b>${p.title}</b></p>
        <ul>
          ${p.points.map(x => `<li>${x}</li>`).join("")}
        </ul>
      `).join("")}
    </section>` : ""}

    <section>
      <h2>EDUCATION</h2>
      ${data.education.map(e => `<p>${e}</p>`).join("")}
    </section>

    <section>
      <h2>SKILLS</h2>
      <p>${data.skills.join(" | ")}</p>
    </section>

  </div>
  `;
}



async function generateResume() {
  const selectedTemplate = localStorage.getItem("selectedTemplate");

  if (!selectedTemplate) {
    alert("Please select a resume template first");
    window.location.href = "template.html";
  }
    const jobTitle = document.getElementById("jobTitle").value.trim();
    const company = document.getElementById("company").value.trim();
    const duration = document.getElementById("duration").value.trim();
  
    const projectTitle = document.getElementById("projectTitle").value.trim();
  
  // ----------FORM DATA COLLECT ----------
  const education = [];
  if (document.getElementById("edu1").value) {
    education.push(
      document.getElementById("edu1").value + " | " +
      document.getElementById("edu2").value + " | " +
      document.getElementById("edu3").value
    );
  }

  
const experience = [];

if (jobTitle) {
  experience.push({ //yha experience ek array banaya h usme object banaya h
    title: jobTitle,
    company: company,
    duration: duration,
    points: document.getElementById("experience").value
      .split("\n")
      .map(p => p.trim())  //isse line k aage peeche k spaces ht jate h
      .filter(p => p.length > 0) //isse khali lines hatadi h
  });
}


const projects = [];

if (projectTitle) {
  projects.push({
    title: projectTitle,
    points: document.getElementById("projects").value
      .split("\n")
      .map(p => p.trim())
      .filter(p => p.length > 0)
  });
}


  const data = {
    full_name: document.getElementById("fullName").value,
    email: document.getElementById("email").value,
    phone: document.getElementById("phone").value,
    location: document.getElementById("location").value,

    skills: document.getElementById("skills").value
      .split(",")
      .map(s => s.trim())
      .filter(s => s.length > 0),

    education,
    experience,
    projects,
    extra: document.getElementById("extra").value,
    template: localStorage.getItem("selectedTemplate")
  };

  if (!data.full_name || !data.email || data.skills.length === 0) {
    alert("Please fill required fields (Name, Email, Skills)");
    return;
  }

  // ---------- RESUME PREVIEW HTML ----------
  let html = "";

if (data.template === "minimal") {
  html = previewMinimal(data);

} else if (data.template === "modern") {
  html = previewModern(data);

} else {
  // classic fallback
   html = `
    <div class="resume">
      <h1>${data.full_name}</h1>
      <p>${data.email} | ${data.phone} | ${data.location}</p>

      <h2>Skills</h2>
      <p>${data.skills.join(", ")}</p>

      <h2>Education</h2>
      ${education.map(e => `<p>${e}</p>`).join("")}
  `;

  if (experience.length) {
    html += `<h2>Experience</h2>`;
    experience.forEach(exp => {
      html += `
        <p><strong>${exp.title}</strong> — ${exp.company} (${exp.duration})</p>
        <ul>
          ${exp.points.map(p => `<li>${p}</li>`).join("")}
        </ul>
      `;
    });
    
  }

  if (projects.length) {
    html += `<h2>Projects</h2>`;
    
    projects.forEach(proj => {
      html += `
        <p><strong>${proj.title}</strong></p>
        <ul>
          ${proj.points.map(point => `<li>${point}</li>`).join("")}
        </ul>
      `;
    });
  }
    

  if (data.extra) {
    html += `<h2>Extra-Curricular</h2><p>${data.extra}</p>`;
  }

  html += `</div>`;
}
  // ---------- SHOW PREVIEW ----------
  document.getElementById("resumePreview").innerHTML = html;

  // ----------SHOW DOWNLOAD BUTTON ----------
  document.getElementById("downloadBtn").style.display = "inline-block";

  // ---------- STORE DATA FOR DOWNLOAD ----------
  window.resumeData = data;
}



async function downloadResume() {

  const res = await fetch(`${API}/generate-resume/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(window.resumeData)
  });

  const blob = await res.blob();     //blob (binary large object)se ye hota h ki jo backend ne raw pdf bytes(001100 aesa kuch) bheji h usse ye file jesa bna deta h
  const url = window.URL.createObjectURL(blob); // file abhi ram me h usse open hone k liye brower chiye toh ye line us file ko ek fake url de deta h open hone k liye

  const a = document.createElement("a");
  a.href = url;
  a.download = "Resume.pdf";
  document.body.appendChild(a);
  a.click();

  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}


//for login modal 

function updateNavbar() { //isse agar tum page ko refresh bhi kr rhe ho toh id save rhegi change nhi hogi or email upper dikegi
  const user = localStorage.getItem("loggedInUser");

  const loginBtn = document.querySelector(".nav-btn.login");    //queryselector ek class finder h jo html k andar cheeze dundta h
  const registerBtn = document.querySelector(".nav-btn.register");

  if (user) {
    loginBtn.style.display = "none";
    registerBtn.style.display = "none";

    // Agar pehle se user-info exist nahi karta
    if (!document.getElementById("userEmail")) {
      const userSpan = document.createElement("span");
      userSpan.id = "userEmail";
      userSpan.style.color = "#2f7f86";
      userSpan.style.fontWeight = "600";
      userSpan.innerText = user;

      const logoutBtn = document.createElement("button");  //isse button create hoti h
      logoutBtn.innerText = "Logout";
      logoutBtn.className = "nav-btn";
      logoutBtn.onclick = logoutUser;

      document.querySelector(".nav-actions").appendChild(userSpan);
      document.querySelector(".nav-actions").appendChild(logoutBtn);
    }
  }
}

//logout function with email and password
function logoutUser() {
  localStorage.removeItem("loggedInUser");
  location.reload(); // page refresh
}

function isValidEmail(email) {  //isse galat email enter nhi hogi
  const emailRegex =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  return emailRegex.test(email);
}


function openLogin() {
  document.getElementById("loginModal").style.display = "flex";
}

function closeLogin() {
  document.getElementById("loginModal").style.display = "none";
}

function signup() {
  closeLogin();
  openRegister();
}

function validateCaptcha() {
  const check = document.getElementById("robotCheck");
  if (!check.checked) {
    alert("Please Consent with terms and policy.");
    return false;
  }
  return true;
}
async function loginUser() {
  if (!validateCaptcha()) return;

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  // BASIC VALIDATION
  if (!email || !password) {
    alert("Email and password required");
    return;
  }
  
  if (!isValidEmail(email)) {
    alert("Please enter a valid email address");
    return;
  }
  

  // BACKEND KO DATA BHEJNA
  const res = await fetch(`${API}/login/email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      password: password
    })
  });

  const data = await res.json();

  if (data.success) {

    // USER KO BROWSER ME SAVE KARO
    localStorage.setItem("loggedInUser", data.user.email);
  
    alert("Login successful ✅");
    closeLogin();
  
    updateNavbar(); 
  }
   else {
    alert(data.message || "Login failed");
  }
}

//FOR REGISTER CALL with email and password
function openRegister() {
  document.getElementById("registerModal").style.display = "flex";
}

function closeRegister() {
  document.getElementById("registerModal").style.display = "none";
}

function switchToLogin() {
  closeRegister();
  openLogin();
}

async function registerUser() {
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value.trim();
  const consent = document.getElementById("registerConsent").checked;

  if (!email || !password) {
    alert("Email and password required");
    return;
  }

  if (!consent) {
    alert("Please agree to Terms & Privacy Policy");
    return;
  }

  const res = await fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      password: password
    })
  });

  const data = await res.json();

  if (data.success) {
    closeRegister();
    openLogin();
    alert("Now login with your credentials");
  }
  
   else {
    alert(data.message);
  }
}

//agar user login h toh hee create resume and check resume open ho
function requireLogin(redirectUrl) {
  const user = localStorage.getItem("loggedInUser");

  if (!user) {
    // User login nahi hai
    openLogin();   // login popup open
    return;
  }

  // ✅ User login hai
  window.location.href = redirectUrl;  //redirect me jo page ka url h wo open ho jayega
}


//google login

function loginWithGoogle() {
  window.location.href = "http://127.0.0.1:8000/login/google";
}

window.onload = function () {
  // Navbar update (normal login)
  updateNavbar();

  // Google login success check
  const params = new URLSearchParams(window.location.search);

  if (params.get("google_login_success") === "true") {
    const email = params.get("email");

    localStorage.setItem("loggedInUser", email);
    updateNavbar();

    alert("Google Login Successful ✅");

    // URL clean
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

