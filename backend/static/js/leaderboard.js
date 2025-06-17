const players = Array.from({ length: 87 }, (_, i) => ({
  id: i + 1,
  rank: i + 1,
  name: `Player ${i + 1}`,
  position: ["Striker", "Midfielder", "Defender", "Goalkeeper"][i % 4],
  score: (Math.random() * 30 + 70).toFixed(1),
  img: `https://via.placeholder.com/60?text=P${i + 1}`
}));

let currentWeek = 1;
let currentPage = 1;
const perPage = 20;

function renderLeaderboard(data, page) {
  const container = document.getElementById("leaderboard");
  container.innerHTML = "";

  const start = (page - 1) * perPage;
  const end = start + perPage;
  const pageData = data.slice(start, end);

  pageData.forEach(player => {
    const row = document.createElement("div");
    row.className = "leaderboard-row";
    row.onclick = () => {
      window.location.href = `player-dashboard.html?id=${player.id}`;
    };
    row.innerHTML = `
      <div class="rank">${player.rank}</div>
      <img class="player-photo" src="${player.img}" alt="${player.name}">
      <div class="player-info">
        <h4>${player.name}</h4>
        <p>${player.position}</p>
      </div>
      <div class="score-card">${player.score}</div>
    `;
    container.appendChild(row);
  });

  renderPagination(data.length, page);
}

function renderPagination(totalItems, currentPage) {
  const pageCount = Math.ceil(totalItems / perPage);
  const container = document.getElementById("pagination");
  container.innerHTML = "";

  for (let i = 1; i <= pageCount; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    if (i === currentPage) btn.classList.add("active");
    btn.onclick = () => {
      currentPage = i;
      filterPlayers();
    };
    container.appendChild(btn);
  }
}

function filterPlayers() {
  const term = document.getElementById("searchInput").value.toLowerCase();
  const filtered = players.filter(p =>
    p.name.toLowerCase().includes(term) || p.position.toLowerCase().includes(term)
  );
  renderLeaderboard(filtered, currentPage);
}

function changeWeek(delta) {
  currentWeek += delta;
  if (currentWeek < 1) currentWeek = 1;
  document.getElementById("weekDisplay").textContent = "Week " + currentWeek;
  alert("Mock: Week " + currentWeek + " data loaded.");
}

document.getElementById("year").textContent = new Date().getFullYear();
renderLeaderboard(players, currentPage);
