function createTooltip (info) {
    const tooltip = new bootstrap.Tooltip(info.el, {
        title: `
        <div class="d-flex flex-column">
            <h5 class="text-center border-bottom py-1">${info.event.extendedProps.type}</h5>
            <div class="row p-2">
                <div class="col-3 d-flex flex-column text-start">
                    Employee:<br>
                    Period:<br>
                    Reason:
                </div>
                <div class="col-9 d-flex flex-column text-start justify-content-start">
                    ${info.event.extendedProps.employee}<br>
                    ${info.event.extendedProps.start_date} – ${info.event.extendedProps.end_date} (${info.event.extendedProps.days} days)<br>
                    <p class="m-0">
                        ${info.event.extendedProps.reason}
                    </p>
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
        events: eventsJson,
        eventDidMount: function(info) {
            createTooltip(info);
        }
    });
    calendar.render();
});