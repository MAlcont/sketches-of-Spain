// Function to send annotation to background script
function saveAnnotation(text, color) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({
            action: 'save_annotation',
            annotation: {
                text: text,
                color: color
            }
        }, response => {
            if (response && response.status === 'sent') {
                console.log('Annotation sent to server');
                resolve(response);
            } else {
                console.error('Failed to send annotation:', response);
                reject(response);
            }
        });
    });
}

// Example of how to use the saveAnnotation function
// This could be called from your UI event handlers
function handleSaveButtonClick() {
    const selectedText = window.getSelection().toString();
    if (selectedText) {
        saveAnnotation(selectedText, 'blue')
            .then(response => {
                console.log('Annotation saved successfully');
                // Update UI to show success
            })
            .catch(error => {
                console.error('Failed to save annotation:', error);
                // Show error in UI
            });
    }
}

// Add your UI event handlers and other content script logic here
// For example:
document.addEventListener('mouseup', function() {
    const selectedText = window.getSelection().toString();
    if (selectedText && selectedText.length > 0) {
        // Show annotation popup or UI
        console.log('Text selected:', selectedText);
        // Actually call handleSaveButtonClick to send the annotation
        handleSaveButtonClick();
    }
});