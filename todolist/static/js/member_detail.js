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
        
        const url = `/teams/member/${employeeId}/edit/`;
        const formData = new FormData(e.target);
        const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    
        const data = await sendRequest(url, 'PATCH', requestBody);
        if (data.success) {
            window.location.reload();
        } else {
            alert("Please, enter a valid phone number (e.g. 0121 234 5678) or a number with an international call prefix");
        }
    });
}
