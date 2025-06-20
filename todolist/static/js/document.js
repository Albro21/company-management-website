// Delete Document
async function deleteDocument(documentId) {
    const url = `/teams/document/${documentId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        queueToast('Document deleted', 'success');
        window.location.reload();
    }
}

// Upload Document
document.addEventListener('DOMContentLoaded', () => {
    uploadDocumentForm = document.getElementById('upload-document-form');
    if (uploadDocumentForm) {
        uploadDocumentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const employeeId = uploadDocumentForm.dataset.employeeId;
            const url = `/teams/document/create/${employeeId}/`;
            const formData = new FormData(e.target);

            const data = await sendRequest(url, 'POST', formData);
            if (data.success) {
                queueToast('Document uploaded', 'success');
                window.location.reload();
            }
        });
    }
});

// Edit Document
async function editDocument(documentId, formData) {
    const url = `/teams/document/${documentId}/edit/`;
    const data = await sendRequest(url, 'POST', formData);
    if (data.success) {
        queueToast('Document updated', 'success');
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
