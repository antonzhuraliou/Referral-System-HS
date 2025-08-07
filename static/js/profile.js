
async function loadUserProfile() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/profile/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok) {
      const profile = data.profile;

      document.getElementById('phone').textContent = profile.phone || 'N/A';
      document.getElementById('ownInviteCode').textContent = profile.own_invite_code || 'N/A';

      const invitedByDiv = document.getElementById('invitedBy');
      const inviteForm = document.getElementById('inviteForm');

      if (profile.invited_by && profile.invited_by.invite_code) {
        invitedByDiv.textContent = profile.invited_by.invite_code;
        inviteForm.style.display = 'none';
      } else {
        invitedByDiv.textContent = 'You haven’t used an invite code yet.';
        inviteForm.style.display = 'block';
      }

      const referralsList = document.getElementById('referralsList');
      referralsList.innerHTML = '';
      if (profile.referrals && profile.referrals.length > 0) {
        profile.referrals.forEach(ref => {
          const li = document.createElement('li');
          li.textContent = ref.phone || `ID: ${ref.id}`;
          referralsList.appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.textContent = 'No referrals yet.';
        referralsList.appendChild(li);
      }
    } else {
      showMessage(data.detail || 'Failed to load profile.', 'error');
    }
  } catch (err) {
    showMessage('Network error.', 'error');
  }
}

async function submitInviteCode() {
  const code = document.getElementById('inviteInput').value.trim();
  if (!code) {
    showMessage('Please enter an invite code.', 'error');
    return;
  }

  const token = localStorage.getItem('access_token');
  try {
    const response = await fetch('/invite-code/use/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ invite_code: code })
    });

    const data = await response.json();

    if (response.ok) {
      showMessage(data.message || 'Invite code applied successfully.');
      loadUserProfile();
    } else {
      showMessage(data.error || 'Could not apply invite code.', 'error');
    }
  } catch (err) {
    showMessage('Network error.', 'error');
  }
}

function showMessage(text, type = 'success') {
  const msg = document.getElementById('message');
  msg.textContent = text;
  msg.className = `message visible ${type}`;
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/auth/send_code/';
}

loadUserProfile();
