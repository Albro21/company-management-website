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

document.addEventListener("DOMContentLoaded", function() {
    const elements = document.querySelectorAll('.change-text-color');
    elements.forEach(function(element) {
        const backgroundColor = window.getComputedStyle(element).backgroundColor;
        
        const rgb = backgroundColor.match(/\d+/g);
        const r = parseInt(rgb[0]);
        const g = parseInt(rgb[1]);
        const b = parseInt(rgb[2]);

        const brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b;

        if (brightness > 128) {
            element.style.color = 'black';
        } else {
            element.style.color = 'white';
        }
    });
});
