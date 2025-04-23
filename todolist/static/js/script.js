async function logoutUser() {
	await sendRequest("/logout/", "POST");
}

async function completeTask(taskId) {
	const url = `/task/${taskId}/complete/`;
	const success = await sendRequest(url, 'POST');

	if (success) {
		const sound = document.getElementById("completion-sound");
		sound.currentTime = 0;
		await sound.play();

		document.getElementById(`task-${taskId}`).remove();

		hideEmptyTaskGroups();
	}
}

async function updateTask(button) {
    event.preventDefault();

    const form = button.closest("form");
    const formData = new FormData(form);
    const taskId = button.getAttribute('data-task-id');

    let requestBody = {};  

    // Convert FormData to an object, handling multiple values for "categories"
    formData.forEach((value, key) => {
        if (key === "categories") {
            if (!requestBody[key]) {
                requestBody[key] = [];  // Ensure it's an array
            }
            requestBody[key].push(value);  // Add each category value
        } else {
            requestBody[key] = value;
        }
    });

	const url = `/task/${taskId}/edit/`;
    requestBody = JSON.stringify(requestBody);

	const success = await sendRequest(url, "POST", requestBody);

	if (success) {
		location.reload();
	}
}

// Change checkmark icon on hover
document.addEventListener("DOMContentLoaded", function () {
	document.querySelectorAll(".checkmark").forEach(icon => {
		icon.addEventListener("mouseenter", function () {
			if (this.classList.contains("bi-circle")) {
				this.classList.replace("bi-circle", "bi-check-circle");
			}
		});
		icon.addEventListener("mouseleave", function () {
			if (this.classList.contains("bi-check-circle")) {
				this.classList.replace("bi-check-circle", "bi-circle");
			}
		});
	});
});
