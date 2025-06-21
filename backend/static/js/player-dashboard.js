
function switchTab(tabName) {
  // Hide all tab contents
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Remove active class from all buttons
  document.querySelectorAll('.tab-button').forEach(button => {
    button.classList.remove('active');
  });
  
  // Show selected tab and mark button as active
  document.getElementById(tabName).classList.add('active');
  event.target.classList.add('active');
}

function editBio() {
  document.getElementById('bioDisplay').style.display = 'none';
  document.getElementById('bioEdit').style.display = 'block';
  document.getElementById('saveBio').style.display = 'inline-block';
  document.getElementById('cancelBio').style.display = 'inline-block';
}

function cancelBioEdit() {
  document.getElementById('bioDisplay').style.display = 'block';
  document.getElementById('bioEdit').style.display = 'none';
  document.getElementById('saveBio').style.display = 'none';
  document.getElementById('cancelBio').style.display = 'none';
}

async function saveBio() {
  const bioText = document.getElementById('bioEdit').value;
  
  try {
    const response = await fetch('/api/update-player-bio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        player_id: '{{ player._id }}',
        bio: bioText
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      document.getElementById('bioDisplay').textContent = bioText || 'No bio available.';
      cancelBioEdit();
      alert('Bio updated successfully!');
    } else {
      alert('Failed to update bio: ' + result.message);
    }
  } catch (error) {
    alert('Error updating bio: ' + error.message);
  }
}

function editAwards() {
  document.getElementById('awardsDisplay').style.display = 'none';
  document.getElementById('awardsEdit').style.display = 'block';
  document.getElementById('saveAwards').style.display = 'inline-block';
  document.getElementById('cancelAwards').style.display = 'inline-block';
}

function cancelAwardsEdit() {
  document.getElementById('awardsDisplay').style.display = 'block';
  document.getElementById('awardsEdit').style.display = 'none';
  document.getElementById('saveAwards').style.display = 'none';
  document.getElementById('cancelAwards').style.display = 'none';
}

async function saveAwards() {
  const awardsText = document.getElementById('awardsEdit').value;
  const awards = awardsText.split('\n').filter(award => award.trim().length > 0);
  
  try {
    const response = await fetch('/api/update-player-awards', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        player_id: '{{ player._id }}',
        awards: awards
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      const displayDiv = document.getElementById('awardsDisplay');
      if (awards.length > 0) {
        displayDiv.innerHTML = awards.map(award => `<p>• ${award}</p>`).join('');
      } else {
        displayDiv.textContent = 'No awards recorded.';
      }
      cancelAwardsEdit();
      alert('Awards updated successfully!');
    } else {
      alert('Failed to update awards: ' + result.message);
    }
  } catch (error) {
    alert('Error updating awards: ' + error.message);
  }
}
