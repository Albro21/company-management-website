// Weekly
let currentWeekStartDate = new Date();
currentWeekStartDate.setDate(currentWeekStartDate.getDate() - (currentWeekStartDate.getDay() === 0 ? 6 : currentWeekStartDate.getDay() - 1));

function formatDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function updateWeeklyDisplay(projectId, startDate) {
    const endDate = new Date(startDate);
    const displayElement = document.getElementById('weekly-date-display-' + projectId);
    const today = new Date();
    const currentWeekStart = new Date(today);
    currentWeekStart.setDate(today.getDate() - (today.getDay() === 0 ? 6 : today.getDay() - 1));
    const lastWeekStart = new Date(currentWeekStart);
    lastWeekStart.setDate(currentWeekStart.getDate() - 7);

    if (startDate.getDate() === currentWeekStart.getDate()) {
        displayElement.textContent = "This week";
    } else if (startDate.getDate() === lastWeekStart.getDate()) {
        displayElement.textContent = "Last week";
    } else {
        endDate.setDate(startDate.getDate() + 6);
        displayElement.textContent = `${formatDate(startDate)} - ${formatDate(endDate)}`;
    }
}

function previousWeek(projectId) {
    currentWeekStartDate.setDate(currentWeekStartDate.getDate() - 7);
    updateWeeklyDisplay(projectId, currentWeekStartDate);
    updateWeeklyUrl(projectId, currentWeekStartDate);
}

function nextWeek(projectId) {
    const today = new Date();
    const currentWeekStart = new Date(today);
    currentWeekStart.setDate(today.getDate() - (today.getDay() === 0 ? 6 : today.getDay() - 1));
    const nextStartDate = new Date(currentWeekStartDate);
    nextStartDate.setDate(currentWeekStartDate.getDate() + 7);

    if (nextStartDate > currentWeekStart) return;

    currentWeekStartDate.setDate(currentWeekStartDate.getDate() + 7);
    updateWeeklyDisplay(projectId, currentWeekStartDate);
    updateWeeklyUrl(projectId, currentWeekStartDate);
}

function updateWeeklyUrl(projectId, startDate) {
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 6);
    const link = document.getElementById(`generate-weekly-report-button-${projectId}`);
    const url = new URL(link.href);
    url.searchParams.set('start_date', formatDate(startDate));
    url.searchParams.set('end_date', formatDate(endDate));
    link.href = url.toString();
}

// Monthly
function getLastSundayOfMonth(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    const lastDay = new Date(year, month + 1, 0);
    while (lastDay.getDay() !== 0) {
        lastDay.setDate(lastDay.getDate() - 1);
    }
    return lastDay;
}

function getLastMondayOfMonth(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    const lastDay = new Date(year, month + 1, 0);
    while (lastDay.getDay() !== 1) {
        lastDay.setDate(lastDay.getDate() - 1);
    }
    return lastDay;
}

function getCurrentPeriodStart() {
    const now = new Date();
    const prevMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return getLastMondayOfMonth(prevMonthDate);
}

let currentPeriodStart = getCurrentPeriodStart();

document.addEventListener('DOMContentLoaded', () => {
    projectIds.forEach(projectId => {
        updateMonthlyDisplay(projectId, currentPeriodStart);
        updateMonthlyUrl(projectId, currentPeriodStart);
    });
});

function updateMonthlyDisplay(projectId, startDate) {
    const displayElement = document.getElementById('monthly-date-display-' + projectId);

    const endDate = getLastSundayOfMonth(new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1));

    const options = { month: 'long', year: 'numeric' };
    const formattedMonthYear = endDate.toLocaleDateString(undefined, options);

    displayElement.textContent = formattedMonthYear;
}

function previousMonth(projectId) {
    const prevMonthDate = new Date(currentPeriodStart.getFullYear(), currentPeriodStart.getMonth() - 1, 1);
    currentPeriodStart = getLastMondayOfMonth(prevMonthDate);

    updateMonthlyDisplay(projectId, currentPeriodStart);
    updateMonthlyUrl(projectId, currentPeriodStart);
}

function nextMonth(projectId) {
    const nextMonthDate = new Date(currentPeriodStart.getFullYear(), currentPeriodStart.getMonth() + 1, 1);
    const proposedStart = getLastMondayOfMonth(nextMonthDate);

    const now = new Date();
    if (proposedStart > now) {
        return;
    }

    currentPeriodStart = proposedStart;
    updateMonthlyDisplay(projectId, currentPeriodStart);
    updateMonthlyUrl(projectId, currentPeriodStart);
}

function updateMonthlyUrl(projectId, startDate) {
    const endDate = getLastSundayOfMonth(new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1));

    const pdfButton = document.getElementById(`generate-monthly-report-button-${projectId}-pdf`);
    const xlsxLink = document.getElementById(`generate-monthly-report-button-${projectId}-xlsx`);

    const pdfUrl = new URL(pdfButton.dataset.url, window.location.origin);
    const xlsxUrl = new URL(xlsxLink.href, window.location.origin);

    pdfUrl.searchParams.set('start_date', formatDate(startDate));
    pdfUrl.searchParams.set('end_date', formatDate(endDate));
    pdfButton.dataset.url = pdfUrl.toString();

    xlsxUrl.searchParams.set('start_date', formatDate(startDate));
    xlsxUrl.searchParams.set('end_date', formatDate(endDate));
    xlsxLink.href = xlsxUrl.toString();
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

async function downloadMonthlyReports(button) {
    const url = button.dataset.url;

    const data = await sendRequest(url, 'GET');

    if (data.success) {
        for (const link of data.links.slice().sort()) {
            const a = document.createElement('a');
            a.href = link;
            a.download = '';
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    } else {
        showToast(data.error || 'Something went wrong.', 'danger');
    }
}