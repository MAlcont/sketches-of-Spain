// WebSocket connection
let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

function connectWebSocket() {
    const wsUrl = 'ws://localhost:8000';

    console.log('Attempting to connect to WebSocket server at:', wsUrl);

    socket = new WebSocket(wsUrl);

    socket.addEventListener('open', function(event) {
        console.log('WebSocket connection established');
        reconnectAttempts = 0;
    });

    socket.addEventListener('message', function(event) {
        try {
            const response = JSON.parse(event.data);
            console.log('Message from server:', response);
        } catch (error) {
            console.error('Error parsing message from server:', error);
        }
    });

    socket.addEventListener('error', function(event) {
        console.error('WebSocket error:', event);
    });

    socket.addEventListener('close', function(event) {
        console.log('WebSocket connection closed');

        // Attempt to reconnect
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            const timeout = Math.pow(2, reconnectAttempts) * 1000; // Exponential backoff
            console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) in ${timeout}ms...`);

            setTimeout(connectWebSocket, timeout);
        } else {
            console.error('Maximum reconnection attempts reached. Please check if the server is running.');
        }
    });
}

// Initialize WebSocket connection when extension loads
connectWebSocket();

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'save_annotation') {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
            sendResponse({status: 'sent'});
        } else {
            sendResponse({status: 'error', message: 'WebSocket is not connected'});
        }
    }
    return true; // Keep the message channel open for sendResponse
});