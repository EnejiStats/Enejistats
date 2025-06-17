const carousel = document.getElementById("carousel");

setInterval(() => {
  carousel.appendChild(carousel.children[0]);
}, 5000);
/* =====================
   Browse Page Styles
   ===================== */

function filterPlayers() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const cards = document.querySelectorAll(".player-card");

  cards.forEach(card => {
    const name = card.querySelector("h4").textContent.toLowerCase();
    card.style.display = name.includes(input) ? "block" : "none";
  });
}
