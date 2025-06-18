// static/js/stats-area.js

document.getElementById("year").textContent = new Date().getFullYear();

function handlePlayerClick() {
  const token = localStorage.getItem("authToken");
  if (token) {
    window.location.href = "/player-dashboard";
  } else {
    window.location.href = "/login";
  }
}
