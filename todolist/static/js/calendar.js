function createTooltip(info) {
    const tooltip = new bootstrap.Tooltip(info.el, {
        title: `
        <div class="d-flex flex-column">
            <h5 class="text-center border-bottom py-1">${info.event.extendedProps.type}</h5>
            <div class="row p-2">
                <div class="col-4 d-flex flex-column text-start">
                    Employees:<br>
                    Reason:<br>
                    Period:
                </div>
                <div class="col-8 d-flex flex-column text-start justify-content-start">
                    ${info.event.extendedProps.users}<br>
                    ${info.event.extendedProps.reason}<br>
                    ${info.event.extendedProps.start_date} – ${info.event.extendedProps.end_date} (${info.event.extendedProps.days} days)
                </div>
            </div>
        </div>`,
        html: true,
        placement: 'top',
        trigger: 'hover',
        container: 'body'
    });
}

document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        firstDay: 1,
        initialView: 'dayGridMonth',
        dayHeaderFormat: { weekday: 'long' },
        events: allHolidaysJson,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'todayLabel holidayLabel bankHolidayLabel sickDayLabel'
        },
        customButtons: {
            todayLabel: {
                text: 'Today',
                click: null
            },
            holidayLabel: {
                text: 'Holiday',
                click: null
            },
            bankHolidayLabel: {
                text: 'Bank Holiday',
                click: null
            },
            sickDayLabel: {
                text: 'Sick Day',
                click: null
            }
        },
        eventDidMount: function (info) {
            createTooltip(info);
        }
    });
    calendar.render();

    function parseDate(dateStr) {
        const parts = dateStr.split('-');
        return new Date(parts[0], parts[1] - 1, parts[2]);
    }

    function convertToDataSource(dates, color) {
        return dates.map(dateStr => ({
            startDate: parseDate(dateStr),
            endDate: parseDate(dateStr),
            color: color
        }));
    }

    const holidayList = convertToDataSource(holidays, '#99d1ff');
    const bankHolidayList = convertToDataSource(bankHolidays, '#9999ff');
    const sickDayList = convertToDataSource(sickDays, '#ffdd99');

    const dataSource = [...holidayList, ...bankHolidayList, ...sickDayList];

    // Full Calendar
    const fullCalendar = new Calendar('#full-calendar', {
        style: 'background',
        weekStart: 1,
        dataSource: dataSource,
    });

    function goToMonth(event) {
        const monthContainer = event.target.closest('.month-container');
        if (monthContainer) {
            const year = new Date().getFullYear();
            const index = monthContainer.dataset.monthId;
            const dateStr = `${year}-${String(Number(index) + 1).padStart(2, '0')}-01`;
            calendar.gotoDate(dateStr);
        }
    }

    document.querySelector('#full-calendar .months-container').addEventListener('click', (event) => {
        goToMonth(event);
    });

    document.querySelectorAll('.day, .day-content').forEach(el => {
        el.addEventListener('click', (event) => {
            goToMonth(event);
        });
    });
});

document.getElementById('holiday-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const errorElement = document.getElementById('holiday-errors');

    const url = '/teams/holiday/create/';
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));

    const data = await sendRequest(url, 'POST', requestBody);

    if (data.success) {
        queueToast('Holiday created', 'success');
        window.location.reload();
    } else if (data.error) {
        errorElement.textContent = data.error;
        showToast(data.error, 'danger');
    }
});

// Edit Holiday
const editHolidayForms = document.querySelectorAll('.edit-holiday-form');
editHolidayForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const holidayId = form.dataset.id;
        const url = `/teams/holiday/${holidayId}/request-edit/`;

        const formData = new FormData(form);
        const formObj = Object.fromEntries(formData.entries());
        const requestBody = JSON.stringify(formObj);

        const data = await sendRequest(url, 'PATCH', requestBody);

        if (data.success) {
            queueToast('Requested holiday edit', 'success');
            window.location.reload();
        } else if (data.error) {
            showToast(data.error, 'danger');
        }
    });
});

// Delete Holiday
async function deleteHoliday(holidayId) {
    const url = `/teams/holiday/${holidayId}/request-delete/`;
    const data = await sendRequest(url, 'PATCH');
    if (data.success) {
        queueToast('Requested holiday deletion', 'success');
        window.location.reload();
    } else {
        showToast(data.error, 'danger');
    }
}

