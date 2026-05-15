const locationData = {
    "FCI": ["Smart Lab 1", "FCI Lecture Hall 1", "Meeting Room Level 3", "Computing Lab 5"],
    "FCM": ["e-Theater", "Sound Studio", "Main Gallery", "FCM Workshop"],
    "FOM": ["FOM Exam Hall", "Case Study Room 1", "Management Suite"],
    "FAC": ["FAC Lecture Room 2", "Accounting Seminar Room", "Level 1 Lounge"]
};

function updateSpecificLocations() {
    const facultySelect = document.getElementById('faculty');
    const specificContainer = document.getElementById('specific_location_container');
    const specificSelect = document.getElementById('specific_location');
    
    const selectedFaculty = facultySelect.value;

    // Clear existing options
    specificSelect.innerHTML = '<option value="">Select a specific spot</option>';

    if (selectedFaculty && locationData[selectedFaculty]) {
        // Show the second dropdown
        specificContainer.style.display = 'block';

        // Populate the second dropdown
        locationData[selectedFaculty].forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            specificSelect.appendChild(option);
        });
    } else {
        // Hide it if no faculty is selected
        specificContainer.style.display = 'none';
        specificSelect.removeAttribute('required');
    }
}

function nextStep() {
    // Basic validation before moving to next step
    const name = document.getElementById('name').value;
    const date = document.getElementById('date').value;

    if (name && date) {
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
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        location: document.getElementById('location').value,
        participants: document.getElementById('participants').value,
        type: document.getElementById('event_type').value,
        price: document.getElementById('price').value || 0
    };

    console.log("Form Submitted Successfully:", formData);
    alert("Event Created Successfully!");
    // Here you would typically use fetch() to send data to your Flask backend
}