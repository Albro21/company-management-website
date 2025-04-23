const taskSelect = document.getElementById('task-select');
const nameInput = document.getElementById('name-input');
const projectSelect = document.getElementById('project-select');
const timerButton = document.getElementById('timer-button');
const timerDisplay = document.getElementById('timer');

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${padZero(hours)}:${padZero(minutes)}:${padZero(remainingSeconds)}`;
}

function calculateElapsedTime(startTime) {
    const start = new Date(startTime);
    const now = new Date();
    return Math.floor((now - start) / 1000);
}

function padZero(num) {
    return num < 10 ? '0' + num : num;
}

function startTimer(elapsedTime = 0) {
    const updateTimer = () => {
        timerDisplay.textContent = formatTime(elapsedTime);
        elapsedTime++;
    };

    if (elapsedTime === 0) {
        updateTimer();
    }

    setInterval(updateTimer, 1000);
}

taskSelect.addEventListener('change', function () {
    const selectedOption = this.options[this.selectedIndex];
    const taskId = this.value;

    if (taskId) {
        const taskTitle = selectedOption.dataset.title;
        const projectId = selectedOption.dataset.projectId;

        nameInput.value = taskTitle;
        nameInput.disabled = true;

        projectSelect.value = projectId;
        projectSelect.disabled = true;
    } else {
        nameInput.value = '';
        nameInput.disabled = false;

        projectSelect.value = '';
        projectSelect.disabled = false;
    }
});

document.querySelector('#tracker-form').addEventListener('submit', function (event) {
    event.preventDefault();

    if (!window.runningTimer) {
        const taskId = taskSelect.value;
        const name = nameInput.value;
        const projectId = projectSelect.value;

        const url = `/timetracker/start/`;
        const method = "POST";
        const requestBody = JSON.stringify({ task_id: taskId, name: name, project_id: projectId });

        sendRequest(url, method, requestBody).then(data => {
            if (data && data.success) {
                startTimer();
                timerButton.textContent = "Stop";
                timerButton.style.backgroundColor = "#ff0000";
                taskSelect.disabled = true;
                nameInput.disabled = true;
                projectSelect.disabled = true;

                window.runningTimer = true
            } else {
                console.error("Server error:", data ? data.error : "No response");
            }
        });
    } else {
        const url = `/timetracker/stop/`;
        const method = "POST";

        sendRequest(url, method).then(data => {
            if (data && data.success) {
                window.location.reload();
            } else {
                console.error("Server error:", data ? data.error : "No response");
            }
        });
    }
});

window.onload = function () {
    if (window.runningTimer) {
        const elapsed = calculateElapsedTime(window.runningTimer.startTime);
        startTimer(elapsed);

        timerButton.textContent = "Stop";
        timerButton.style.backgroundColor = "#ff0000";

        taskSelect.value = window.runningTimer.taskId;
        nameInput.value = window.runningTimer.name;
        projectSelect.value = window.runningTimer.projectId;

        taskSelect.disabled = true;
        nameInput.disabled = true;
        projectSelect.disabled = true;
    }
};

async function deleteTimeEntry(timeEntryId) {
    const url = `/timetracker/time-entry/${timeEntryId}/delete/`;
    const method = 'DELETE';

    const success = await sendRequest(url, method);

    if (success) {
        const timeEntry = document.getElementById(`time-entry-${timeEntryId}`);
        
        timeEntry.remove();
        document.getElementById(timeEntry.dataset.offcanvas).remove();
        
        const collapse = document.getElementById(timeEntry.dataset.timeEntryParent);
        if (collapse.children.length === 0) {
            collapse.remove();
            
            const grouper = document.getElementById(timeEntry.dataset.timeEntryGrouper);
            const grouperParent = grouper.parentElement;
            
            grouper.remove();

            if (grouperParent.children.length === 1) {
                grouperParent.remove();
            }
        }
    } else {
        console.error('Failed to delete project');
    }
}

document.addEventListener("DOMContentLoaded", function () {
	document.querySelectorAll(".time-entry-form").forEach(form => {
		const id = form.getAttribute("data-time-entry-id");
		const taskSelect = form.querySelector(`#task-${id}`);
		const nameInput = form.querySelector(`#name-${id}`);
		const projectSelect = form.querySelector(`#project-${id}`);

		function toggleInputs() {
			const selectedOption = taskSelect.options[taskSelect.selectedIndex];

			if (taskSelect.value) {
				nameInput.disabled = true;
				projectSelect.disabled = true;

				const taskName = selectedOption.getAttribute("data-task-name");
				const taskProjectId = selectedOption.getAttribute("data-task-project-id");

				if (taskName !== null) nameInput.value = taskName;
				if (taskProjectId !== null) {
					projectSelect.value = taskProjectId;
				}
			} else {
				nameInput.disabled = false;
				projectSelect.disabled = false;
			}
		}

		toggleInputs();

		taskSelect.addEventListener("change", toggleInputs);
	});
});

async function duplicateTimeEntry(timeEntryId) {
    const url = `/timetracker/time-entry/${timeEntryId}/duplicate/`;
    await sendRequest(url, 'POST');
    window.location.reload();
};