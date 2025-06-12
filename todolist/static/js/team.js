const totalTimeElement = document.getElementById("totalTime");

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
                        color: textColor
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
                    color: textColor,
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
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        precision: 2,
                        callback: function (value) {
                            return value + 'h';
                        }
                    },
                    title: {
                        display: true,
                        color: textColor
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
                        color: textColor
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
                    }
                },
                datalabels: {
                    color: textColor,
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

async function assignTask(employeeId, formData) {
    const url = `/teams/employee/${employeeId}/assign-task/`;
    const requestBody = JSON.stringify(Object.fromEntries(formData.entries()));
    const data = await sendRequest(url, 'POST', requestBody);

    if (data.success) {
        queueToast('Task assigned', 'success');
        window.location.reload();
    }
}

document.querySelectorAll('.assign-task-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const employeeId = form.dataset.employeeId;
        const formData = new FormData(form);
        
        await assignTask(employeeId, formData);
    });
});

// Delete Invitation
async function deleteInvitation(invitationId) {
    const url = `/teams/invitation/${invitationId}/delete/`;
    const data = await sendRequest(url, 'DELETE');
    if (data.success) {
        queueToast('Invitation deleted', 'success');
        window.location.reload();
    }
}
