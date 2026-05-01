// ================= NAVIGATION =================
function registerEventPage(eventId) {
  localStorage.setItem("eventId", eventId);
  window.location.href = "/form";
}


// ================= FORM LISTENER =================
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("regForm");

  if (!form) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    // ================= GET FORM DATA =================
    const data = {
      name: document.getElementById("name").value.trim(),
      studentId: document.getElementById("studentId").value.trim(),
      studentEmail: document.getElementById("studentEmail").value.trim(),
      personalEmail: document.getElementById("personalEmail").value.trim(),
      phone: document.getElementById("phone").value.trim(),
      faculty: document.getElementById("faculty").value
    };

    // basic validation
    if (!data.name || !data.studentId || !data.studentEmail || !data.phone || !data.faculty) {
      return;
    }

    // ================= SEND TO BACKEND =================
    fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) throw new Error("Server error");
      return response.json();
    })
    .then(result => {
      const checkbox = document.getElementById("addToCalendar");
      let eventId = 1;

      if (checkbox && checkbox.checked) {
        const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Test Event
DESCRIPTION:Testing calendar
LOCATION:Test Location
DTSTART:20260520T100000
DTEND:20260520T120000
END:VEVENT
END:VCALENDAR`;

        const blob = new Blob([icsContent], { type: "text/calendar" });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "Test Event.ics";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }

      console.log("CALENDAR TRIGGERED");

      // ================= SUCCESS FLOW =================
      form.reset();

      // optional: show modal if you want
      const successModal = document.getElementById("successModal");
      if (successModal) {
        successModal.classList.remove("hidden");
      }

      // redirect after short delay
      setTimeout(() => {
        window.location.href = `/event/${eventId}`;
      }, 800);
    })
    .catch(error => {
      console.error(error);
    });

  });
});