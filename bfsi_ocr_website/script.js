document.getElementById('loanForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let formData = new FormData(this);

    fetch('http://localhost:3000/apply-loan', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = data.message;
    })
    .catch(error => console.error('Error:', error));
});

function processFile() {
    const fileInput = document.getElementById("fileInput");
    const outputText = document.getElementById("outputText");

    if (!fileInput.files.length) {
        alert("Please select a file first.");
        return;
    }

    const file = fileInput.files[0];
    const fileType = file.name.split('.').pop().toLowerCase();

    if (["png", "jpg", "jpeg", "pdf"].includes(fileType)) {
        extractTextFromImage(file);
    } else {
        alert("Choose correct file format.");
    }
}

function extractTextFromImage(imageFile) {
    const outputText = document.getElementById("outputText");

    Tesseract.recognize(
        URL.createObjectURL(imageFile),
        "eng+ara+tam+tel+mal",
        { logger: m => console.log(m) }
    ).then(({ data }) => {
        outputText.value = data.text;
    }).catch(error => {
        console.error("OCR Error:", error);
        outputText.value = "Failed to extract text.";
    });
}
document.getElementById("loanForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission

    let formData = new FormData(this);

    fetch("upload.php", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("status").innerText = "Application Submitted Successfully!";
            document.getElementById("status").style.color = "green";
            this.reset(); // Reset form fields
        } else {
            document.getElementById("status").innerText = "Submission Failed. Try Again.";
            document.getElementById("status").style.color = "red";
        }
    })
    .catch(error => {
        document.getElementById("status").innerText = "Error in Submission.";
        document.getElementById("status").style.color = "red";
    });
});
document.addEventListener("DOMContentLoaded", function () {
    // Get chart elements
    const ctx1 = document.getElementById("transactionsChart").getContext("2d");
    const ctx2 = document.getElementById("invoiceChart").getContext("2d");

    // Placeholder charts (empty initially)
    const transactionsChart = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: [], // Labels will be added dynamically
            datasets: [{
                label: "Total Transactions",
                data: [],
                backgroundColor: "rgba(54, 162, 235, 0.5)"
            }]
        }
    });

    const invoiceChart = new Chart(ctx2, {
        type: "line",
        data: {
            labels: [], // Labels will be added dynamically
            datasets: [{
                label: "Aggregated Invoice Values",
                data: [],
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 2
            }]
        }
    });

    // Function to simulate OCR-extracted data (replace with real OCR data)
    function fetchOCRData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const extractedData = {
                    transactions: [
                        { month: "Jan", count: 120 },
                        { month: "Feb", count: 200 },
                        { month: "Mar", count: 150 },
                        { month: "Apr", count: 180 },
                        { month: "May", count: 220 }
                    ],
                    invoiceValues: [
                        { month: "Jan", value: 5000 },
                        { month: "Feb", value: 7000 },
                        { month: "Mar", value: 6000 },
                        { month: "Apr", value: 9000 },
                        { month: "May", value: 8000 }
                    ]
                };
                resolve(extractedData);
            }, 2000); // Simulate delay
        });
    }

    // Function to update charts with OCR data
    async function updateCharts() {
        const data = await fetchOCRData();

        // Update Transaction Chart
        transactionsChart.data.labels = data.transactions.map(t => t.month);
        transactionsChart.data.datasets[0].data = data.transactions.map(t => t.count);
        transactionsChart.update();

        // Update Invoice Chart
        invoiceChart.data.labels = data.invoiceValues.map(i => i.month);
        invoiceChart.data.datasets[0].data = data.invoiceValues.map(i => i.value);
        invoiceChart.update();
    }

    // Fetch and update data dynamically
    updateCharts();
});

