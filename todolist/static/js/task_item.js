async function completeTask(taskId) {
	const url = `/task/${taskId}/complete/`;
	const success = await sendRequest(url, 'POST');

	if (success) {
		const sound = document.getElementById("completion-sound");
		sound.currentTime = 0;
		await sound.play();

		const taskElement = document.getElementById(`task-${taskId}`);
		const taskEditingOffcanvas = document.getElementById(`edit-task-${taskId}`);
		const taskElementParent = taskElement.parentElement;
		taskElement.remove();
		taskEditingOffcanvas.remove();
		if (taskElementParent.children.length === 1) {
			taskElementParent.remove();
		}
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
