document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');

    // Update this to your Vercel deployment URL
    const API_URL = 'https://hacktbot-backend.vercel.app';

    // Auto-resize textarea
    function autoResizeTextarea() {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    }

    userInput.addEventListener('input', autoResizeTextarea);

    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;
        typingIndicator.classList.remove('hidden');

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();
            console.log('API Response:', data);

            if (!response.ok) {
                throw new Error(data.detail || `Server error: ${response.status}`);
            }

            if (!data.answer) {
                throw new Error('No answer received from the server');
            }

            addMessage(data.answer, 'bot');
        } catch (error) {
            console.error('Detailed Error:', {
                message: error.message,
                stack: error.stack,
                response: error.response
            });
            
            let errorMessage = 'An error occurred. ';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage += 'Cannot connect to the server. Please check your internet connection.';
            } else if (error.message.includes('content not loaded')) {
                errorMessage += 'Please make sure to process the documents first.';
            } else if (error.message.includes('OPENAI_API_KEY')) {
                errorMessage += 'There is an issue with the AI service configuration.';
            } else {
                errorMessage += `Error details: ${error.message}`;
            }
            
            addMessage(errorMessage, 'error');
        } finally {
            userInput.disabled = false;
            sendButton.disabled = false;
            typingIndicator.classList.add('hidden');
            userInput.focus();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}); 