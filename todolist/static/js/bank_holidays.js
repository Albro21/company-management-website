const checkboxes = document.querySelectorAll('.employee-checkbox');

function updateEmployeeHighlight(checkbox) {
    const employeeEl = checkbox.closest('.employee');
    if (!employeeEl) return;

    if (checkbox.checked) {
        employeeEl.classList.replace('bg-2', 'bg-3');
    } else {
        employeeEl.classList.replace('bg-3', 'bg-2');
    }
}

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function () {
        updateEmployeeHighlight(this);
    });
});

document.getElementById('select-all-employees').addEventListener('change', function () {
    checkboxes.forEach(cb => {
        cb.checked = this.checked;
        updateEmployeeHighlight(cb);
    });
});

document.querySelectorAll('.holiday').forEach(holidayEl => {
    const userIds = holidayEl.dataset.userIds.trim().split(/\s+/);
    const offcanvasId = holidayEl.dataset.bsTarget || holidayEl.getAttribute('data-bs-target');
    const offcanvasEl = document.querySelector(offcanvasId);

    if (!offcanvasEl) return;

    offcanvasEl.addEventListener('show.bs.offcanvas', () => {
        userIds.forEach(id => {
            const userCheckbox = document.querySelector(`.employee[data-id="${id}"] input[type="checkbox"]`);
            if (userCheckbox) {
                userCheckbox.checked = true;
                userCheckbox.dataset.autoChecked = "true";
                updateEmployeeHighlight(userCheckbox);
            }
        });
    });

    offcanvasEl.addEventListener('hidden.bs.offcanvas', () => {
        userIds.forEach(id => {
            const userCheckbox = document.querySelector(`.employee[data-id="${id}"] input[type="checkbox"]`);
            if (userCheckbox && userCheckbox.dataset.autoChecked === "true") {
                userCheckbox.checked = false;
                delete userCheckbox.dataset.autoChecked;
                updateEmployeeHighlight(userCheckbox);
            }
        });
    });
});

// Create Holiday
const createHolidayForm = document.getElementById('create-holiday-form');
if (createHolidayForm) {
    createHolidayForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = '/teams/holiday/create/';
        const formData = new FormData(e.target);
        const formObj = Object.fromEntries(formData.entries());

        // Parse employee checkboxes
        const employeeIds = Array.from(document.querySelectorAll('input[name="employees"]:checked'))
            .map(cb => parseInt(cb.value, 10));

        // If no employees selected, block submission
        if (employeeIds.length === 0) {
            showToast('Please select at least one employee for a bank holiday.', 'danger');
            return;
        }

        formObj.type = 'bank_holiday';
        formObj.employees = employeeIds;

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

// Select all forms with class 'edit-holiday-form'
const editHolidayForms = document.querySelectorAll('.edit-holiday-form');
editHolidayForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const holidayId = form.dataset.id;
        const url = `/teams/holiday/${holidayId}/edit/`;
        const formData = new FormData(form);
        const formObj = Object.fromEntries(formData.entries());

        // Parse employee checkboxes
        const employeeIds = Array.from(document.querySelectorAll('input[name="employees"]:checked'))
            .map(cb => parseInt(cb.value, 10));

        // If no employees selected, block submission
        if (employeeIds.length === 0) {
            showToast('Please select at least one employee for a bank holiday.', 'danger');
            return;
        }

        formObj.type = 'bank_holiday';
        formObj.employees = employeeIds;

        const requestBody = JSON.stringify(formObj);

        const data = await sendRequest(url, 'PATCH', requestBody);

        if (data.success) {
            queueToast('Holiday updated', 'success');
            window.location.reload();
        } else if (data.error) {
            showToast(data.error, 'danger');
        }
    });
});

// Delete Holiday
async function deleteHoliday(holidayId) {
    const url = `/teams/holiday/${holidayId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        queueToast('Holiday deleted', 'success');
        window.location.reload();
    } else {
        showToast(data.error, 'danger');
    }
}
