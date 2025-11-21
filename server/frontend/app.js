document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    const pushBtn = document.getElementById('btn-push-junk');
    const refreshBtn = document.getElementById('btn-refresh');
    const logoutBtn = document.getElementById('btn-logout');
    const simulateBtn = document.getElementById('btn-simulate');
    const clearSimBtn = document.getElementById('btn-clear-simulate');
    const sendEmailBtn = document.getElementById('btn-send-email');
    if (pushBtn) pushBtn.addEventListener('click', pushJunk);
    if (refreshBtn) refreshBtn.addEventListener('click', checkStatus);
    if (logoutBtn) logoutBtn.addEventListener('click', logout);
    if (simulateBtn) simulateBtn.addEventListener('click', simulateMiss);
    if (clearSimBtn) clearSimBtn.addEventListener('click', clearSimulation);
    if (sendEmailBtn) sendEmailBtn.addEventListener('click', sendTestEmail);
});

function logout() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/login.html';
        });
}

async function checkStatus() {
    const loadingEl = document.getElementById('loading-message');
    const dashboardEl = document.getElementById('dashboard');
    const statusHeader = document.getElementById('status-header');
    const statusMsg = document.getElementById('status-message');
    const actionContainer = document.getElementById('action-container');

    loadingEl.classList.remove('hidden');
    dashboardEl.classList.add('hidden');

    try {
        const response = await fetch('/api/status');
        if (response.status === 401) {
            window.location.href = '/login.html';
            return;
        }
        const data = await response.json();

        document.getElementById('streak-count').textContent = data.current_streak;
        document.getElementById('last-push-date').textContent = data.last_push_date || "Never";

        if (data.pushed_today) {
            statusHeader.textContent = "You are Safe!";
            statusHeader.className = "status-safe";
            statusMsg.textContent = "Great job! You have already pushed code today.";
            actionContainer.classList.add('hidden');
        } else {
            statusHeader.textContent = "Your streak might reset soon!";
            statusHeader.className = "status-danger";
            statusMsg.textContent = "No public activity detected on GitHub today.";
            actionContainer.classList.remove('hidden');
        }

        loadingEl.classList.add('hidden');
        dashboardEl.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        if (loadingEl) loadingEl.textContent = "Error connecting to server.";
    }
}

async function pushJunk() {
    if (!confirm("Are you sure? This will push a dummy text file to your junk repo.")) return;

    const btn = document.getElementById('btn-push-junk');
    const originalText = btn.textContent;
    btn.textContent = "Pushing...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/push-junk', { method: 'POST' });

        if (response.ok) {
            alert("Success! Junk commit pushed.");
            checkStatus();
        } else if (response.status === 401) {
            window.location.href = '/login.html';
        } else {
            alert("Failed to push. Check server logs.");
        }
    } catch (error) {
        alert("Network error.");
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function simulateMiss() {
    const res = await fetch('/api/simulate-miss', { method: 'POST' });
    if (res.ok) {
        alert('Simulation enabled: dashboard will show as if you did not push today.');
        checkStatus();
    } else if (res.status === 401) {
        window.location.href = '/login.html';
    } else {
        alert('Failed to enable simulation.');
    }
}

async function clearSimulation() {
    const res = await fetch('/api/clear-simulate', { method: 'POST' });
    if (res.ok) {
        alert('Simulation cleared.');
        checkStatus();
    } else if (res.status === 401) {
        window.location.href = '/login.html';
    } else {
        alert('Failed to clear simulation.');
    }
}

async function sendTestEmail() {
    if (!confirm('Send a test alert email to the logged-in user?')) return;
    const res = await fetch('/api/send-test-email', { method: 'POST' });
    if (res.ok) {
        alert('Test email sent (or attempted).');
    } else if (res.status === 401) {
        window.location.href = '/login.html';
    } else {
        alert('Failed to send test email. Check server logs or email configuration.');
    }
}