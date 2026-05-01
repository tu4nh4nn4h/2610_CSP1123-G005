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
    .then(response => response.json())
    .then(result => {

      // ================= OUTLOOK CALENDAR =================
      const checkbox = document.getElementById("addToCalendar");
      let eventId = parseInt(localStorage.getItem("eventId")) || 1;

      const events = {
        1: {
          title: "Tech Talk 2026",
          desc: "Learn about AI trends",
          location: "Main Hall",
          start: "20260520T100000",
          end: "20260520T120000"
        },
        2: {
          title: "Sports Day",
          desc: "Annual university sports event",
          location: "Stadium",
          start: "20260525T080000",
          end: "20260525T120000"
        },
        3: {
          title: "Hackathon 2026",
          desc: "Build innovative projects",
          location: "Lab 1",
          start: "20260601T090000",
          end: "20260601T180000"
        },
        4: {
          title: "MMU Fun Run 2026",
          desc: "Run for fun and fitness",
          location: "Campus Park",
          start: "20260610T070000",
          end: "20260610T100000"
        }
      };

      // ✅ Generate .ics for Outlook
      if (checkbox && checkbox.checked && events[eventId]) {
        const e = events[eventId];

        const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:${e.title}
DESCRIPTION:${e.desc}
LOCATION:${e.location}
DTSTART:${e.start}
DTEND:${e.end}
END:VEVENT
END:VCALENDAR`;

        const blob = new Blob([icsContent], { type: "text/calendar" });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `${e.title}.ics`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }

      // ================= SUCCESS FLOW =================
      form.reset();

      // optional: show modal if you want
      document.getElementById("successModal").classList.remove("hidden");

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