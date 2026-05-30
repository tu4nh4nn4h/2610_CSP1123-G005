function registerEventPage(eventId) {
  localStorage.setItem("eventId", eventId);
  window.location.href = "/form";
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
  event: eventName,
  ...data
});

      localStorage.setItem("registrations", JSON.stringify(registrations));

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