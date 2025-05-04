document.getElementById('create-task-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const url = '/task/create/';
    const formData = new FormData(e.target);
    formData.delete('csrfmiddlewaretoken');

    const categories = [];
    formData.getAll('categories').forEach(value => {
        categories.push(value);
    });

    const requestBody = Object.fromEntries(formData.entries());
    requestBody.categories = categories;

    const success = await sendRequest(url, 'POST', JSON.stringify(requestBody));
    if (success) {
        window.location.reload();
    }
});

async function editTask(taskId, formData) {
    const url = `/task/${taskId}/edit/`;
    const categories = [];
    formData.getAll('categories').forEach(value => {
        categories.push(value);
    });

    const requestBody = Object.fromEntries(formData.entries());
    requestBody.categories = categories;

    const success = await sendRequest(url, 'PATCH', JSON.stringify(requestBody));
    if (success) {
        window.location.reload();
    }
}

document.querySelectorAll('.edit-task-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editTask(id, formData);
    });
});
