const locationData = {
    "General": [
        "Central Plaza",
        "MMU Stadium",
        "Surau Al-Hidayah",
        "Tun Dr. Hasmah Mohd Ali Digital Library",
        "Dewan Tun Canselor",
        "Annex Hall",
        "MMU Hostel"
    ],

    "FCI": {
        "Wing A": ["Smart Lab 1", "FCI Lecture Hall 1"],
        "Wing B": ["Meeting Room Level 3", "Computing Lab 5"],
        "Wing C": ["Innovation Hub", "FCI Seminar Room"]
    },

    "FAIE": {
        "Wing A": ["e-Theater", "Sound Studio"],
        "Wing B": ["Main Gallery", "FAIE Workshop"],
        "Wing C": ["Media Lab", "FAIE Conference Room"]
    },

    "FCM": {
        "Wing A": ["e-Theater", "Sound Studio"],
        "Wing B": ["Main Gallery", "FCM Workshop"],
        "Wing C": ["Media Lab", "FCM Conference Room"]
    },

    "FOM": {
        "Wing A": ["FOM Exam Hall"],
        "Wing B": ["Case Study Room 1", "Management Suite"],
        "Wing C": ["FOM Seminar Room", "Strategy Lab"]
    },

    "FAC": {
        "Wing A": ["FAC Lecture Room 2"],
        "Wing B": ["Accounting Seminar Room", "Level 1 Lounge"]
    },

    "FCA": {
        "Wing A": ["FCA Main Auditorium"],
        "Wing B": ["FCA Art Studio", "Design Lab"],
        "Wing C": ["FCA Gallery", "Creative Workshop"]
    }
};

function updateMainLocations() {
    const mainlocSelect = document.getElementById('mainloc');

    const wingContainer = document.getElementById('faculty_wing_container');
    const wingSelect = document.getElementById('faculty_wing');

    const generalContainer = document.getElementById('general_location_container');
    const generalSelect = document.getElementById('general_location');

    const specificContainer = document.getElementById('specific_location_container');
    const specificSelect = document.getElementById('specific_location');

    const selectedLocation = mainlocSelect.value;

    // Clear previous options
    generalSelect.innerHTML = '<option value="">Select Venue</option>';
    wingSelect.innerHTML = '<option value="">Select Wing</option>';
    specificSelect.innerHTML = '<option value="">Select Room / Venue</option>';

    // Hide everything first
    generalContainer.style.display = 'none';
    wingContainer.style.display = 'none';
    specificContainer.style.display = 'none';

    if (selectedLocation === "General") {

        generalContainer.style.display = 'block';

        Object.values(locationData["General"]).forEach(location => {

            const option = document.createElement('option');

            option.value = location;
            option.textContent = location;

            generalSelect.appendChild(option);
        });
    }
    else if (selectedLocation && locationData[selectedLocation]) {
        // Show the second dropdown and populate it based on selected location
       wingContainer.style.display = 'block';

        Object.keys(locationData[selectedLocation]).forEach(wing => {
            const option = document.createElement('option');
            option.value = wing;
            option.textContent = wing;
            wingSelect.appendChild(option);
        });

    } else {
        // Selected a general spot or no faculty, hide the second dropdown
        wingContainer.style.display = 'none';
        specificContainer.style.display = 'none';
    }
}

function updateSpecificLocations() {

    const mainLocation = document.getElementById('mainloc').value;
    const generalLocation = document.getElementById('general_location').value;
    const facultyWing = document.getElementById('faculty_wing').value;

    const generalContainer = document.getElementById('general_location_container');
    const specificContainer = document.getElementById('specific_location_container');
    const specificSelect = document.getElementById('specific_location');

    // Reset options
    specificSelect.innerHTML = '<option value="">Select Room / Venue</option>';

    if (mainLocation === "General") {
        generalContainer.style.display = 'block';
    }
    else if (mainLocation && facultyWing) {

        specificContainer.style.display = 'block';

        locationData[mainLocation][facultyWing].forEach(location => {

            const option = document.createElement('option');

            option.value = location;
            option.textContent = location;

            specificSelect.appendChild(option);
        });

    } else {

        specificContainer.style.display = 'none';
    }
}

function nextStep() {
    // Basic validation before moving to next step
    const eventName = document.getElementById('event_name').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    if (eventName && startDate && endDate) {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        document.getElementById('step-indicator').innerText = "Step 2 of 2: Logistics";
    } else {
        alert("Please fill in the basic details first.");
    }
}

function prevStep() {
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step-indicator').innerText = "Step 1 of 2: Basic Details";
}

function submitEvent() {
    const formData = handleSubmit(event); // collect data, maybe reuse handleSubmit
    fetch('/createevent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "create_event_success") {
            alert("Event created successfully!");
            window.location.href = "/eventbrowsing";
        } else {
            alert("Failed to create event. Please try again.");
        }
    });
}

function handleSubmit(event) {
    event.preventDefault();
    
    // Collect all data
   const formData = {
    eventName: document.getElementById('event_name').value,
    eventDescription: document.getElementById('event_description').value,

    startDate: document.getElementById('start_date').value,
    endDate: document.getElementById('end_date').value,

    startTime: document.getElementById('start_time').value,
    endTime: document.getElementById('end_time').value,

    eventMode: document.getElementById('event_mode').value,

    mainLocation: document.getElementById('mainloc').value,
    generalLocation: document.getElementById('general_location').value,
    facultyWing: document.getElementById('faculty_wing').value,
    specificLocation: document.getElementById('specific_location').value,

    participants: document.getElementById('participants').value,
    eventLink: document.getElementById('event_link').value
   };
    return formData;
}

/* =========================
   DATE & TIME VALIDATION
========================= */

const startDate = document.getElementById("start_date");
const endDate = document.getElementById("end_date");

const startTime = document.getElementById("start_time");
const endTime = document.getElementById("end_time");

function validateDateTime() {

    // End date cannot be earlier than start date
    endDate.min = startDate.value;

    if (endDate.value < startDate.value) {
        endDate.value = startDate.value;
    }

    // If same day, end time cannot be earlier
    if (startDate.value === endDate.value) {

        endTime.min = startTime.value;

        if (endTime.value < startTime.value) {
            endTime.value = startTime.value;
        }

    } else {
        endTime.min = "";
    }
}

function toggleEventLink() {
    const eventMode = document.getElementById("event_mode").value;
    const linkContainer = document.getElementById("event_link_container");
    const eventLink = document.getElementById("event_link");

    if (eventMode === "offline") {
        linkContainer.style.display = "none";
        eventLink.required = false;
        eventLink.value = "";
    } else {
        linkContainer.style.display = "block";
        eventLink.required = true;
    }
}

// Event listeners
startDate.addEventListener("change", validateDateTime);
endDate.addEventListener("change", validateDateTime);
startTime.addEventListener("change", validateDateTime);
endTime.addEventListener("change", validateDateTime);