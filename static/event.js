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


// ================= NAVIGATE TO FORM =================
function registerEventPage() {
  const event = events[0];
  localStorage.setItem("selectedEvent", event.title);
  window.location.href = "/form";
}


function submitRegistration() {
  const name = document.getElementById("name").value.trim();
  const studentId = document.getElementById("studentId").value.trim();
  const studentEmail = document.getElementById("studentEmail").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const faculty = document.getElementById("faculty").value;

  if (!name || !studentId || !studentEmail || !phone || !faculty) {
    alert("Please fill in all required fields!");
    return;
  }

  let eventName = localStorage.getItem("selectedEvent");
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({
    event: eventName,
    name,
    studentId,
    studentEmail,
    phone,
    faculty
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  document.getElementById("successModal").classList.remove("hidden");
}


// ================= BACK TO EVENT PAGE =================
function backToEvent() {
  document.getElementById("successModal").classList.add("hidden");
  window.location.href = "/eventregister";
}


// ================= FORM LISTENER =================
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("regForm");

  function handleSubmit(event) {
    event.preventDefault();

    const data = {
      name: document.getElementById("name").value,
      studentId: document.getElementById("studentId").value,
      studentEmail: document.getElementById("studentEmail").value,
      personalEmail: document.getElementById("personalEmail").value,
      phone: document.getElementById("phone").value,
      faculty: document.getElementById("faculty").value
    };

    fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
  // ✅ SAVE TO LOCAL STORAGE HERE
  let eventName = localStorage.getItem("selectedEvent");
  let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

  registrations.push({
    event: eventName
  });

  localStorage.setItem("registrations", JSON.stringify(registrations));

  window.location.href = "/eventregister";

  alert("Registered successfully!");
  document.getElementById("regForm").reset();
})
    .catch(error => {
      alert("Error occurred!");
      console.error(error);
    });
  }

  if (form) {
    form.addEventListener("submit", handleSubmit);
  }
});