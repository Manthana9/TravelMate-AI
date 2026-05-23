// ======================
// LOGIN SYSTEM & STATE
// ======================
const loginBtn = document.getElementById("login-btn");
const loginSection = document.querySelector(".login-section");
const dashboard = document.querySelector(".dashboard-section");
const loginName = document.getElementById("login-name");
const loginPassword = document.getElementById("login-password");

const profileName = document.getElementById("profile-name");
const profileEmail = document.getElementById("profile-email");
const topProfileName = document.getElementById("top-profile-name");

// Generate a random unique session tracking key for this user instance
const currentSessionId = "session_" + Math.floor(Math.random() * 100000);

loginBtn.addEventListener("click", () => {
  if (!loginName.value || !loginPassword.value) {
    alert("Please enter username and password");
    return;
  }

  profileName.innerText = loginName.value;
  topProfileName.innerText = loginName.value;
  profileEmail.innerText = loginName.value + "@travelmate.ai";

  loginSection.classList.add("hide");

  setTimeout(() => {
    dashboard.classList.remove("hidden");
    dashboard.classList.add("show");
    document.body.style.overflow = "auto";
  }, 800);
});

// ======================
// PROFILE POPUP TOGLE
// ======================
const profileBtn = document.getElementById("profile-btn");
const sidebarProfile = document.getElementById("sidebar-profile");
const profilePopup = document.querySelector(".profile-popup");

const toggleProfile = () => profilePopup.classList.toggle("hidden");
profileBtn.addEventListener("click", toggleProfile);
sidebarProfile.addEventListener("click", toggleProfile);

// ======================
// LOGOUT CONTROL
// ======================
const logoutBtn = document.getElementById("logout-btn");
logoutBtn.addEventListener("click", () => {
  loginSection.classList.remove("hide");
  dashboard.classList.add("hidden");
  loginName.value = "";
  loginPassword.value = "";
  profilePopup.classList.add("hidden");
  document.body.style.overflow = "hidden";
});

// ======================
// CORE DATA GENERATION (CONNECTED TO FLASK & GOOGLE ADK)
// ======================
const generateBtn = document.getElementById("generate-btn");
const loader = document.getElementById("loader");
const displayBox = document.getElementById("itinerary-display-box");
const markdownTarget = document.getElementById("markdown-target-element");
const approvalBox = document.getElementById("frontend-approval-box");

generateBtn.addEventListener("click", async () => {
  const destination = document.getElementById("destination").value;
  const budget = document.getElementById("budget").value;
  const duration = document.getElementById("duration").value;

  if (!destination || !budget || !duration) {
    alert("Please fill all fields");
    return;
  }

  // Hide old elements and spin the loading wheel animation
  displayBox.classList.add("hidden");
  approvalBox.classList.add("hidden");
  loader.classList.remove("hidden");

  try {
    const res = await fetch("http://127.0.0.1:5000/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        destination: destination,
        duration: duration,
        budget: budget,
        session_id: currentSessionId
      })
    });

    const data = await res.json();
    loader.classList.add("hidden");

    if (data.success && data.itinerary) {
      // Use Marked.js to transform the ADK output markdown into styled HTML elements
      markdownTarget.innerHTML = marked.parse(data.itinerary);
      
      // Smoothly display dashboard containers
      displayBox.classList.remove("hidden");
      approvalBox.classList.remove("hidden");
    } else {
      alert("Error generating itinerary: " + (data.error || "Unknown Error"));
    }
  } catch (error) {
    loader.classList.add("hidden");
    console.error(error);
    alert("Backend connection failed. Make sure your Flask server is running on port 5000!");
  }
});

// ======================
// TRANSACTIONAL BOOKING REDIRECT
// ======================
const confirmBtn = document.getElementById("confirm-booking-btn");
const modifyBtn = document.getElementById("modify-booking-btn");

confirmBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("http://127.0.0.1:5000/api/approve-trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: currentSessionId })
    });

    const data = await res.json();
    if (data.success) {
      alert("Trip Approved Successfully! Redirecting you to secure final hotel options... 🎉");
      // Fire the native browser window redirect out to live aggregator engine mapping
      window.open("https://www.google.com/travel/search", "_blank");
    }
  } catch (error) {
    alert("Error logging trip approval state.");
  }
});

modifyBtn.addEventListener("click", () => {
  const destInput = document.getElementById("destination");
  destInput.focus();
  alert("Conversion adjustment focused! Update criteria options in the top bar fields and re-click 'Generate Plan'.");
});