async function acceptHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/accept/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        document.getElementById(`holiday-${holidayId}`).remove();
        showToast('Holiday request accepted', 'success');
    }
}

async function declineHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/decline/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        element = document.getElementById(`holiday-${holidayId}`);
        element.remove();
        showToast('Holiday request declined', 'success');
    }
}

async function acceptEditHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/accept-edit/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        document.getElementById(`holiday-${holidayId}`).remove();
        showToast('Holiday edit request accepted', 'success');
    }
}

async function declineEditHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/decline-edit/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        element = document.getElementById(`holiday-${holidayId}`);
        element.remove();
        showToast('Holiday edit request declined', 'success');
    }
}

async function acceptDeleteHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/accept-delete/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        document.getElementById(`holiday-${holidayId}`).remove();
        showToast('Holiday delete request accepted', 'success');
    }
}

async function declineDeleteHolidayRequest(holidayId) {
    const url = `/teams/holiday/${holidayId}/decline-delete/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        element = document.getElementById(`holiday-${holidayId}`);
        element.remove();
        showToast('Holiday delete request declined', 'success');
    }
}