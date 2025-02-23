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

function openCloseForm(element) {
    const closeId = element.getAttribute('data-close-id'); 
    const openId = element.getAttribute('data-open-id');

    document.getElementById(closeId).style.display = 'none';
    document.getElementById(openId).style.display = 'flex';
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".note-form").forEach(form => {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const projectId = this.closest(".list-group-item-settings").id.replace("edit-project-", "");

            const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

            const url = `/project/${projectId}/edit/`;
            const method = "POST";

            const data = await sendRequest(url, method, requestBody);

            console.log(data);

            if (data && data.success) {
                location.reload();
            } else {
                console.error("Server error:", data ? data.error : "No response");
            }
        });
    });
});

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
