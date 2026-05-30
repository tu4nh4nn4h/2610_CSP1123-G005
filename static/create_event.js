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

    const mainloc = document.getElementById('mainloc').value;
    const generalloc = document.getElementById('general_location').value;
    const wing = document.getElementById('faculty_wing').value;

    const generalContainer = document.getElementById('general_location_container');
    const specificContainer = document.getElementById('specific_location_container');
    const specificSelect = document.getElementById('specific_location');

    // Reset options
    specificSelect.innerHTML = '<option value="">Select Room / Venue</option>';

    if (mainloc === "General") {
        generalContainer.style.display = 'block';
    }
    else if (mainloc && wing) {

        specificContainer.style.display = 'block';

        locationData[mainloc][wing].forEach(location => {

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
    const name = document.getElementById('name').value;
    const startdate = document.getElementById('start_date').value;
    const enddate = document.getElementById('end_date').value;

    if (name && startdate && enddate) {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        document.getElementById('step-indicator').innerText = "Step 2 of 2: Logistics & Pricing";
    } else {
        alert("Please fill in the basic details first.");
    }
}

function prevStep() {
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step-indicator').innerText = "Step 1 of 2: Basic Details";
}

function togglePriceInput() {
    const eventType = document.getElementById('event_type').value;
    const priceContainer = document.getElementById('price_container');
    const priceInput = document.getElementById('price');

    if (eventType === 'paid') {
        priceContainer.style.display = 'block';
        priceInput.setAttribute('required', 'true');
    } else {
        priceContainer.style.display = 'none';
        priceInput.removeAttribute('required');
        priceInput.value = ""; // Clear value if switched back to free
    }
}

function handleSubmit(event) {
    event.preventDefault();
    
    // Collect all data
   const formData = {
    name: document.getElementById('name').value,
    description: document.getElementById('description').value,

    start_date: document.getElementById('start_date').value,
    end_date: document.getElementById('end_date').value,

    start_time: document.getElementById('start_time').value,
    end_time: document.getElementById('end_time').value,

    location: document.getElementById('location').value,
    participants: document.getElementById('participants').value,
    type: document.getElementById('event_type').value,
    price: document.getElementById('price').value || 0
    };

    console.log("Form Submitted Successfully:", formData);
    alert("Event Created Successfully!");
    // Here you would typically use fetch() to send data to your Flask backend
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

// Event listeners
startDate.addEventListener("change", validateDateTime);
endDate.addEventListener("change", validateDateTime);
startTime.addEventListener("change", validateDateTime);
endTime.addEventListener("change", validateDateTime);