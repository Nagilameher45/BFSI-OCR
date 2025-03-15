document.getElementById('fileInput').addEventListener('change', handleFile);

document.getElementById('processBtn').addEventListener('click', processDocument);

function handleFile(event) {
    const file = event.target.files[0];
    if (file) {
        console.log(`File selected: ${file.name}`);
    }
}

async function processDocument() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('https://your-backend-endpoint.com/process', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error processing document:', error);
    }
}

function displayResults(data) {
    const outputArea = document.getElementById('output');
    outputArea.innerHTML = `<pre>${JSON.stringify(data.text, null, 2)}</pre>`;
    generateCharts(data.analytics);
}

function generateCharts(analytics) {
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: analytics.labels,
            datasets: [{
                label: 'Transaction Values',
                data: analytics.values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
