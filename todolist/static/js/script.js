async function logoutUser() {
	await sendRequest("/logout/", "POST");
}

async function completeTask(button) {
	const taskId = button.getAttribute('data-task-id');
	const url = `/task/${taskId}/complete/`;
	const method = 'POST';

	const success = await sendRequest(url, method);

	if (success) {
		const sound = document.getElementById("completion-sound");
		sound.currentTime = 0;
		await sound.play();

		document.getElementById(`task-${taskId}`).remove();

		hideEmptyTaskGroups();
	} else {
		console.error('Failed to complete task');
	}
}

function updateTask(button) {
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

    requestBody = JSON.stringify(requestBody);

    sendRequest(`/task/${taskId}/edit/`, "POST", requestBody).then(data => {
        if (data && data.success) {
            location.reload();
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    });
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
