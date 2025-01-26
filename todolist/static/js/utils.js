window.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

window.sendRequest = async function(url, method) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken,
            },
        });

        const data = await response.json();
        if (data.success) {
            return true;
        } else {
            console.error('Error:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Request failed:', error);
        return false;
    }
};
