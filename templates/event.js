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
  let name = document.getElementById("name").value;
  let email = document.getElementById("email").value;
  let eventName = localStorage.getItem("selectedEvent");

  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({
    event: eventName,
    name: name,
    email: email
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  alert("Registration successful!");

  window.location.href = "registered.html";
} 

function cancelRegistration(index) {
  let confirmCancel = confirm("Are you sure you want to cancel?");

  if (confirmCancel) {
let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
    registrations.splice(index, 1);

    localStorage.setItem("registrations", JSON.stringify(registrations));

    loadRegistrations();
  }
}