
// Widget state variables
let selectedPlayer = null;
let matchClock = { minutes: 0, seconds: 0, isRunning: false, extraTime: 0 };
let clockInterval = null;
let currentStats = {
  goals: 0, shotsOn: 0, shotsOff: 0, shortPassesSuccessful: 0, shortPassesUnsuccessful: 0,
  longPassesSuccessful: 0, longPassesUnsuccessful: 0, crossesSuccessful: 0, crossesUnsuccessful: 0,
  interceptions: 0, tackles: 0, clearances: 0, gkSaves: 0, yellowCards: 0, redCards: 0,
  fouls: 0, offsides: 0
};

// Sample data
const leagues = ['Nigerian Professional Football League', 'Nigerian National League One', 'Nigerian National League Two'];
const teams = ['Rivers United', 'Enyimba', 'Kano Pillars', 'Plateau United', 'Akwa United'];
const players = [
  { id: 1, name: 'John Doe', position: 'ST', club: 'Rivers United' },
  { id: 2, name: 'Jane Smith', position: 'CM', club: 'Enyimba' },
  { id: 3, name: 'Mike Johnson', position: 'CB', club: 'Kano Pillars' }
];

// Initialize the widget
document.addEventListener('DOMContentLoaded', function() {
  loadLeagues();
  document.getElementById('matchDate').value = new Date().toISOString().split('T')[0];
});

function switchWidget(widgetName) {
  // Hide all widget contents
  document.querySelectorAll('.widget-content').forEach(widget => {
    widget.classList.remove('active');
  });
  
  // Remove active class from all buttons
  document.querySelectorAll('.widget-tab').forEach(button => {
    button.classList.remove('active');
  });
  
  // Show selected widget and mark button as active
  document.getElementById(widgetName).classList.add('active');
  event.target.classList.add('active');
}

function loadLeagues() {
  const leagueSelect = document.getElementById('leagueSelect');
  leagues.forEach(league => {
    const option = document.createElement('option');
    option.value = league;
    option.textContent = league;
    leagueSelect.appendChild(option);
  });
}

function loadTeams() {
  const homeTeamSelect = document.getElementById('homeTeam');
  const awayTeamSelect = document.getElementById('awayTeam');
  
  // Clear existing options
  homeTeamSelect.innerHTML = '<option value="">Select Home Team</option>';
  awayTeamSelect.innerHTML = '<option value="">Select Away Team</option>';
  
  teams.forEach(team => {
    const homeOption = document.createElement('option');
    homeOption.value = team;
    homeOption.textContent = team;
    homeTeamSelect.appendChild(homeOption);
    
    const awayOption = document.createElement('option');
    awayOption.value = team;
    awayOption.textContent = team;
    awayTeamSelect.appendChild(awayOption);
  });
}

function searchPlayers() {
  const searchTerm = document.getElementById('playerSearch').value.toLowerCase();
  const dropdown = document.getElementById('playerDropdown');
  
  if (searchTerm.length < 2) {
    dropdown.style.display = 'none';
    return;
  }
  
  const filteredPlayers = players.filter(player => 
    player.name.toLowerCase().includes(searchTerm) ||
    player.position.toLowerCase().includes(searchTerm) ||
    player.club.toLowerCase().includes(searchTerm)
  );
  
  dropdown.innerHTML = '';
  filteredPlayers.forEach(player => {
    const option = document.createElement('div');
    option.className = 'player-option';
    option.textContent = `${player.name} - ${player.position} - ${player.club}`;
    option.onclick = () => selectPlayer(player);
    dropdown.appendChild(option);
  });
  
  dropdown.style.display = filteredPlayers.length > 0 ? 'block' : 'none';
}

function selectPlayer(player) {
  selectedPlayer = player;
  document.getElementById('playerSearch').value = player.name;
  document.getElementById('selectedPlayerName').textContent = player.name;
  document.getElementById('selectedPlayerPosition').textContent = player.position;
  document.getElementById('selectedPlayerClub').textContent = player.club;
  document.getElementById('selectedPlayerInfo').style.display = 'block';
  document.getElementById('playerDropdown').style.display = 'none';
}

function startClock() {
  if (!matchClock.isRunning) {
    matchClock.isRunning = true;
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('pauseBtn').style.display = 'inline-block';
    
    clockInterval = setInterval(() => {
      matchClock.seconds++;
      if (matchClock.seconds >= 60) {
        matchClock.seconds = 0;
        matchClock.minutes++;
      }
      updateClockDisplay();
    }, 1000);
  }
}

function pauseClock() {
  if (matchClock.isRunning) {
    matchClock.isRunning = false;
    clearInterval(clockInterval);
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('pauseBtn').style.display = 'none';
  }
}

function resetClock() {
  matchClock = { minutes: 0, seconds: 0, isRunning: false, extraTime: 0 };
  clearInterval(clockInterval);
  document.getElementById('startBtn').style.display = 'inline-block';
  document.getElementById('pauseBtn').style.display = 'none';
  updateClockDisplay();
}

function addExtraTime() {
  matchClock.extraTime += 1;
  updateClockDisplay();
}

function updateClockDisplay() {
  const display = document.getElementById('clockDisplay');
  const minutes = String(matchClock.minutes).padStart(2, '0');
  const seconds = String(matchClock.seconds).padStart(2, '0');
  display.textContent = `${minutes}:${seconds}`;
  
  document.getElementById('extraTimeDisplay').textContent = `Extra Time: +${matchClock.extraTime}`;
  
  // Update half indicator
  const halfIndicator = document.getElementById('halfIndicator');
  if (matchClock.minutes < 45) {
    halfIndicator.textContent = 'First Half';
  } else if (matchClock.minutes < 90) {
    halfIndicator.textContent = 'Second Half';
  } else {
    halfIndicator.textContent = 'Extra Time';
  }
}

function updateMetric(metric, change) {
  if (currentStats.hasOwnProperty(metric)) {
    currentStats[metric] = Math.max(0, currentStats[metric] + change);
    document.getElementById(metric).textContent = currentStats[metric];
    calculateLiveRating();
  }
}

function calculateLiveRating() {
  // Simple rating calculation based on performance metrics
  let rating = 6.0; // Base rating
  
  // Positive actions
  rating += currentStats.goals * 1.0;
  rating += currentStats.shotsOn * 0.2;
  rating += (currentStats.shortPassesSuccessful + currentStats.longPassesSuccessful) * 0.05;
  rating += (currentStats.crossesSuccessful) * 0.1;
  rating += currentStats.interceptions * 0.3;
  rating += currentStats.tackles * 0.2;
  rating += currentStats.clearances * 0.1;
  rating += currentStats.gkSaves * 0.4;
  
  // Negative actions
  rating -= currentStats.shotsOff * 0.1;
  rating -= (currentStats.shortPassesUnsuccessful + currentStats.longPassesUnsuccessful) * 0.05;
  rating -= currentStats.crossesUnsuccessful * 0.05;
  rating -= currentStats.yellowCards * 0.5;
  rating -= currentStats.redCards * 2.0;
  rating -= currentStats.fouls * 0.1;
  rating -= currentStats.offsides * 0.2;
  
  // Cap rating between 1.0 and 10.0
  rating = Math.max(1.0, Math.min(10.0, rating));
  
  document.getElementById('liveRating').textContent = rating.toFixed(1);
}

function handleSubstitution() {
  if (selectedPlayer && matchClock.minutes > 0) {
    const subTime = `${matchClock.minutes}:${String(matchClock.seconds).padStart(2, '0')}`;
    document.getElementById('substitutionTime').textContent = `Substituted at ${subTime}`;
    alert(`${selectedPlayer.name} substituted at ${subTime}`);
  } else {
    alert('Please select a player and start the match clock first.');
  }
}

function submitMatchStats() {
  if (!selectedPlayer) {
    alert('Please select a player first.');
    return;
  }
  
  const homeTeam = document.getElementById('homeTeam').value;
  const awayTeam = document.getElementById('awayTeam').value;
  const matchDate = document.getElementById('matchDate').value;
  const league = document.getElementById('leagueSelect').value;
  
  if (!homeTeam || !awayTeam || !matchDate || !league) {
    alert('Please fill in all match setup fields.');
    return;
  }
  
  const matchData = {
    player_id: selectedPlayer.id,
    home_team: homeTeam,
    away_team: awayTeam,
    match_date: matchDate,
    league: league,
    stats: currentStats,
    performance_rating: parseFloat(document.getElementById('liveRating').textContent),
    match_duration: `${matchClock.minutes}:${String(matchClock.seconds).padStart(2, '0')}`,
    extra_time: matchClock.extraTime
  };
  
  // Submit to server
  fetch('/api/submit-match-stats', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(matchData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Match statistics submitted successfully!');
      resetAllStats();
    } else {
      alert('Failed to submit statistics: ' + data.message);
    }
  })
  .catch(error => {
    alert('Error submitting statistics: ' + error.message);
  });
}

function resetAllStats() {
  // Reset all metrics to 0
  Object.keys(currentStats).forEach(metric => {
    currentStats[metric] = 0;
    document.getElementById(metric).textContent = '0';
  });
  
  // Reset rating
  document.getElementById('liveRating').textContent = '6.0';
  
  // Clear player selection
  selectedPlayer = null;
  document.getElementById('playerSearch').value = '';
  document.getElementById('selectedPlayerInfo').style.display = 'none';
  
  // Clear substitution time
  document.getElementById('substitutionTime').textContent = '';
  
  alert('All statistics have been reset.');
}

// Close player dropdown when clicking outside
document.addEventListener('click', function(e) {
  const searchContainer = document.querySelector('.player-search');
  const dropdown = document.getElementById('playerDropdown');
  
  if (searchContainer && !searchContainer.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});
