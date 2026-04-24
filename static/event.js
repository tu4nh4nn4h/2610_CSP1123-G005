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

  registrations.push({
    event: eventName,
    name: name,
    studentId: studentId,
    studentEmail: studentEmail
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  document.getElementById("successModal").classList.remove("hidden");
}


// ================= BACK BUTTON =================
function backToEvent() {
  document.getElementById("successModal").classList.add("hidden");
  window.location.href = "/eventregister";
}


// ================= FORM HANDLER =================
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("regForm");

  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    submitRegistration();
  });
});