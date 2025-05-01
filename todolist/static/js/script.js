async function logoutUser() {
	await sendRequest("/logout/", "POST");
}