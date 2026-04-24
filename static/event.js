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

function registerEventPage() {
  const event = events[0];

  localStorage.setItem("selectedEvent", event.title);

  // IMPORTANT: use Flask route, NOT form.html
  window.location.href = "/form";
}

function registerEvent(eventName) {
  // store selected event temporarily
  localStorage.setItem("selectedEvent", eventName);

  // go to registration form page
  window.location.href = "form.html";
}

function loadRegistrations() {
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  let output = "";

  registrations.forEach((r, index) => {
    output += `
      <div class="event-card">
        <p>${r.event}</p>
        <button onclick="cancelRegistration(${index})">Cancel</button>
      </div>
    `;
  });

  document.getElementById("list").innerHTML = output;
}

function submitRegistration() {
  const name = document.getElementById("name").value;
  const studentId = document.getElementById("studentId").value;
  const studentEmail = document.getElementById("studentEmail").value;
  const personalEmail = document.getElementById("personalEmail").value;
  const phone = document.getElementById("phone").value;
  const faculty = document.getElementById("faculty").value;

  if (!name || !studentId || !studentEmail) {
    alert("Please fill in required fields!");
    return;
  }

  let eventName = localStorage.getItem("selectedEvent");

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({
    event: eventName,
    name,
    studentId,
    studentEmail,
    personalEmail,
    phone,
    faculty
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  // ✅ SHOW SUCCESS POPUP (instead of alert)
  document.getElementById("successPopup").classList.remove("hidden");

  updateButton();
}

function closePopup() {
  document.getElementById("successPopup").classList.add("hidden");

  // optional: reset form after closing
  document.querySelector("form").reset();
}
  let name = document.getElementById("name").value;
  let studentId = document.getElementById("studentId").value;
  let studentEmail = document.getElementById("studentEmail").value;
  let personalEmail = document.getElementById("personalEmail").value;
  let phone = document.getElementById("phone").value;
  let faculty = document.getElementById("faculty").value;

  let eventName = localStorage.getItem("selectedEvent");

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({
    event: eventName,
    name,
    studentId,
    studentEmail,
    personalEmail,
    phone,
    faculty
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  alert("Registered successfully!");

window.location.href = "/register";
function updateButton() {
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
  let eventName = localStorage.getItem("selectedEvent") || events[0].title;

  const btn = document.querySelector(".register-btn");
  if (!btn) return;

  let isRegistered = registrations.some(r => r.event === eventName);

  if (isRegistered) {
    btn.innerText = "Cancel Registration";
    btn.style.background = "red";

    btn.onclick = function () {
      showCancelPopup(eventName);
    };

  } else {
    btn.innerText = "Register";
    btn.style.background = "";

    btn.onclick = registerEventPage;
  }
}

function cancelRegistration(eventName) {
  showCancelPopup(eventName);
}

function showCancelPopup(eventName) {
  const popup = document.getElementById("cancelPopup");
  popup.classList.remove("hidden");

  popup.dataset.event = eventName;
}

function closeCancelPopup() {
  document.getElementById("cancelPopup").classList.add("hidden");
}

function confirmCancel() {
  let eventName = document.getElementById("cancelPopup").dataset.event;

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations = registrations.filter(r => r.event !== eventName);

  localStorage.setItem("registrations", JSON.stringify(registrations));

  closeCancelPopup();

  alert("Your registration has been removed");

  updateButton();
}