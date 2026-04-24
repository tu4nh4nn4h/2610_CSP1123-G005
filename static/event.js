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
  // you can still collect data here if needed
  const name = document.getElementById("name").value;

  if (!name) {
    alert("Please fill in required fields!");
    return;
  }

  // show popup
  document.getElementById("successPopup").classList.remove("hidden");
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

  let isRegistered = registrations.some(r => r.event === eventName);

  const btn = document.querySelector(".register-btn");

  if (!btn) return;

  if (isRegistered) {
    btn.innerText = "Cancel Registration";
    btn.style.background = "red";
    btn.onclick = cancelRegistration;
  } else {
    btn.innerText = "Register";
    btn.style.background = "";
    btn.onclick = registerEventPage;
  }
}

updateButton();

function cancelRegistration() {
  let confirmCancel = confirm("Are you sure you want to cancel the registration?");

  if (!confirmCancel) {
    return; // do nothing (NO)
  }

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
   let eventName = localStorage.getItem("selectedEvent");
  registrations = registrations.filter(r => r.event !== eventName);

  localStorage.setItem("registrations", JSON.stringify(registrations));

  alert("Registration cancelled");

  location.reload();

  window.onload = updateButton;
}

document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("registerBtn");

  if (btn) {
    btn.addEventListener("click", function () {
      const event = events[0];

      localStorage.setItem("selectedEvent", event.title);

      window.location.href = "/form";  // FLASK ROUTE ONLY
    });
  }
});