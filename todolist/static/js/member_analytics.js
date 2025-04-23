const totalTimeElement = document.getElementById("total_time");

document.addEventListener("DOMContentLoaded", function () {
    const stackedBarCanvas = document.getElementById("memberChart");
    const stackedBarCTX = stackedBarCanvas.getContext("2d");
    
    const donutCanvas = document.getElementById("donutChart");
    const donutCTX = donutCanvas.getContext("2d");

    const memberId = stackedBarCanvas.dataset.memberId;
    
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
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function(context) {
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
                    display: function(context) {
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
                    grid: { display: false }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        precision: 2,
                        callback: function(value) {
                            return value + 'h';
                        },
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
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            const value = tooltipItem.raw;
                            const totalSeconds = Math.round(value * 3600);
    
                            const hours = Math.floor(totalSeconds / 3600);
                            const minutes = Math.floor((totalSeconds % 3600) / 60);
                            const seconds = totalSeconds % 60;
    
                            // Return formatted tooltip label with hours, minutes, seconds
                            return tooltipItem.label + ': ' + hours + 'h ' + minutes + 'm ' + seconds + 's';
                        }
                    }
                },
                datalabels: {
                    color: '#fff',
                    font: {
                        weight: 'bold',
                    },
                    formatter: function(value, context) {
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
        const url = `/teams/member/${memberId}/analytics/`;
        const requestBody = JSON.stringify({ filter: filter});
    
        const data = await sendRequest(url, "POST", requestBody);
    
        if (data) {
            updateBarChart(data.bar_chart_data);
            updateDonutChart(data.donut_chart_data);
            totalTimeElement.textContent = `Total Time: ${data.total_time}`;
        }
    }

    function updateBarChart(bar_chart_data) {
        StackedBarChart.data.labels = bar_chart_data.labels;
        StackedBarChart.data.datasets = bar_chart_data.datasets;
        StackedBarChart.update();
    }

    function updateDonutChart(donut_chart_data) {
        DonutChart.data.labels = donut_chart_data.labels;
        DonutChart.data.datasets = donut_chart_data.datasets;
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
