const status = document.getElementById('status');
document.getElementById('save').addEventListener('click', async () => {
    status.textContent = 'saving…';
    try {
        const resp = await fetch('/progress', {
            method: 'POST',
            headers: {'Content-Type': 'text/plain'},
            body: document.getElementById('content').value,
        });
        const text = await resp.text();
        status.textContent = text;
        status.style.color = resp.ok ? '#6a9955' : '#f48771';
    } catch (err) {
        status.textContent = String(err);
        status.style.color = '#f48771';
    }
});