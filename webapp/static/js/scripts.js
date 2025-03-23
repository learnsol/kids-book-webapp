document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('storyForm');
    const processingMessage = document.getElementById('processingMessage');
    const resultsDiv = document.getElementById('results');
    const compositeStoryP = document.getElementById('compositeStory');
    const illustrationsDiv = document.getElementById('illustrations');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        processingMessage.style.display = 'block';
        resultsDiv.style.display = 'none';

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',  // Identify as AJAX request
            },
        })
        .then(response => response.json())
        .then(data => {
            processingMessage.style.display = 'none';
            resultsDiv.style.display = 'block';

            compositeStoryP.textContent = data.composite_story;

            illustrationsDiv.innerHTML = ''; // Clear previous illustrations
            data.illustrations.forEach((url, index) => {
                const img = document.createElement('img');
                img.src = url;
                img.alt = `Illustration ${index + 1}`;
                illustrationsDiv.appendChild(img);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            processingMessage.style.display = 'none';
            resultsDiv.style.display = 'block';
            compositeStoryP.textContent = 'Error generating story. Please try again.';
            illustrationsDiv.innerHTML = '';
        });
    });
});