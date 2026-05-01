// ================= NAVIGATION =================
function registerEventPage(eventId) {
  localStorage.setItem("eventId", eventId);
  window.location.href = "/form";
}

function goBackEvent() {
  const eventId = localStorage.getItem("eventId") || 1;
  window.location.href = `/event/${eventId}`;
}

// ================= FORM LISTENER =================
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("regForm");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const eventId = parseInt(localStorage.getItem("eventId")) || 1;

    const data = {
      name: document.getElementById("name").value.trim(),
      studentId: document.getElementById("studentId").value.trim(),
      studentEmail: document.getElementById("studentEmail").value.trim(),
      personalEmail: document.getElementById("personalEmail").value.trim(),
      phone: document.getElementById("phone").value.trim(),
      faculty: document.getElementById("faculty").value
    };

    if (!data.name || !data.studentId || !data.studentEmail || !data.phone || !data.faculty) {
      return;
    }

    fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    .then(res => {
      if (!res.ok) throw new Error("Server error");
      return res.json();
    })
    .then(() => {

      // SHOW MODAL
      const modal = document.getElementById("successModal");
      if (modal) modal.classList.remove("hidden");

      // DELAY REDIRECT
      setTimeout(() => {
        window.location.href = `/event/${eventId}`;
      }, 2000);
    })
    .catch(err => console.error("Registration error:", err));
  });
});