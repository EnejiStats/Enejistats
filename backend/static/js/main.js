const carousel = document.getElementById("carousel");

setInterval(() => {
  carousel.appendChild(carousel.children[0]);
}, 5000);
