document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("memberChart");
    const memberId = canvas.dataset.memberId;
    const ctx = canvas.getContext("2d");

    Chart.register(ChartDataLabels);

    let myChart = new Chart(ctx, {
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

    async function fetchChartData(filter) {
        const url = `/teams/member-chart/${memberId}/filter/`;
        const method = "POST";
        const requestBody = JSON.stringify({ filter: filter});
    
        const data = await sendRequest(url, method, requestBody);
    
        if (data && data.success) {
            updateChart(data.labels, data.datasets);
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    }
    

    function updateChart(labels, datasets) {
        myChart.data.labels = labels;
        myChart.data.datasets = datasets;
        myChart.update();
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
