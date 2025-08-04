
function showMessage(text, type = 'success') {
    const msg = document.getElementById('message');
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

    msg.innerHTML = icon + text;
    msg.className = `message visible ${type}`;
}

async function verifyCode() {
    const code = document.getElementById('code').value.trim();
    const phone = localStorage.getItem('phone');

    try {
        const response = await fetch('/auth/verify_code/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code })
        });

        const data = await response.json();

        if (response.ok && data.access && data.refresh) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            showMessage('Code verified! You are logged in.', 'success');
        } else {
            showMessage(data.detail || 'Invalid code. Try again.', 'error');
        }
    } catch (err) {
        showMessage('Server error. Please try again.', 'error');
    }
}

async function resendCode() {
    try {
        const response = await fetch('/auth/resend_code/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: localStorage.getItem('phone') || '' })
        });

        if (response.ok) {
            showMessage('Code resent successfully.', 'success');
        } else {
            const data = await response.json();
            showMessage(data.error || 'Failed to resend code.', 'error');
        }
    } catch (err) {
        showMessage('Error resending code.', 'error');
    }
}
