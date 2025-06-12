document.getElementById('select-all-employees').addEventListener('change', function () {
    const checkboxes = document.querySelectorAll('.employee-checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
});

// Create Holiday
const createHolidayForm = document.getElementById('create-holiday-form');
if (createHolidayForm) {
    createHolidayForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = '/teams/holiday/create/';  // unified endpoint
        const formData = new FormData(e.target);

        // Create object from form data
        const formObj = Object.fromEntries(formData.entries());

        // Parse employee checkboxes
        const employeeIds = Array.from(document.querySelectorAll('input[name="employees"]:checked'))
            .map(cb => parseInt(cb.value, 10));

        // If employees are checked, it's a bank holiday
        if (employeeIds.length > 0) {
            formObj.type = 'bank_holiday';
            formObj.employees = employeeIds;
        } else {
            formObj.type = formObj.type || 'personal'; // fallback
        }

        const requestBody = JSON.stringify(formObj);

        const data = await sendRequest(url, 'POST', requestBody);

        if (data.success) {
            queueToast('Holiday created', 'success');
            window.location.reload();
        } else if (data.error) {
            showToast(data.error, 'danger');
        }
    });
}
