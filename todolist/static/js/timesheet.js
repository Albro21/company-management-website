// Week change handling
function getStartOfWeek(date) {
    const newDate = new Date(date);
    newDate.setDate(date.getDate() - (date.getDay() === 0 ? 6 : date.getDay() - 1));
    return newDate;
}

function getStartDateFromURL() {
    const params = new URLSearchParams(window.location.search);
    const startDateStr = params.get('start_date');

    if (!startDateStr) {
        return getStartOfWeek(new Date());
    }

    const date = new Date(startDateStr);
    return (!isNaN(date) ? date : getStartOfWeek(new Date()));
}

let currentWeekStartDate = getStartDateFromURL();

function previousWeek() {
    currentWeekStartDate.setDate(currentWeekStartDate.getDate() - 7);
    applyWeek(currentWeekStartDate);
}

function nextWeek() {
    currentWeekStartDate.setDate(currentWeekStartDate.getDate() + 7);
    applyWeek(currentWeekStartDate);
}

function applyWeek(startDate) {
    const url = new URL(window.location.href);
    url.searchParams.set('start_date', startDate.toISOString().split('T')[0]);
    window.location.href = url.toString();
}

// Calculate and display totals
async function updateTimeEntryTimes(timeEntryId, startTime, endTime) {
    const url = `/timetracker/time-entry/${timeEntryId}/update-times/`;
    const requestBody = JSON.stringify({ start_time: startTime, end_time: endTime });
    const data = await sendRequest(url, 'PATCH', requestBody);
}

document.addEventListener("DOMContentLoaded", () => {

    function parseTime(timeStr) {
        if (!timeStr) return 0;
        const [h, m] = timeStr.split(':').map(Number);
        if (isNaN(h) || isNaN(m)) return 0;
        return h * 60 + m;
    }

    function formatDuration(minutes) {
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }

    // Convert date string (e.g. '2025-05-20') to Monday=0 ... Sunday=6
    function getMondayBasedDayIndex(dateString) {
        const date = new Date(dateString);
        const jsDay = date.getDay(); // Sunday=0 ... Saturday=6
        return jsDay === 0 ? 6 : jsDay - 1;
    }

    function calculateDurations(changedInput = null) {
        const dateTotals = {};
        const projectTotals = {};
        const projectDayTotals = {};

        document.querySelectorAll('.entry-duration').forEach(cell => {
            const entryId = cell.dataset.entryId;
            const startInput = document.querySelector(`#start-time-${entryId}`);
            const endInput = document.querySelector(`#end-time-${entryId}`);
            const totalTimeElement = document.getElementById(`total-time-${entryId}`);

            const start = parseTime(startInput?.value);
            const end = parseTime(endInput?.value);
            let duration = 0;

            // Reset invalid classes first
            startInput.classList.remove('invalid');
            endInput.classList.remove('invalid');
            totalTimeElement.classList.remove('invalid');

            if (start > 0 && end > 0) {
                if (end > start) {
                    duration = end - start;
                    if (changedInput === startInput || changedInput === endInput) {
                        updateTimeEntryTimes(entryId, startInput?.value, endInput?.value);
                    }
                } else {
                    startInput.classList.add('invalid');
                    endInput.classList.add('invalid');
                    totalTimeElement.classList.add('invalid');
                }
            }

            cell.textContent = formatDuration(duration);

            const projectId = cell.dataset.projectId || startInput.dataset.projectId;
            const dateId = cell.dataset.date || startInput.dataset.date;
            if (!projectId || !dateId) return;

            const dateKey = `${projectId}_${dateId}`;
            dateTotals[dateKey] = (dateTotals[dateKey] || 0) + duration;
            projectTotals[projectId] = (projectTotals[projectId] || 0) + duration;

            const dayIndex = getMondayBasedDayIndex(dateId);
            if (!projectDayTotals[projectId]) projectDayTotals[projectId] = {};
            projectDayTotals[projectId][dayIndex] = (projectDayTotals[projectId][dayIndex] || 0) + duration;
        });

        // Update date totals UI
        document.querySelectorAll('.date-total').forEach(cell => {
            const projectId = cell.dataset.projectId;
            const dateId = cell.dataset.date;
            const key = `${projectId}_${dateId}`;
            cell.textContent = formatDuration(dateTotals[key] || 0);
        });

        // Update project totals UI
        document.querySelectorAll('.project-total').forEach(cell => {
            const projectId = cell.dataset.projectId;
            cell.textContent = formatDuration(projectTotals[projectId] || 0);
        });

        const totalMinutes = Object.values(projectTotals).reduce((acc, val) => acc + val, 0);
        document.getElementById('total-week').textContent = formatDuration(totalMinutes);

        // Update day columns in each project row
        Object.entries(projectDayTotals).forEach(([projectId, dayTotals]) => {
            const projectRow = document.querySelector(`.project-row[data-project-id="${projectId}"]`);
            if (!projectRow) return;

            for (let i = 0; i < 7; i++) {
                const dayCol = projectRow.querySelector(`.col.text-center[data-day="${i}"]`);
                if (dayCol) {
                    dayCol.textContent = formatDuration(dayTotals[i] || 0);
                    if (!dayTotals[i]) {
                        dayCol.classList.add('text-muted');
                    }
                }
            }
        });
    }

    calculateDurations();

    document.querySelectorAll('input.time-input').forEach(input => {
        input.addEventListener('change', () => calculateDurations(input));
    });

});
