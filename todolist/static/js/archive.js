async function deleteProject(button) {
    const projectId = button.getAttribute('data-project-id');
    const url = `/${projectId}/delete-project/`;
    const method = 'DELETE';

    const success = await sendRequest(url, method);

    if (success) {
        const projectElement = document.getElementById(`project-${projectId}`);
        if (projectElement) {
            projectElement.remove();
        }
    } else {
        console.error('Failed to delete project');
    }
}

async function deleteCategory(button) {
    const categoryId = button.getAttribute('data-category-id');
    const url = `/${categoryId}/delete-category/`;
    const method = 'DELETE';

    const success = await sendRequest(url, method);

    if (success) {
        const categoryElement = document.getElementById(`category-${categoryId}`);
        if (categoryElement) {
            categoryElement.remove();
        }
    } else {
        console.error('Failed to delete category');
    }
}

function openCloseForm(element) {
    const closeId = element.getAttribute('data-close-id'); 
    const openId = element.getAttribute('data-open-id');

    document.getElementById(closeId).style.display = 'none';
    document.getElementById(openId).style.display = 'flex';
}

function updateProject(button) {
    const form = button.closest(".note-form");
    const formData = new FormData(form);
    const projectId = button.getAttribute('data-project-id');

    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const url = `/project/${projectId}/edit/`;
    const method = "POST";

    sendRequest(url, method, requestBody).then(data => {
        console.log(data);
        if (data && data.success) {
            location.reload();
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    });

    event.preventDefault();
}

function updateCategory(button) {
    const form = button.closest(".note-form");
    const formData = new FormData(form);
    const categoryId = button.getAttribute('data-category-id');

    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const url = `/category/${categoryId}/edit/`;
    const method = "POST";

    sendRequest(url, method, requestBody).then(data => {
        console.log(data);
        if (data && data.success) {
            location.reload();
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    });

    event.preventDefault();
}

function showCreationForm(button) {
    const formId = button.getAttribute('data-form-id');
    document.getElementById(formId).style.display = 'flex'; 
}

function closeCreationForm(button) {
    const formId = button.getAttribute('data-close-id');
    document.getElementById(formId).style.display = 'none'; 
}