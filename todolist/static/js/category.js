// Delete Category
async function deleteCategory(categoryId) {
    const url = `/category/${categoryId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        window.location.reload();
    }
}

// Edit Category
async function editCategory(categoryId, formData) {
    const url = `/category/${categoryId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const data = await sendRequest(url, 'PATCH', requestBody);
    if (data.success) {
        window.location.reload();
    }
}

// Edit Category forms submission listeners
document.querySelectorAll('.edit-category-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = form.dataset.id;
        const formData = new FormData(form);

        await editCategory(id, formData);
    });
});

// Create Category
const createCategoryForm = document.getElementById('create-category-form');
if (createCategoryForm) {
    createCategoryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = '/category/create/';
        const formData = new FormData(e.target);
        formData.delete('csrfmiddlewaretoken');
        const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

        const data = await sendRequest(url, 'POST', requestBody);
        if (data.success) {
            window.location.reload();
        }
    });
}
