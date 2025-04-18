window.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

window.sendRequest = async function(url, method, body = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken,
            },
        };

        if (body) {
            options.body = body;
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            console.error('Server returned error', response.status);
            return false;
        }

        const data = await response.json();
        return data
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

function closeWindow(button){
    const elementId = button.getAttribute('data-close-id');
    document.getElementById(elementId).style.display = 'none';
}

function openWindow(button){
    const elementId = button.getAttribute('data-open-id');
    document.getElementById(elementId).style.display = 'flex';
}

function openCloseWindows(button){
    const openId = button.getAttribute('data-open-id');
    const closeId = button.getAttribute('data-close-id');
    document.getElementById(closeId).style.display = 'none';
    document.getElementById(openId).style.display = 'flex';
}

// Hides empty task groups if all tasks in the group are hidden or if there are no tasks
window.hideEmptyTaskGroups = function() {
    document.querySelectorAll(".task-group").forEach(group => {
        const tasks = group.querySelectorAll(".task");
        
        //   Check if there are no tasks   or   if all tasks are hidden
        const isEmpty = tasks.length === 0 || [...tasks].every(task => task.style.display === "none");

        // Toggle visibility of the task group
        group.classList.replace(isEmpty ? "d-flex" : "d-none", isEmpty ? "d-none" : "d-flex");
    });
}

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

