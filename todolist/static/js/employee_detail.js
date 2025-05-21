// Update get parameters on tab change
function updateTab(tab) {
    const url = new URL(window.location);
    url.searchParams.set('tab', tab);
    window.history.pushState({}, '', url);
}

// Edit Employee
editEmployeeForm = document.getElementById('edit-employee-form');
employeeId = editEmployeeForm.dataset.id;
if (editEmployeeForm) {
    editEmployeeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = `/teams/employee/${employeeId}/edit/`;
        const formData = new FormData(e.target);
        formData.delete('csrfmiddlewaretoken');
        const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    
        const data = await sendRequest(url, 'PATCH', requestBody);
        if (data.success) {
            queueToast('Employee updated', 'success');
            window.location.reload();
        } else {
            showToast(data.error, 'danger');
        }
    });
}
