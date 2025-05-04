const totalTimeElement = document.getElementById("total_time");

document.addEventListener("DOMContentLoaded", function () {
    const stackedBarCanvas = document.getElementById("companyStackedBarChart");
    const stackedBarCTX = stackedBarCanvas.getContext("2d");

    const donutCanvas = document.getElementById("companyDonutChart");
    const donutCTX = donutCanvas.getContext("2d");

    Chart.register(ChartDataLabels);

    let StackedBarChart = new Chart(stackedBarCTX, {
        type: "bar",
        data: {
            labels: [],
            datasets: [{
                label: "Completed Tasks",
                data: [],
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1
            }]
        },
        options: {
            plugins: [ChartDataLabels],
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: "white"
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const value = context.parsed.y;
                            const totalSeconds = Math.round(value * 3600);
    
                            const hours = Math.floor(totalSeconds / 3600);
                            const minutes = Math.floor((totalSeconds % 3600) / 60);
                            const seconds = totalSeconds % 60;
    
                            return `${context.dataset.label}: ${hours}h ${minutes}m ${seconds}s`;
                        }
                    }
                },
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    color: 'white',
                    display: function (context) {
                        return context.dataset.data[context.dataIndex] !== 0;
                    },
                    formatter: function (value, context) {
                        const chart = context.chart;
                        const index = context.dataIndex;
                        const datasets = chart.data.datasets;
    
                        let total = 0;
                        datasets.forEach(dataset => {
                            const v = dataset.data[index];
                            if (typeof v === 'number') {
                                total += v;
                            }
                        });
    
                        const isTopDataset = context.datasetIndex === datasets.length - 1
                            || datasets.slice(context.datasetIndex + 1).every(ds => !ds.data[index]);
    
                        return isTopDataset ? `${Math.floor(total)}h ${Math.round((total - Math.floor(total)) * 60)}m` : '';
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        color: '#333'
                    },
                    ticks: {
                        color: "white"
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: '#333'
                    },
                    ticks: {
                        color: "white",
                        precision: 2,
                        callback: function (value) {
                            return value + 'h';
                        }
                    },
                    title: {
                        display: true,
                        color: "white"
                    }
                }
            }
        }
    });

    let DonutChart = new Chart(donutCTX, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [],
                borderColor: "#000",
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: 'white'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const value = tooltipItem.raw;
                            const totalSeconds = Math.round(value * 3600);
                            const hours = Math.floor(totalSeconds / 3600);
                            const minutes = Math.floor((totalSeconds % 3600) / 60);
                            const seconds = totalSeconds % 60;
                            return tooltipItem.label + ': ' + hours + 'h ' + minutes + 'm ' + seconds + 's';
                        }
                    },
                    bodyColor: 'white',
                    titleColor: 'white'
                },
                datalabels: {
                    color: '#fff',
                    font: {
                        weight: 'bold'
                    },
                    anchor: 'center',
                    align: 'center',
                    formatter: function (value, context) {
                        const chart = context.chart;
                        const index = context.dataIndex;
                        const datasets = chart.data.datasets;
                        let total = 0;
                        datasets.forEach(dataset => {
                            const v = dataset.data[index];
                            if (typeof v === 'number') {
                                total += v;
                            }
                        });
                        const hours = Math.floor(total);
                        const minutes = Math.floor((total - hours) * 60);
                        return `${hours}h ${minutes}m`;
                    }
                }
            }
        }
    });

    async function fetchChartData(filter) {
        const url = `/teams/team/`;
        const requestBody = JSON.stringify({ filter: filter });

        const data = await sendRequest(url, "POST", requestBody);

        if (data) {
            updateBarChart(data.bar_chart_data);
            updateDonutChart(data.donut_chart_data);
            totalTimeElement.textContent = `Total Time: ${data.total_time}`;
        }
    }

    function updateBarChart(bar_chart_data) {
        labels = bar_chart_data.labels;
        datasets = bar_chart_data.datasets;

        StackedBarChart.data.labels = labels;
        StackedBarChart.data.datasets = datasets;

        let maxStacked = 0;
        for (let i = 0; i < labels.length; i++) {
            let stackedTotal = 0;
            datasets.forEach(dataset => {
                stackedTotal += dataset.data[i] || 0;
            });
            if (stackedTotal > maxStacked) {
                maxStacked = stackedTotal;
            }
        }
        StackedBarChart.options.scales.y.max = Math.ceil(maxStacked * 1.1);

        StackedBarChart.update();
    }

    function updateDonutChart(donut_chart_data) {
        DonutChart.data.labels = donut_chart_data.labels;
        DonutChart.data.datasets = donut_chart_data.datasets;
        DonutChart.data.datasets.forEach(dataset => {
            dataset.borderColor = 'rgb(25, 24, 29)';
        });
        DonutChart.update();
    }

    const timeRangeButtons = document.querySelectorAll('input[name="timeRange"]');
    timeRangeButtons.forEach(button => {
        button.addEventListener("change", function () {
            if (this.checked) {
                fetchChartData(this.id);
            }
        });
    });

    fetchChartData("week");
});

let currentStartDate = new Date();
currentStartDate.setDate(currentStartDate.getDate() - (currentStartDate.getDay() === 0 ? 6 : currentStartDate.getDay() - 1));

function formatDate(date) {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function updateDisplay(projectId, startDate) {
    const endDate = new Date(startDate);
    const displayElement = document.getElementById('date-display-' + projectId);
    const today = new Date();
    const startOfCurrentWeek = new Date(today);
    startOfCurrentWeek.setDate(today.getDate() - (today.getDay() === 0 ? 6 : today.getDay() - 1)); // Start of this week

    const startOfPreviousWeek = new Date(startOfCurrentWeek);
    startOfPreviousWeek.setDate(startOfPreviousWeek.getDate() - 7);

    if (startDate.getDate() === startOfCurrentWeek.getDate()) {
        displayElement.textContent = "This week";
    } else if (startDate.getDate() === startOfPreviousWeek.getDate()) {
        displayElement.textContent = "Last week";
    } else {
        endDate.setDate(startDate.getDate() + 6);
        displayElement.textContent = formatDate(startDate) + ' - ' + formatDate(endDate);
    }
}

function previousWeek(projectId) {
    currentStartDate.setDate(currentStartDate.getDate() - 7);
    updateDisplay(projectId, currentStartDate);
    updateUrlWithDates(projectId, currentStartDate);
}

function nextWeek(projectId) {
    const today = new Date();
    const startOfCurrentWeek = new Date(today);
    startOfCurrentWeek.setDate(today.getDate() - (today.getDay() === 0 ? 6 : today.getDay() - 1));

    const nextStartDate = new Date(currentStartDate);
    nextStartDate.setDate(currentStartDate.getDate() + 7);

    if (nextStartDate > startOfCurrentWeek) {
        return;
    }

    currentStartDate.setDate(currentStartDate.getDate() + 7);
    updateDisplay(projectId, currentStartDate);
    updateUrlWithDates(projectId, currentStartDate);
}

function updateUrlWithDates(projectId, startDate) {
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 6);

    const linkElement = document.getElementById(`generate-report-button-${projectId}`);

    const url = new URL(linkElement.href);
    url.searchParams.set('start_date', formatDate(startDate));
    url.searchParams.set('end_date', formatDate(endDate));

    linkElement.href = url.toString();
}

async function assignTask(memberId, formData) {
    const url = `/teams/member/${memberId}/assign-task/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const success = await sendRequest(url, 'POST', requestBody);

    if (success) {
        window.location.reload();
    }
}

document.querySelectorAll('.assign-task-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const memberId = form.dataset.memberId;
        const formData = new FormData(form);
        
        await assignTask(memberId, formData);
    });
});

async function editMember(memberId, formData) {
    const url = `/teams/member/${memberId}/edit/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const success = await sendRequest(url, 'PATCH', requestBody);

    if (success) {
        window.location.reload();
    }
}

document.querySelectorAll('.edit-member-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const memberId = form.dataset.memberId;
        const formData = new FormData(form);
        
        await editMember(memberId, formData);
    });
});

