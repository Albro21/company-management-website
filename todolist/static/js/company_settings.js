// Delete Job Title
async function deleteJobTitle(jobTitleId) {
    const url = `/teams/job-title/${jobTitleId}/delete/`;
    const data = await sendRequest(url, "DELETE"); 
    if (data.success) {
        queueToast('Job title deleted', 'success');
        document.getElementById(`job-title-${jobTitleId}`).remove();
    }
};

// Create Job Title
const createJobTitleForm = document.getElementById('create-job-title-form');
if (createJobTitleForm) {
    createJobTitleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
    
        const url = '/teams/job-title/create/';
        const formData = new FormData(e.target);
        formData.delete('csrfmiddlewaretoken');
        const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    
        const data = await sendRequest(url, 'POST', requestBody);
        if (data.success) {
            queueToast('Job title created', 'success');
            window.location.reload();
        }
    });
}
