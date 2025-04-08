// Get DOM elements
const taskSelect = document.getElementById('task-select');
const nameInput = document.getElementById('name-input');
const projectSelect = document.getElementById('project-select');
const timerButton = document.getElementById('timer-button');
const timerDisplay = document.getElementById('timer');

// Function to format the time (seconds) as HH:MM:SS
// Converts seconds into a human-readable format
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    return `${padZero(hours)}:${padZero(minutes)}:${padZero(remainingSeconds)}`;
}

// Helper function to pad single digits with a leading zero
// Ensures that single-digit minutes/seconds are displayed as '01', '09', etc.
function padZero(num) {
    return num < 10 ? '0' + num : num;
}

// Function to start the timer
// Accepts elapsed time (in seconds) and updates the timer every second
function startTimer(elapsedTime = 0) {
    const updateTimer = () => {
        timerDisplay.textContent = formatTime(elapsedTime); // Display the formatted time
        elapsedTime++; // Increment the time every second
        localStorage.setItem('elapsedTime', elapsedTime); // Save the elapsed time in localStorage
    };

    if (elapsedTime === 0) {
        updateTimer();
    }

    setInterval(updateTimer, 1000); // Call the updateTimer function every 1000ms (1 second)
}

// Event listener for task selection change
taskSelect.addEventListener('change', function () {
    const selectedOption = this.options[this.selectedIndex];
    const taskId = this.value;

    if (taskId) {
        const taskTitle = selectedOption.dataset.title;
        const projectId = selectedOption.dataset.projectId;

        // If a task is selected, set the name and project inputs accordingly
        nameInput.value = taskTitle;
        nameInput.disabled = true; // Disable the name input to prevent changes

        projectSelect.value = projectId;
        projectSelect.disabled = true; // Disable the project input to prevent changes
    } else {
        // If no task is selected, reset the inputs
        nameInput.value = '';
        nameInput.disabled = false; // Enable the name input

        projectSelect.value = '';
        projectSelect.disabled = false; // Enable the project input
    }
});

// Event listener for form submission
document.querySelector('#tracker-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission

    // If the timer is not running, start it
    if (!localStorage.getItem('isTimerRunning')) {
        const taskId = taskSelect.value;
        const name = nameInput.value;
        const projectId = projectSelect.value;

        const url = `/timetracker/start/`; // URL for starting the timer
        const method = "POST";
        const requestBody = JSON.stringify({ task_id: taskId, name: name, project_id: projectId });

        sendRequest(url, method, requestBody).then(data => {
            if (data && data.success) {
                // If the request is successful, save the timer state and start the timer
                localStorage.setItem('isTimerRunning', 'true');
                localStorage.setItem('RunningTimerTaskId', taskId);
                localStorage.setItem('RunningTimerName', name);
                localStorage.setItem('RunningTimerProjectId', projectId);
                startTimer(); // Start the timer
                timerButton.textContent = "Stop"; // Change button text to "Stop"
                timerButton.style.backgroundColor = "#ff0000"; // Change button color to red
                taskSelect.disabled = true; // Disable task select
                nameInput.disabled = true; // Disable name input
                projectSelect.disabled = true; // Disable project select
            } else {
                console.error("Server error:", data ? data.error : "No response");
            }
        });
    } else {
        // If the timer is already running, stop it
        const url = `/timetracker/stop/`; // URL for stopping the timer
        const method = "POST";

        sendRequest(url, method).then(data => {
            if (data && data.success) {
                // If the request is successful, clear the stored state and reload the page
                localStorage.clear();
                window.location.reload(); // Reload the page to reset everything
            } else {
                console.error("Server error:", data ? data.error : "No response");
            }
        });
    }
});

// Window onload function
window.onload = function () {
    // Check if the timer is currently running from localStorage
    const isTimerRunning = localStorage.getItem('isTimerRunning') === 'true';
    const elapsedTime = parseInt(localStorage.getItem('elapsedTime')) || 0; // Get the elapsed time (or 0 if not available)

    // If the timer is running, continue the timer from the saved elapsed time
    if (isTimerRunning) {
        startTimer(elapsedTime); // Start the timer from the saved time
        timerButton.textContent = "Stop"; // Change button text to "Stop"
        timerButton.style.backgroundColor = "#ff0000"; // Change button color to red

        // Get saved task details from localStorage
        const runningTimerTaskId = localStorage.getItem('RunningTimerTaskId');
        const runningTimerName = localStorage.getItem('RunningTimerName');
        const runningTimerProjectId = localStorage.getItem('RunningTimerProjectId');

        // Set the form inputs to the saved values
        taskSelect.value = runningTimerTaskId;
        nameInput.value = runningTimerName;
        projectSelect.value = runningTimerProjectId;

        // Disable the inputs since the timer is running
        taskSelect.disabled = true;
        nameInput.disabled = true;
        projectSelect.disabled = true;
    }
};
