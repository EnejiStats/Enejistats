const carousel = document.getElementById("carousel");

setInterval(() => {
  carousel.appendChild(carousel.children[0]);
}, 5000);
/* =====================
   Browse script starts here
   ===================== */

function filterPlayers() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const cards = document.querySelectorAll(".player-card");

  cards.forEach(card => {
    const name = card.querySelector("h4").textContent.toLowerCase();
    card.style.display = name.includes(input) ? "block" : "none";
  });
}

/* ==============================
   Contact us script starts here
   ============================== */
// Set current year in footer
document.getElementById("year").textContent = new Date().getFullYear();

/* ==============================
   Register script starts here
   ============================== */
// List of countries
const countries = ["Nigeria", "Ghana", "Kenya", "South Africa", "Egypt", "United Kingdom", "United States", "Germany", "France", "Brazil", "Argentina", "Spain", "Italy", "Cameroon", "Senegal", "Ivory Coast", "Morocco", "Algeria", "Tunisia"];

// League clubs data
const leagueClubs = {
  npfl: ["Enyimba FC", "Kano Pillars", "Rivers United", "Plateau United"],
  nnl1: ["Gombe United", "El-Kanemi Warriors", "ABS FC", "Insurance FC"],
  nnl2: ["Confluence Stars", "Ottasolo FC", "Beyond Limits", "Mighty Jets"],
  academy: ["Pepsi Academy", "Right to Dream", "Barcelona Academy", "Dream Team"]
};

const generalClubs = [
  "Lagos City FC", "Abuja FC", "Kano United", "Jos Plateau FC",
  "University of Lagos FC", "University of Nigeria Nsukka FC"
];

const allClubs = [
  ...leagueClubs.npfl,
  ...leagueClubs.nnl1,
  ...leagueClubs.nnl2,
  ...leagueClubs.academy,
  ...generalClubs
];

function initializeCountries() {
  const nationalitySelect = document.getElementById('playerNationality');
  countries.forEach(country => {
    const option = document.createElement('option');
    option.value = country.toLowerCase().replace(/\s+/g, '-');
    option.textContent = country;
    nationalitySelect.appendChild(option);
  });
}

function initializeClubAssociation() {
  const clubSelect = document.getElementById('club');
  allClubs.forEach(club => {
    const option = document.createElement('option');
    option.value = club.toLowerCase().replace(/\s+/g, '-');
    option.textContent = club;
    clubSelect.appendChild(option);
  });
}

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

  leagueClubDropdown.classList.add('hidden');
  generalClubDropdown.classList.add('hidden');
  leagueClubSelect.innerHTML = '<option value=\"\">Select Club/Team</option>';
  generalClubSelect.innerHTML = '<option value=\"\">Select Club/Team</option>';

  if (leagueClubs[league]) {
    leagueClubDropdown.classList.remove('hidden');
    leagueClubs[league].forEach(club => {
      const option = document.createElement('option');
      option.value = club.toLowerCase().replace(/\s+/g, '-');
      option.textContent = club;
      leagueClubSelect.appendChild(option);
    });
    clubAssociation.disabled = false;
  } else {
    generalClubDropdown.classList.remove('hidden');
    generalClubs.forEach(club => {
      const option = document.createElement('option');
      option.value = club.toLowerCase().replace(/\s+/g, '-');
      option.textContent = club;
      generalClubSelect.appendChild(option);
    });
    clubAssociation.disabled = true;
    clubAssociation.value = 'no';
    document.getElementById('clubDropdown').classList.add('hidden');
  }
}

function toggleClubDropdown() {
  const clubAssociation = document.getElementById('clubAssociation').value;
  const clubDropdown = document.getElementById('clubDropdown');
  clubDropdown.classList.toggle('hidden', clubAssociation !== 'yes');
}

function validateAuthFields() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const emailPattern = /^[^@]+@[^@]+\\.[^@]+$/;

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
    const maxSize = 20 * 1024;
    if (file.size > maxSize) {
      alert("Photo size must be 20KB or less.");
      return false;
    }
  }
  return true;
}

document.getElementById('registrationForm').addEventListener('submit', function(e) {
  e.preventDefault();
  if (!validateAuthFields() || !validatePhotoSize()) return;
  alert("Form submitted successfully (mock).");
});

document.addEventListener('DOMContentLoaded', function () {
  initializeCountries();
  initializeClubAssociation();
});
