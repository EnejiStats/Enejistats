// Update footer year
document.getElementById("year").textContent = new Date().getFullYear();

// Redirect to player dashboard or login depending on cookie
document.getElementById("player-btn").addEventListener("click", () => {
  const token = getCookie("access_token");
  if (token) {
    window.location.href = "/player-dashboard";
  } else {
    window.location.href = "/login";
  }
});

// Helper function to read cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}
