async function deleteProject(projectId) {
    const url = `/project/${projectId}/delete/`;
    const success = await sendRequest(url, 'DELETE');
    if (success) {
        document.getElementById(`project-${projectId}`).remove();
    }
}

async function deleteCategory(categoryId) {
    const url = `/category/${categoryId}/delete/`;
    const success = await sendRequest(url, 'DELETE');
    if (success) {
        document.getElementById(`category-${categoryId}`).remove();
    }
}

async function updateProject(button) {
    event.preventDefault();

    const form = button.closest(".note-form");
    const formData = new FormData(form);
    const projectId = button.getAttribute('data-project-id');

    const url = `/project/${projectId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const success = await sendRequest(url, "POST", requestBody);

    if (success) {
        location.reload();
    }
}

async function updateCategory(button) {
    event.preventDefault();

    const form = button.closest(".note-form");
    const formData = new FormData(form);
    const categoryId = button.getAttribute('data-category-id');

    const url = `/category/${categoryId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const success = await sendRequest(url, "POST", requestBody);

    if (success) {
        location.reload();
    }
}
