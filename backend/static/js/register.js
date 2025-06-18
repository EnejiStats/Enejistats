
// Countries list for nationality dropdown
const countries = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
  "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
  "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
  "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia",
  "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
  "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia",
  "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
  "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
  "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",
  "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
  "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
  "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand",
  "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine",
  "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
  "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
  "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan",
  "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania",
  "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
  "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
  "Yemen", "Zambia", "Zimbabwe"
];

// Position data
const positions = {
  goalkeeper: [
    { value: "GK", text: "GK - Goalkeeper" },
    { value: "SWK", text: "SWK - Sweeper Keeper" }
  ],
  defender: [
    { value: "CB", text: "CB - Centre Back" },
    { value: "RCB", text: "RCB - Right Centre Back" },
    { value: "LCB", text: "LCB - Left Centre Back" },
    { value: "LB", text: "LB - Left Back" },
    { value: "RB", text: "RB - Right Back" },
    { value: "LWB", text: "LWB - Left Wing Back" },
    { value: "RWB", text: "RWB - Right Wing Back" }
  ],
  midfielder: [
    { value: "CDM", text: "CDM - Central Defensive Midfielder" },
    { value: "CM", text: "CM - Central Midfielder" },
    { value: "CAM", text: "CAM - Central Attacking Midfielder" },
    { value: "RM", text: "RM - Right Midfielder" },
    { value: "LM", text: "LM - Left Midfielder" },
    { value: "RW", text: "RW - Right Winger" },
    { value: "LW", text: "LW - Left Winger" },
    { value: "DM", text: "DM - Defensive Midfielder" },
    { value: "AM", text: "AM - Attacking Midfielder" }
  ],
  attacker: [
    { value: "ST", text: "ST - Striker" },
    { value: "CF", text: "CF - Centre Forward" },
    { value: "LF", text: "LF - Left Forward" },
    { value: "RF", text: "RF - Right Forward" },
    { value: "SS", text: "SS - Second Striker" }
  ]
};

// League clubs data
const leagueClubs = {
  npfl: [
    "Enyimba FC", "Kano Pillars", "Rivers United", "Plateau United", "Shooting Stars SC", "3SC Ibadan",
    "Akwa United", "Lobi Stars", "Heartland FC", "Rangers International", "Kwara United", "Nasarawa United",
    "Dakkada FC", "Sunshine Stars", "Wikki Tourist", "MFM FC", "FC IfeanyiUbah", "Katsina United",
    "Jigawa Golden Stars", "Warri Wolves"
  ],
  nnl1: [
    "Gombe United", "El-Kanemi Warriors", "ABS FC", "Insurance FC", "Real Sapphire", "Gateway United",
    "Bendel Insurance", "Osun United", "Delta Force", "COD United", "Niger Tornadoes", "Crown FC",
    "Go Round FC", "Adamawa United", "Sokoto United", "Zamfara United"
  ],
  nnl2: [
    "Confluence Stars", "Ottasolo FC", "Beyond Limits", "Mighty Jets", "Ekiti United", "Bayelsa United",
    "Sporting Supreme", "Liberty FC", "FC One Rocket", "Kogi United", "Yobe Desert Stars", "Gombe Bulls",
    "Kebbi United", "Taraba FC", "Jigawa Stars", "Bauchi United"
  ],
  academy: [
    "Pepsi Football Academy", "36 Lion FC Academy", "Right to Dream Academy Nigeria", "Barcelona Academy Lagos",
    "Manchester City Football School", "Lagos State FA Academy", "Flying Eagles Academy", "Golden Eaglets Academy",
    "Future Eagles Academy", "Dream Team Academy", "Crown FC Academy", "Shooting Stars Academy"
  ]
};

// General clubs for ***** and university
const generalClubs = [
  // ***** clubs
  "Lagos City FC", "Abuja FC", "Kano United", "Port Harcourt City", "Kaduna United", "Ibadan City FC",
  "Jos Plateau FC", "Maiduguri FC", "Calabar Rovers", "Warri City FC", "Benin City FC", "Lokoja United",
  
  // University clubs
  "University of Lagos FC", "University of Nigeria Nsukka FC", "Ahmadu Bello University FC", "University of Ibadan FC",
  "University of Benin FC", "Federal University of Technology Akure FC", "University of Port Harcourt FC",
  "Bayero University Kano FC", "University of Jos FC", "Federal University Lokoja FC", "Nnamdi Azikiwe University FC",
  "Michael Okpara University FC", "University of Calabar FC", "Rivers State University FC"
];

// All clubs for club association dropdown
const allClubs = [
  ...leagueClubs.npfl,
  ...leagueClubs.nnl1,
  ...leagueClubs.nnl2,
  ...leagueClubs.academy,
  ...generalClubs
];

// Initialize country dropdown
function initializeCountries() {
  const nationalitySelect = document.getElementById('playerNationality');
  countries.forEach(country => {
    const option = document.createElement('option');
    option.value = country.toLowerCase().replace(/\s+/g, '-');
    option.textContent = country;
    nationalitySelect.appendChild(option);
  });
}

// Initialize club association dropdown
function initializeClubAssociation() {
  const clubSelect = document.getElementById('club');
  allClubs.forEach(club => {
    const option = document.createElement('option');
    option.value = club.toLowerCase().replace(/\s+/g, '-');
    option.textContent = club;
    clubSelect.appendChild(option);
  });
}

// Show preferred positions based on category selection
function showPreferredPositions() {
  const category = document.getElementById('preferredPositionCategory').value;
  const optionsDiv = document.getElementById('preferredPositionOptions');
  const positionSelect = document.getElementById('preferredPosition');
  
  if (category) {
    optionsDiv.classList.remove('hidden');
    positionSelect.innerHTML = '<option value="">Select Position</option>';
    
    positions[category].forEach(position => {
      const option = document.createElement('option');
      option.value = position.value;
      option.textContent = position.text;
      positionSelect.appendChild(option);
    });
  } else {
    optionsDiv.classList.add('hidden');
  }
}

// Toggle other positions dropdown
function toggleOtherPositionsDropdown() {
  const panel = document.getElementById('otherPositionsPanel');
  const arrow = document.getElementById('dropdownArrow');
  
  if (panel.classList.contains('hidden')) {
    panel.classList.remove('hidden');
    arrow.classList.add('open');
  } else {
    panel.classList.add('hidden');
    arrow.classList.remove('open');
  }
}

// Update other positions display
function updateOtherPositionsDisplay() {
  const checkboxes = document.querySelectorAll('input[name="otherPositions"]:checked');
  const display = document.getElementById('otherPositionsDisplay');
  
  if (checkboxes.length === 0) {
    display.textContent = 'Click to select positions';
  } else if (checkboxes.length === 1) {
    display.textContent = checkboxes[0].value;
  } else {
    display.textContent = `${checkboxes.length} positions selected`;
  }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
  const dropdown = document.querySelector('.other-positions-dropdown');
  const panel = document.getElementById('otherPositionsPanel');
  const arrow = document.getElementById('dropdownArrow');
  
  if (!dropdown.contains(event.target)) {
    panel.classList.add('hidden');
    arrow.classList.remove('open');
  }
});

function displayFields() {
  const userType = document.getElementById('userType').value;
  document.querySelectorAll('.user-fields').forEach(field => field.classList.add('hidden'));
  
  if (userType === 'player') {
    document.getElementById('playerFields').classList.remove('hidden');
  } else if (userType === 'club') {
    document.getElementById('clubFields').classList.remove('hidden');
  } else if (userType === 'scout') {
    document.getElementById('scoutFields').classList.remove('hidden');
  }
}

function handleLeagueChange() {
  const league = document.getElementById('league').value;
  const leagueClubDropdown = document.getElementById('leagueClubDropdown');
  const generalClubDropdown = document.getElementById('generalClubDropdown');
  const leagueClubSelect = document.getElementById('leagueClub');
  const generalClubSelect = document.getElementById('generalClub');
  const clubAssociation = document.getElementById('clubAssociation');

  // Hide both dropdowns first
  leagueClubDropdown.classList.add('hidden');
  generalClubDropdown.classList.add('hidden');
  
  // Clear previous options
  leagueClubSelect.innerHTML = '<option value="">Select Club/Team</option>';
  generalClubSelect.innerHTML = '<option value="">Select Club/Team</option>';

  if (league === 'npfl' || league === 'nnl1' || league === 'nnl2' || league === 'academy') {
    // Show league-specific clubs
    leagueClubDropdown.classList.remove('hidden');
    const clubs = leagueClubs[league] || [];
    clubs.forEach(club => {
      const option = document.createElement('option');
      option.value = club.toLowerCase().replace(/\s+/g, '-');
      option.textContent = club;
      leagueClubSelect.appendChild(option);
    });
    
    // Enable club association for these leagues
    clubAssociation.disabled = false;
  } else if (league === '*****' || league === 'university') {
    // Show general clubs dropdown
    generalClubDropdown.classList.remove('hidden');
    generalClubs.forEach(club => {
      const option = document.createElement('option');
      option.value = club.toLowerCase().replace(/\s+/g, '-');
      option.textContent = club;
      generalClubSelect.appendChild(option);
    });
    
    // Disable club association for these leagues
    clubAssociation.disabled = true;
    clubAssociation.value = 'no';
    document.getElementById('clubDropdown').classList.add('hidden');
  }
}

function toggleClubDropdown() {
  const clubAssociation = document.getElementById('clubAssociation').value;
  const clubDropdown = document.getElementById('clubDropdown');
  
  if (clubAssociation === 'yes') {
    clubDropdown.classList.remove('hidden');
  } else {
    clubDropdown.classList.add('hidden');
  }
}

function validateAuthFields() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
  
  if (!emailPattern.test(email)) {
    alert("Please enter a valid email address.");
    return false;
  }
  if (password.length < 6) {
    alert("Password must be at least 6 characters long.");
    return false;
  }
  return true;
}

function validatePhotoSize() {
  const photoInput = document.getElementById('playerPhoto');
  if (photoInput.files.length > 0) {
    const file = photoInput.files[0];
    const maxSize = 20 * 1024; // 20KB in bytes
    if (file.size > maxSize) {
      alert("Photo size must be 20KB or less.");
      return false;
    }
  }
  return true;
}

document.getElementById('registrationForm').addEventListener('submit', function(e) {
  e.preventDefault();
  
  if (!validateAuthFields() || !validatePhotoSize()) {
    return;
  }
  
  // Create FormData object to handle form submission
  const formData = new FormData(this);
  
  // Submit form data to FastAPI backend
  fetch('/register', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert("Registration successful!");
      // Optionally redirect or reset form
      this.reset();
      document.querySelectorAll('.user-fields').forEach(field => field.classList.add('hidden'));
    } else {
      alert("Registration failed: " + data.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert("An error occurred during registration.");
  });
});

// Initialize dropdowns when page loads
document.addEventListener('DOMContentLoaded', function() {
  initializeCountries();
  initializeClubAssociation();
});
