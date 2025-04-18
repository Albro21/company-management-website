function acceptJoinRequest(requestId) {
    const requestElement = document.getElementById(`join-request-${requestId}`);

    const url = `/teams/join-request/${requestId}/accept/`;
    const method = "POST";

    sendRequest(url, method).then(data => {
        if (data && data.success) {
            requestElement.remove();
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    });
}

function declineJoinRequest(requestId) {
    const requestElement = document.getElementById(`join-request-${requestId}`);

    const url = `/teams/join-request/${requestId}/decline/`;
    const method = "POST";

    sendRequest(url, method).then(data => {
        if (data && data.success) {
            requestElement.remove();
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    });
}

async function deleteProject(projectId) {
    const url = `/project/${projectId}/delete/`;
    const method = 'DELETE';

    const success = await sendRequest(url, method);

    if (success) {
        document.getElementById(`project-${projectId}`).remove();
        Array.from(document.getElementsByClassName('tooltip')).forEach(function(tooltip) {tooltip.remove();});
    } else {
        console.error('Failed to delete project');
    }
}