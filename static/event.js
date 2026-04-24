const events = [
  {
    title: "Tech Talk 2026",
    desc: "Learn about AI trends",
    date: "20 May 2026",
    time: "10:00 AM",
    venue: "Main Hall"
  },
  {
    title: "Sports Day",
    desc: "Annual university sports event",
    date: "25 May 2026",
    time: "8:00 AM",
    venue: "Stadium"
  },
  {
    title: "Coding Workshop",
    desc: "Beginner friendly coding session",
    date: "30 May 2026",
    time: "2:00 PM",
    venue: "Lab 3"
  }
];

// ================= REGISTER PAGE =================
function registerEventPage() {
  const event = events[0];
  localStorage.setItem("selectedEvent", event.title);
  window.location.href = "/form";
}

// ================= SUBMIT FORM =================
function submitRegistration() {
  const name = document.getElementById("name").value;
  const studentId = document.getElementById("studentId").value;
  const studentEmail = document.getElementById("studentEmail").value;

  if (!name || !studentId || !studentEmail) {
    alert("Please fill in required fields!");
    return;
  }

  let eventName = localStorage.getItem("selectedEvent");
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({ event: eventName, name });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  // ✅ SHOW SUCCESS POPUP
  document.getElementById("successModal").classList.remove("hidden");

  updateButton();
}

// ================= BUTTON STATE =================
function updateButton() {
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
  let eventName = localStorage.getItem("selectedEvent");

  const btn = document.getElementById("registerBtn");
  if (!btn) return;

  let isRegistered = registrations.some(r => r.event === eventName);

  if (isRegistered) {
    btn.textContent = "Cancel Registration";
    btn.style.background = "red";
  } else {
    btn.textContent = "Register";
    btn.style.background = "";
  }
}

// ================= CANCEL POPUP =================
function showCancelPopup() {
  document.getElementById("cancelModal").classList.remove("hidden");
}

function closeCancel() {
  const modal = document.getElementById("cancelModal");
  modal.classList.add("hidden");
}

function confirmCancel() {
  let eventName = localStorage.getItem("selectedEvent");

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
  registrations = registrations.filter(r => r.event !== eventName);

  localStorage.setItem("registrations", JSON.stringify(registrations));

  closeCancel();

  alert("Your registration has been removed");

  // 🔥 go back to event page
  window.location.href = "/eventregister";
}
function backToEvent() {
  document.getElementById("successModal").classList.add("hidden");
  window.location.href = "/eventregister";
}

// ================= MAIN BUTTON CONTROL =================
document.addEventListener("DOMContentLoaded", function () {

  document.getElementById("regForm").addEventListener("submit", function(e) {
    e.preventDefault();
    submitRegistration();
  });

});