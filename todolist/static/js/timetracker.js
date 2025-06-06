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

document.querySelector('#tracker-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    if (!window.runningTimer) {
        const name = nameInput.value;
        const projectId = projectSelect.value;

        const url = `/timetracker/start/`;
        const requestBody = JSON.stringify({ name: name, project_id: projectId });

        const data = await sendRequest(url, "POST", requestBody);

        if (data.success) {
            startTimer();
            timerButton.textContent = "Stop";
            timerButton.style.backgroundColor = "#ff0000";
            nameInput.disabled = true;
            projectSelect.disabled = true;
            window.runningTimer = true
            showToast('Timer started', 'success');
        }
    } else {
        const url = `/timetracker/stop/`;
        const data = await sendRequest(url, "POST");
        if (data.success) {
            queueToast('Timer stopped', 'success');
            window.location.reload();
        }
    }
});

window.onload = function () {
    if (window.runningTimer) {
        const elapsed = calculateElapsedTime(window.runningTimer.startTime);
        startTimer(elapsed);

        timerButton.textContent = "Stop";
        timerButton.style.backgroundColor = "#ff0000";

        nameInput.value = window.runningTimer.name;
        projectSelect.value = window.runningTimer.projectId;

        nameInput.disabled = true;
        projectSelect.disabled = true;
    }
};
