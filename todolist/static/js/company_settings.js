async function deleteJobTitle(jobTitleId) {
    const url = `/teams/job-title/${jobTitleId}/delete/`;
    const success = await sendRequest(url, "DELETE"); 
    if (success) {
        document.getElementById(`job-title-${jobTitleId}`).remove();
    }
};