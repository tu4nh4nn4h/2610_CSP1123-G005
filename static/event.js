function registerEventPage(eventId) {
  localStorage.setItem("eventId", eventId);
  window.location.href = "/form";
}

function submitRegistration() {
  const name = document.getElementById("name").value.trim();
  const studentId = document.getElementById("studentId").value.trim();
  const studentEmail = document.getElementById("studentEmail").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const faculty = document.getElementById("faculty").value;

  // ❌ no alert, just stop silently
  if (!name || !studentId || !studentEmail || !phone || !faculty) {
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
      let eventName = localStorage.getItem("selectedEvent");
      let registrations = JSON.parse(localStorage.getItem("registrations")) || [];

      registrations.push({
        event: eventName
      });

      localStorage.setItem("registrations", JSON.stringify(registrations));

      document.getElementById("regForm").reset();
      let eventId = localStorage.getItem("eventId") || 1;
window.location.href = `/event/${eventId}`;
    })
    .catch(error => {
      console.error(error);
      // ❌ no alert here either
    });
  }

  if (form) {
    form.addEventListener("submit", handleSubmit);
  }
});

