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
// --- ISO Week Helpers ---
function getISOWeekStart(date) {
    const day = date.getDay(); // 0 = Sun, 1 = Mon, ..., 6 = Sat
    const diff = (day === 0 ? -6 : 1) - day;
    const monday = new Date(date);
    monday.setDate(date.getDate() + diff);
    monday.setHours(0, 0, 0, 0);
    return monday;
}

function getISOWeekEnd(date) {
    const monday = getISOWeekStart(date);
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    sunday.setHours(23, 59, 59, 999);
    return sunday;
}

function getFirstISOWeekStartOfMonth(date) {
    const firstOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
    return getISOWeekStart(firstOfMonth);
}

function getLastISOWeekEndOfMonth(date) {
    const lastOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
    return getISOWeekEnd(lastOfMonth);
}

function getCurrentPeriodStart() {
    const now = new Date();
    const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    return getFirstISOWeekStartOfMonth(prevMonth);
}

let currentPeriodStart = getCurrentPeriodStart();

// --- Main DOM Ready Logic ---
document.addEventListener('DOMContentLoaded', () => {
    projectIds.forEach(projectId => {
        updateMonthlyDisplay(projectId, currentPeriodStart);
        updateMonthlyUrl(projectId, currentPeriodStart);
    });
});

// --- Display Logic ---
function updateMonthlyDisplay(projectId, startDate) {
    const displayElement = document.getElementById('monthly-date-display-' + projectId);
    const endDate = getLastISOWeekEndOfMonth(new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1));

    const options = { month: 'long', year: 'numeric' };
    const formattedMonthYear = endDate.toLocaleDateString(undefined, options);

    displayElement.textContent = formattedMonthYear;
}

// --- Navigation ---
function previousMonth(projectId) {
    const prevMonth = new Date(currentPeriodStart.getFullYear(), currentPeriodStart.getMonth() - 1, 1);
    currentPeriodStart = getFirstISOWeekStartOfMonth(prevMonth);

    updateMonthlyDisplay(projectId, currentPeriodStart);
    updateMonthlyUrl(projectId, currentPeriodStart);
}

function nextMonth(projectId) {
    const nextMonth = new Date(currentPeriodStart.getFullYear(), currentPeriodStart.getMonth() + 1, 1);
    const proposedStart = getFirstISOWeekStartOfMonth(nextMonth);

    const now = new Date();
    if (proposedStart > now) return;

    currentPeriodStart = proposedStart;
    updateMonthlyDisplay(projectId, currentPeriodStart);
    updateMonthlyUrl(projectId, currentPeriodStart);
}

// --- Update Download URLs ---
function updateMonthlyUrl(projectId, startDate) {
    const endDate = getLastISOWeekEndOfMonth(new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1));

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

// --- Formatting Helper ---
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

// --- Async Report Downloader ---
async function downloadMonthlyReports(button) {
    const url = button.dataset.url;
    const data = await sendRequest(url, 'GET');

    if (data.success) {
        for (const link of data.links) {
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

