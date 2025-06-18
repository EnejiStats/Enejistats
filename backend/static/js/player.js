document.getElementById("year").textContent = new Date().getFullYear();

// Auto-redirect if logged in
const token = document.cookie
  .split("; ")
  .find(row => row.startsWith("access_token="));
if (token) {
  window.location.href = "/dashboard";
}
