csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Helper function for sending requests to the server
window.sendRequest = async function(url, method, requestBody = null) {
    try {
        const isFormData = requestBody instanceof FormData;

        const options = {
            method: method,
            headers: isFormData ? { 'X-CSRFToken': csrfToken } : {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: requestBody,
        };

        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error(`Server error | Status: ${response.status} | Message: ${data.error}`);
        }

        return data;

    } catch (error) {
        console.error('Request failed:', error);
        return false;
    }
};

// Helper function for displaying toast messages
window.showToast = function(message, type = 'info') {
    const container = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { autohide: true, animation: true, delay: 3000 });
    bsToast.show();
};

// Set toast to show it after page load
window.queueToast = function(message, type = 'info') {
    sessionStorage.setItem('toastMessage', JSON.stringify({message: message, type: type}));
};

// Show toast message after page load
document.addEventListener("DOMContentLoaded", () => {
    const toastData = sessionStorage.getItem('toastMessage');
    if (toastData) {
        const { message, type } = JSON.parse(toastData);
        showToast(message, type);
        sessionStorage.removeItem('toastMessage');
    }
});

// Change text color based on background
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
