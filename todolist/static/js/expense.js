// Delete Expense
async function deleteExpense(expenseId) {
    const url = `/teams/expense/${expenseId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        window.location.reload();
    }
}

// Upload Expense
uploadDocumentForm = document.getElementById('upload-expense-form');
if (uploadDocumentForm) {
    uploadDocumentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = '/teams/expense/create/';
        const formData = new FormData(e.target);

        const data = await sendRequest(url, 'POST', formData);
        if (data.success) {
            window.location.reload();
        }
    });
}

// Edit Expense
async function editExpense(expenseId, formData) {
    const url = `/teams/expense/${expenseId}/edit/`;
    const data = await sendRequest(url, 'POST', formData);
    if (data.success) {
        window.location.reload();
    }
}

// Edit Expense forms submission listeners
document.querySelectorAll('.edit-expense-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editExpense(id, formData);
    });
});
