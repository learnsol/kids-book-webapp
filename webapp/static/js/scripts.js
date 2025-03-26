document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('storyForm');
    const processingMessage = document.getElementById('processingMessage');
    const resultsDiv = document.getElementById('results');
    const compositeStoryP = document.getElementById('compositeStory');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        processingMessage.style.display = 'block';
        resultsDiv.style.display = 'none';

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            processingMessage.style.display = 'none';
            resultsDiv.style.display = 'block';

            if (data.status === 'success') {
                // Create a blob from the HTML content
                const blob = new Blob([data.html_content], { type: 'text/html' });
                const url = URL.createObjectURL(blob);

                // Display the story in an iframe
                const iframe = document.createElement('iframe');
                iframe.src = url;
                iframe.style.width = '100%';
                iframe.style.height = '600px';
                iframe.style.border = '1px solid #ccc';
                compositeStoryP.innerHTML = '';
                compositeStoryP.appendChild(iframe);

                // Add download button
                const downloadBtn = document.createElement('button');
                downloadBtn.textContent = 'Download Story';
                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'my-kids-story.html';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };
                compositeStoryP.appendChild(downloadBtn);
            } else {
                compositeStoryP.textContent = 'Error generating story. Please try again.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            processingMessage.style.display = 'none';
            resultsDiv.style.display = 'block';
            compositeStoryP.textContent = 'Error generating story. Please try again.';
        });
    });
});