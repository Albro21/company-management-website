document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("tasksChart").getContext("2d");

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
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false } },
                y: { 
                    grid: { display: false }, 
                    beginAtZero: true,
                    suggestedMin: 0,
                    suggestedMax: 4,
                    ticks: { precision: 0 }
                }
            }
        }
    });

    async function fetchChartData(filter) {
        const url = "/chart/filter/";
        const method = "POST";
        const requestBody = JSON.stringify({ filter: filter, project_title: projectTitle });
    
        const data = await sendRequest(url, method, requestBody);
    
        if (data && data.success) {
            updateChart(data.labels, data.data);
        } else {
            console.error("Server error:", data ? data.error : "No response");
        }
    }
    

    function updateChart(labels, data) {
        myChart.data.labels = labels;
        myChart.data.datasets[0].data = data;
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
