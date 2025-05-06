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
let currentMonthDate = new Date();

function updateMonthlyDisplay(projectId, date) {
    const displayElement = document.getElementById('monthly-date-display-' + projectId);
    const now = new Date();
    const thisMonth = now.getMonth();
    const thisYear = now.getFullYear();
    const targetMonth = date.getMonth();
    const targetYear = date.getFullYear();

    if (targetMonth === thisMonth && targetYear === thisYear) {
        displayElement.textContent = "This month";
    } else {
        displayElement.textContent = date.toLocaleString('default', { month: 'long', year: 'numeric' });
    }
}

function previousMonth(projectId) {
    currentMonthDate.setMonth(currentMonthDate.getMonth() - 1);
    updateMonthlyDisplay(projectId, currentMonthDate);
    updateMonthlyUrl(projectId, currentMonthDate);
}

function nextMonth(projectId) {
    const now = new Date();
    const temp = new Date(currentMonthDate);
    temp.setMonth(temp.getMonth() + 1);
    if (temp > now) return;
    currentMonthDate.setMonth(currentMonthDate.getMonth() + 1);
    updateMonthlyDisplay(projectId, currentMonthDate);
    updateMonthlyUrl(projectId, currentMonthDate);
}

function updateMonthlyUrl(projectId, date) {
    const start = new Date(date.getFullYear(), date.getMonth(), 1);
    const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);

    const link = document.getElementById(`generate-monthly-report-button-${projectId}`);
    const url = new URL(link.href);
    url.searchParams.set('start_date', formatDate(start));
    url.searchParams.set('end_date', formatDate(end));
    link.href = url.toString();
}
