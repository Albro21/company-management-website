function deleteRole(roleId) {
    const roleElement = document.getElementById(`role-${roleId}`);

    const url = `/teams/role/${roleId}/delete/`;
    const method = "DELETE";

    sendRequest(url, method).then(data => {
        if (data && data.success) {
            roleElement.remove();
        } else {
            const errorMessage = data && data.error ? data.error : "No response from server";
            const statusCode = data ? data.status : 500;
            console.error(`${statusCode}: ${errorMessage}`);
        }
    });
}