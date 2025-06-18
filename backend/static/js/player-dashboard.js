// Sample player data simulation (replace with real fetch if backend-connected)
const player = {
  first_name: "John",
  last_name: "Doe",
  dob: "2000-01-15",
  nationality: "Nigeria",
  preferred_position: "CM - Midfielder",
  club: "Lagos Stars FC",
  photo_url: "https://via.placeholder.com/150"
};

function calculateAge(dobString) {
  const dob = new Date(dobString);
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  if (
    today.getMonth() < dob.getMonth() ||
    (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate())
  ) {
    age--;
  }
  return age;
}

function populatePlayerDashboard() {
  document.getElementById("player-name").textContent = `${player.first_name} ${player.last_name}`;
  document.getElementById("player-dob").textContent = player.dob;
  document.getElementById("player-age").textContent = calculateAge(player.dob);
  document.getElementById("player-nationality").textContent = player.nationality;
  document.getElementById("player-position").textContent = player.preferred_position;
  document.getElementById("player-club").textContent = player.club;
  document.getElementById("player-photo").src = player.photo_url;
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(tabId).classList.add("active");
  document.querySelector(`.tab-btn[onclick*='${tabId}']`).classList.add("active");
}

window.onload = populatePlayerDashboard;

