async function updateProgress() {
    const resultContainer = document.getElementById('result-container');

    let response = await fetch('http://127.0.0.1:5000/progress_api');
    if (response.ok) {
        let newText = ''
        let data = await response.json();
        let progress_data = data['progress'];
        for (let timeStamp in progress_data) {
            let text = progress_data[timeStamp];
            let progressText = `${timeStamp}: ${text}`;
            newText += progressText + '<br>';
        };
        if (resultContainer.innerHTML != newText) {
            resultContainer.innerHTML = newText;
        };
        resultContainer.scrollTop = resultContainer.scrollHeight;

    };
};

// Update progress every 1 second
function repeatAsyncFunction(fn, interval) {
    fn(); // Call the function immediately
    setInterval(() => {
        setTimeout(fn, 0); // Use setTimeout to schedule the async function
    }, interval);
};

repeatAsyncFunction(updateProgress, 100);
