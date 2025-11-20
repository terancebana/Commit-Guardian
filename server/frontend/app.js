document.addEventListener('DOMContentLoaded', () => {
    checkStatus();

    // Attach event listeners to buttons
    document.getElementById('btn-push-junk').addEventListener('click', pushJunk);
    document.getElementById('btn-refresh').addEventListener('click', checkStatus);
});

async function checkStatus() {
    const loadingEl = document.getElementById('loading-message');
    const dashboardEl = document.getElementById('dashboard');
    const statusHeader = document.getElementById('status-header');
    const statusMsg = document.getElementById('status-message');
    const actionContainer = document.getElementById('action-container');

    // Show loading
    loadingEl.classList.remove('hidden');
    dashboardEl.classList.add('hidden');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update Stats
        document.getElementById('streak-count').textContent = data.current_streak;
        document.getElementById('last-push-date').textContent = data.last_push_date || "Never";

        // Update UI based on status
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

        // Show dashboard
        loadingEl.classList.add('hidden');
        dashboardEl.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        loadingEl.textContent = "Error connecting to server.";
    }
}

async function pushJunk() {
    if (!confirm("Are you sure? This will push a dummy text file to your junk repo.")) return;

    const btn = document.getElementById('btn-push-junk');
    const originalText = btn.textContent;
    btn.textContent = "Pushing...";
    btn.disabled = true;

    try {
        // NOTE: We haven't built this endpoint in Python yet. It will 404.
        const response = await fetch('/api/push-junk', { method: 'POST' });
        
        if (response.ok) {
            alert("Success! Junk commit pushed.");
            checkStatus(); // Refresh to see green
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