async function deleteProject(projectId) {
    const url = `/project/${projectId}/delete/`;
    const success = await sendRequest(url, 'DELETE');
    if (success) {
        window.location.reload();
    }
}

async function deleteCategory(categoryId) {
    const url = `/category/${categoryId}/delete/`;
    const success = await sendRequest(url, 'DELETE');
    if (success) {
        window.location.reload();
    }
}

async function editProject(projectId, formData) {
    const url = `/project/${projectId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const success = await sendRequest(url, 'PATCH', requestBody);
    if (success) {
        window.location.reload();
    }
}

async function editCategory(categoryId, formData) {
    const url = `/category/${categoryId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const success = await sendRequest(url, 'PATCH', requestBody);
    if (success) {
        window.location.reload();
    }
}

document.querySelectorAll('.edit-project-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editProject(id, formData);
    });
});

document.querySelectorAll('.edit-category-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = form.dataset.id;
        const formData = new FormData(form);

        await editCategory(id, formData);
    });
});

document.getElementById('create-project-form').addEventListener('submit', async (e) => {
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

document.getElementById('create-category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = '/category/create/';
    const formData = new FormData(e.target);
    formData.delete('csrfmiddlewaretoken');
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const success = await sendRequest(url, 'POST', requestBody);
    if (success) {
        window.location.reload();
    }
});
