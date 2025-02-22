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
        button.closest('a').remove();
    } else {
        console.error('Failed to delete category');
    }
}
