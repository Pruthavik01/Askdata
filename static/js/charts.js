let myChart = null;

function renderChart(data) {
    const ctx = document.getElementById('chartCanvas').getContext('2d');
    const chartType = document.getElementById('chartType').value || 'bar'; // Default to 'bar'
    
    if (myChart) myChart.destroy();

    // Convert values object to datasets array
    const datasets = Object.keys(data.values).map((key, index) => ({
        label: key,  // Column name as label
        data: data.values[key],  // Data array
        backgroundColor: getColor(index, 0.5),
        borderColor: getColor(index, 1),
        borderWidth: 1
    }));

    myChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: data.labels,  // First column values as labels
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: data.title }
            }
        }
    });

    // Store chart data globally
    window.currentChartData = data;
}

// Function to get dynamic colors for datasets
function getColor(index, opacity) {
    const colors = [
        'rgba(255, 99, 132, OPACITY)',
        'rgba(54, 162, 235, OPACITY)',
        'rgba(255, 206, 86, OPACITY)',
        'rgba(75, 192, 192, OPACITY)',
        'rgba(153, 102, 255, OPACITY)',
        'rgba(255, 159, 64, OPACITY)'
    ];
    return colors[index % colors.length].replace("OPACITY", opacity);
}

// Event listener for chart type change
document.getElementById('chartType').addEventListener('change', () => {
    if (myChart && window.currentChartData) {
        renderChart(window.currentChartData);
    }
});
