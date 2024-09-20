const chatMessages = document.getElementById('chat-box'); // Correct reference to chat-box
const messageInput = document.getElementById('user-input'); // Correct reference to user-input

// Function to add a message to the chat box
function addMessage(message, isUser) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(isUser ? 'user' : 'bot'); // Set classes for user or bot message

    const text = document.createElement('span');
    text.textContent = message;

    messageElement.appendChild(text);
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to send the message to the server and get the chatbot's response
async function sendMessage() {
    const message = messageInput.value.trim(); // Get the input message
    if (message) {
        addMessage(message, true); // Add user message to the chat
        messageInput.value = '';   // Clear input field

        // Show loading animation while waiting for a response
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'bot');
        loadingElement.innerText = 'Loading...'; // Placeholder text or gif
        chatMessages.appendChild(loadingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            // Send POST request to the server
            const response = await fetch('http://localhost:8000/api/chat', {  // Ensure correct endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }) // Send the user's message
            });
            
            // Parse the server's response
            const data = await response.json();
            chatMessages.removeChild(loadingElement); // Remove the loading animation
            addMessage(data.text || 'Sorry, I couldn’t understand that.', false); // Add bot's response

        } catch (error) {
            console.error('Error:', error); // Log any errors
            chatMessages.removeChild(loadingElement); // Remove the loading animation on error
            addMessage('Sorry, there was an error processing your request.', false); // Show error message in chat
        }
    }
}

// Event listener to send a message when the user presses "Enter"
messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();  // Prevents form submission
        sendMessage(); // Trigger message sending
    }
});

