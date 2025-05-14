// Update get parameters on tab change
function updateTab(tab) {
    const url = new URL(window.location);
    url.searchParams.set('tab', tab);
    window.history.pushState({}, '', url);
}

// Delete Document
async function deleteDocument(documentId) {
    const url = `/teams/document/${documentId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        window.location.reload();
    }
}

// Upload Document
uploadDocumentForm = document.getElementById('upload-document-form');
if (uploadDocumentForm) {
    uploadDocumentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = '/teams/document/create/';
        const formData = new FormData(e.target);

        const data = await sendRequest(url, 'POST', formData);
        if (data.success) {
            window.location.reload();
        }
    });
}

// Edit Document
async function editDocument(documentId, formData) {
    const url = `/teams/document/${documentId}/edit/`;
    const data = await sendRequest(url, 'POST', formData);
    formData.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });
    if (data.success) {
        window.location.reload();
    }
}

// Edit Document forms submission listeners
document.querySelectorAll('.edit-document-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = form.dataset.id;
        const formData = new FormData(form);
        
        await editDocument(id, formData);
    });
});

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
