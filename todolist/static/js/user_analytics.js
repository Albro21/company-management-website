const totalTimeElement = document.getElementById("totalTime");
const totalTasksElement = document.getElementById("totalTasks");

const donutTimeChartCTX = document.getElementById("donutTimeChart").getContext("2d");
const barTimeChartCTX = document.getElementById("barTimeChart").getContext("2d");
const donutTaskChartCTX = document.getElementById("donutTaskChart").getContext("2d");
const barTaskChartCTX = document.getElementById("barTaskChart").getContext("2d");

document.addEventListener("DOMContentLoaded", function () {
    Chart.register(ChartDataLabels);

    let DonutTimeChart = new Chart(donutTimeChartCTX, {
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
                    },
                    titleColor: textColor
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

    let BarTimeChart = new Chart(barTimeChartCTX, {
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

    let DonutTaskChart = new Chart(donutTaskChartCTX, {
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
                            return `${tooltipItem.label}: ${value} completed task${value === 1 ? '' : 's'}`;
                        }
                    },
                    titleColor: textColor
                },
                datalabels: {
                    color: textColor,
                    font: {
                        weight: 'bold'
                    },
                    anchor: 'center',
                    align: 'center',
                    formatter: function (value) {
                        return `${value} task${value === 1 ? '' : 's'}`;
                    }
                }
            }
        }
    });

    let BarTaskChart = new Chart(barTaskChartCTX, {
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
                            return `${context.dataset.label}: ${value} completed task${value === 1 ? '' : 's'}`;
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
                    formatter: function (value) {
                        return `${value} task${value === 1 ? '' : 's'}`;
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
                        stepSize: 1,
                        color: textColor,
                        precision: 0
                    },
                    suggestedMax: 5,
                    title: {
                        display: true,
                        color: textColor,
                        text: 'Completed Tasks'
                    }
                }
            }
        }
    });

    async function fetchChartData(filter) {
        const url = `/user/${userId}/analytics/`;
        const requestBody = JSON.stringify({ filter: filter});
    
        const response = await sendRequest(url, "POST", requestBody);

        if (response.success) {
            const data = response.data;
            updateDonutTimeChart(data.donut_time_chart_data);
            updateBarTimeChart(data.bar_time_chart_data);
            updateDonutTaskChart(data.donut_task_chart_data);
            updateBarTaskChart(data.bar_task_chart_data);
            totalTimeElement.textContent = `Total Time: ${data.total_time}`;
            totalTasksElement.textContent = `Total Tasks: ${data.total_tasks}`;
        }
    }

    function updateDonutTimeChart(donut_time_chart_data) {
        DonutTimeChart.data.labels = donut_time_chart_data.labels;
        DonutTimeChart.data.datasets = donut_time_chart_data.datasets;
        DonutTimeChart.data.datasets.forEach(dataset => {
            dataset.borderColor = 'rgb(25, 24, 29)';
        });
        DonutTimeChart.update();
    }  
    
    function updateBarTimeChart(bar_time_chart_data) {
        labels = bar_time_chart_data.labels;
        datasets = bar_time_chart_data.datasets;

        BarTimeChart.data.labels = labels;
        BarTimeChart.data.datasets = datasets;

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
        BarTimeChart.options.scales.y.max = Math.ceil(maxStacked * 1.1);

        BarTimeChart.update();
    }

    function updateDonutTaskChart(donut_task_chart_data) {
        DonutTaskChart.data.labels = donut_task_chart_data.labels;
        DonutTaskChart.data.datasets = donut_task_chart_data.datasets;
        DonutTaskChart.data.datasets.forEach(dataset => {
            dataset.borderColor = 'rgb(25, 24, 29)';
        });
        DonutTaskChart.update();
    }  
    
    function updateBarTaskChart(bar_task_chart_data) {
        labels = bar_task_chart_data.labels;
        datasets = bar_task_chart_data.datasets;

        BarTaskChart.data.labels = labels;
        BarTaskChart.data.datasets = datasets;

        BarTaskChart.update();
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
