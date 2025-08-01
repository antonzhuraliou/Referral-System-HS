
function showStatus(message, type = 'success') {
  const status = document.getElementById('status');
  let icon = '';

  if (type === 'success') {
    icon = `
      <svg viewBox="0 0 24 24" fill="none" stroke="#1a7f4a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 6L9 17l-5-5"/>
      </svg>`;
  } else if (type === 'error') {
    icon = `
      <svg viewBox="0 0 24 24" fill="none" stroke="#a42828" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>`;
  }

  status.innerHTML = icon + message;
  status.className = `status visible ${type}`;
}

async function sendCode() {
  const phone = document.getElementById('phone').value.trim();
  if (!phone) {
    showStatus('Please enter your phone number.', 'error');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/send_code/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await res.json();

    if (res.ok) {
      showStatus('Verification code has been sent successfully. Redirecting...', 'success');
      localStorage.setItem('phone', phone);

      setTimeout(() => {
        window.location.href = '/verify_page/';
      }, 1800);
    } else {
      showStatus(data.error || data.detail || 'Failed to send code.', 'error');
    }
  } catch (error) {
    showStatus('Network error. Please try again.', 'error');
  }
}
