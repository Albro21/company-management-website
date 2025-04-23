async function deleteRole(roleId) {
    const url = `/teams/role/${roleId}/delete/`;
    const success = await sendRequest(url, "DELETE"); 
    if (success) {
        document.getElementById(`role-${roleId}`).remove();
    }
};