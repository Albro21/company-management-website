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
