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
