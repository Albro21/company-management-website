window.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function deleteProject(button) {
    const projectId = button.getAttribute('data-project-id');

    fetch(`/${projectId}/delete-project/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.closest('a').remove();
        } else {
            console.error('Error completing task:', data.error);
        }
    })
    .catch(error => console.error('Request failed:', error));
}

function deleteCategory(button) {
    const categoryId = button.getAttribute('data-category-id');

    fetch(`/${categoryId}/delete-category/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.closest('a').remove();
        } else {
            console.error('Error completing task:', data.error);
        }
    })
    .catch(error => console.error('Request failed:', error));
}