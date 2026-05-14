// ================= NAVIGATION =================
function registerEventPage(eventId) {
    localStorage.setItem("eventId", eventId);
    window.location.href = "/form";
}

function goBackEvent() {
    const eventId = localStorage.getItem("eventId") || 1;
    window.location.href = `/event/${eventId}`; 
}

function closeModal() {
    const modal = document.getElementById("successModal");
    if (modal) modal.classList.add("hidden");
}

// ================= FORM LISTENER =================
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("regForm");
    if (!form) return;

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        // 1. Ambil data dari input
        const eventId = localStorage.getItem("eventId") || 1;
        const data = {
            name: document.getElementById("name").value.trim(),
            studentId: document.getElementById("studentId").value.trim(),
            studentEmail: document.getElementById("studentEmail").value.trim(),
            personalEmail: document.getElementById("personalEmail").value.trim(),
            phone: document.getElementById("phone").value.trim(),
            faculty: document.getElementById("faculty").value
        };

        // 2. Semak Checkbox (Wajib untuk Outlook Sync)
        const checkbox = document.getElementById("addToCalendar");
        if (!checkbox.checked) {
            alert("Sila tanda kotak penyegerakan kalendar untuk meneruskan.");
            return;
        }

        // 3. Simpan data ke Database via Flask
        fetch("/register", { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(res => {
            if (!res.ok) throw new Error("Gagal menyimpan data");
            return res.json();
        })
        .then((response) => {
            // 4. Papar Modal Kejayaan
            const modal = document.getElementById("successModal");
            if (modal) modal.classList.remove("hidden");

            // 5. Proses Download Fail .ics (Outlook)
            const events = {
                1: { title: "Tech Talk 2026", desc: "Learn about AI trends", location: "Main Hall", start: "20260520T100000", end: "20260520T120000" },
                2: { title: "Sports Day", desc: "Annual university sports event", location: "Stadium", start: "20260525T080000", end: "20260525T120000" },
                3: { title: "Hackathon 2026", desc: "Build innovative projects", location: "Lab 1", start: "20260601T090000", end: "20260601T180000" },
                4: { title: "MMU Fun Run 2026", desc: "Run for fun and fitness", location: "Campus Park", start: "20260610T070000", end: "20260610T100000" }
            };

            const e = events[eventId];
            if (e) {
                const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UniSphere//Campus Events//EN
BEGIN:VEVENT
SUMMARY:${e.title}
DESCRIPTION:${e.desc}
LOCATION:${e.location}
DTSTART:${e.start}
DTEND:${e.end}
END:VEVENT
END:VCALENDAR`;

                const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${e.title}.ics`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }

            // 6. Redirect automatik selepas 3 saat
            setTimeout(() => {
                goBackEvent();
            }, 3000);
        })
        .catch(err => {
            console.error("Error:", err);
            alert("System error. Try again.");
        });
    });
});