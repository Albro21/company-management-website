const checkboxes = document.querySelectorAll('.employee-checkbox');

function updateEmployeeHighlight(checkbox) {
    const employeeEl = checkbox.closest('.employee');
    if (!employeeEl) return;

    if (checkbox.checked) {
        employeeEl.classList.replace('bg-2', 'bg-3');
        employeeEl.style.color = 'orange';
    } else {
        employeeEl.classList.replace('bg-3', 'bg-2');
        employeeEl.style.color = '';
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

// Edit Holiday
function openHolidayEditOffcanvas(holidayId) {
    fetch(`/teams/holiday/${holidayId}/edit/`)
        .then(res => res.text())
        .then(html => {
            const body = document.getElementById("holiday-edit-body");
            body.innerHTML = html;

            const form = body.querySelector('#edit-holiday-form');
            const offcanvasEl = document.getElementById("holidayEditOffcanvas");
            const offcanvas = new bootstrap.Offcanvas(offcanvasEl);

            // Parse user IDs for the holiday
            const userIds = document.getElementById(`holiday-${holidayId}`)
                .dataset.userIds.trim().split(/\s+/) || [];

            // Auto-select employees now (instead of on show)
            userIds.forEach(id => {
                const checkbox = document.querySelector(`.employee[data-id="${id}"] input[type="checkbox"]`);
                if (checkbox) {
                    checkbox.checked = true;
                    checkbox.dataset.autoChecked = "true";
                    updateEmployeeHighlight(checkbox);
                }
            });

            // Clean-up on offcanvas close
            const onHidden = () => {
                userIds.forEach(id => {
                    const checkbox = document.querySelector(`.employee[data-id="${id}"] input[type="checkbox"]`);
                    if (checkbox && checkbox.dataset.autoChecked === "true") {
                        checkbox.checked = false;
                        delete checkbox.dataset.autoChecked;
                        updateEmployeeHighlight(checkbox);
                    }
                });
                offcanvasEl.removeEventListener('hidden.bs.offcanvas', onHidden);
            };
            offcanvasEl.addEventListener('hidden.bs.offcanvas', onHidden);

            // Set up form submit
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData(form);
                const formObj = Object.fromEntries(formData.entries());

                const employeeIds = Array.from(document.querySelectorAll('input[name="employees"]:checked'))
                    .map(cb => parseInt(cb.value, 10));

                if (employeeIds.length === 0) {
                    showToast('Please select at least one employee for a bank holiday.', 'danger');
                    return;
                }

                formObj.employees = employeeIds;

                const data = await sendRequest(`/teams/holiday/${holidayId}/edit/`, 'PATCH', JSON.stringify(formObj));

                if (data.success) {
                    queueToast('Holiday updated', 'success');
                    window.location.reload();
                } else {
                    showToast(data.error || 'An error occurred.', 'danger');
                }
            });

            window.scrollTo({ top: 0, behavior: 'smooth' });
            offcanvas.show();
        });
}

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
