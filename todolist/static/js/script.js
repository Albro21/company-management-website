async function logoutUser() {
	await sendRequest("/logout/", "POST");
}

async function completeTask(button) {
	const taskId = button.getAttribute('data-task-id');
	const url = `/${taskId}/complete/`;
	const method = 'POST';

	const success = await sendRequest(url, method);

	if (success) {
		const sound = document.getElementById("completion-sound");
		sound.currentTime = 0;

		try {
			await sound.play();

			const taskElement = document.getElementById(`task-${taskId}`);
			const parentElement = taskElement.parentElement;
			const childElements = parentElement.children;
			
			if (childElements.length === 2) {
				parentElement.remove(); // Removes both task group date and tasks 
			} else {
				taskElement.remove(); // Removes only task
			}
		} catch (error) {
			console.error("Error playing sound:", error);
		}
	} else {
		console.error('Failed to complete task');
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
