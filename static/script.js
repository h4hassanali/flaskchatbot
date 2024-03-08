// Function to fetch predicted response from backend
function getPredictedResponse() {
    const question = document.getElementById('question').value; // Get the user's question
    fetch('http://127.0.0.1:5000/get_response', {
        method: 'POST',
        headers: {
            
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question }) // Send the question to the backend as JSON
    })
    .then(response => response.json())
    .then(data => {
        // Extract predicted response from data
        const predictedResponse = data.response;

        // Update HTML element with the predicted response
        document.getElementById('response').innerText = predictedResponse;
    })
    .catch(error => console.error('Error:', error));
}
