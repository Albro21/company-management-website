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
			document.getElementById(`task-${taskId}`).remove();
		} catch (error) {
			console.error("Error playing sound:", error);
		}
	} else {
		console.error('Failed to complete task');
	}
}

// Date calculator (days left/overdue)
function daysBetween(startDate, endDate) {
	if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
		throw new Error('Применяйте корректные объекты Date.');
	}

	const diffTime = (Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()) - Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()));
	const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

	return diffDays;
};

const startDate = new Date(); // today user's date
const endDate = document.querySelectorAll('div.endDateLabel');

endDate.forEach((item) => {
	if (daysBetween(startDate, new Date('20' + item.textContent)) == 1) {
		item.textContent = 'Do it today'
	} else if (daysBetween(startDate, new Date('20' + item.textContent)) > 0) {
		item.textContent = daysBetween(startDate, new Date('20' + item.textContent)) + ' days left';
	} else if (daysBetween(startDate, new Date('20' + item.textContent)) <= 0 && daysBetween(startDate, new Date('20' + item.textContent)) >= -1) {
		item.textContent = 'overdue yesterday';
		item.style.textDecorationLine = 'line-through';
	} else {
		item.textContent = 'overdue ' + -daysBetween(startDate, new Date('20' + item.textContent)) + ' days';
		item.style.textDecorationLine = 'line-through';
	}

})

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
