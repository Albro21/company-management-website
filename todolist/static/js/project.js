// Delete Project
async function deleteProject(projectId) {
    const url = `/project/${projectId}/delete/`;
    const success = await sendRequest(url, 'DELETE');
    if (success) {
        window.location.reload();
    }
}

// Edit Project
async function editProject(projectId, formData) {
    const url = `/project/${projectId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const success = await sendRequest(url, 'PATCH', requestBody);
    if (success) {
        window.location.reload();
    }
}

// Edit Project forms submission listeners
document.querySelectorAll('.edit-project-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editProject(id, formData);
    });
});

// Create Project
const createProjectForm = document.getElementById('create-project-form');
if (createProjectForm) {
    createProjectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = '/project/create/';
        const formData = new FormData(e.target);
        formData.delete('csrfmiddlewaretoken');
        const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

        const success = await sendRequest(url, 'POST', requestBody);
        if (success) {
            window.location.reload();
        }
    });
}