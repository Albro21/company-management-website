window.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

window.sendRequest = async function(url, method, requestBody = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken,
            },
            body: requestBody,
        };
        
        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error(`Server error | Status: ${response.status} | Message: ${data.error}`);
            return false;
        }

        return data;
        
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

// Displays image after upload
function previewImage(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    
    reader.onload = function() {
        document.getElementById("image_preview").src = reader.result;
    };
    
    if (file) {
        reader.readAsDataURL(file);
    }
}

