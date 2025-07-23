// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const documentUpload = document.getElementById('document-upload');
    const uploadStatus = document.getElementById('upload-status');
    const loadingModal = document.getElementById('loading-modal');
    const clearDataBtn = document.getElementById('clear-data-btn');
    const messageBox = document.getElementById('message-box');
    const messageBoxText = document.getElementById('message-box-text');

    // Define a timeout for fetch requests (e.g., 5 minutes for uploads, 2 minutes for chat)
    const UPLOAD_TIMEOUT_MS = 300 * 1000; // 5 minutes
    const CHAT_TIMEOUT_MS = 120 * 1000;   // 2 minutes

    // Function to show a temporary message box
    function showMessageBox(message, type = 'info') {
        messageBoxText.textContent = message;
        messageBox.classList.remove('hidden');
        messageBox.classList.remove('bg-red-600', 'bg-green-600', 'bg-blue-600');

        if (type === 'error') {
            messageBox.classList.add('bg-red-600');
        } else if (type === 'success') {
            messageBox.classList.add('bg-green-600');
        } else {
            messageBox.classList.add('bg-blue-600');
        }

        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 5000); // Hide after 5 seconds
    }

    // Function to add a message to the chat display
    function addMessage(sender, message, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message', 'flex', 'mb-4');

        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble', 'rounded-lg', 'p-3', 'shadow-sm', 'max-w-md');

        if (sender === 'user') {
            bubbleDiv.classList.add('bg-indigo-500', 'text-white', 'ml-auto');
        } else {
            bubbleDiv.classList.add('bg-blue-100', 'text-blue-800', 'mr-auto');
        }

        // Replace newlines with <br> for proper display in HTML
        bubbleDiv.innerHTML = message.replace(/\n/g, '<br>');

        messageDiv.appendChild(bubbleDiv);

        if (sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.classList.add('source-context', 'mt-2', 'text-xs', 'text-gray-500', 'pl-2', 'border-l-2', 'border-indigo-200');
            sourcesDiv.textContent = 'Sources: ' + sources.join(', ');
            bubbleDiv.appendChild(sourcesDiv); // Append sources inside the bubble
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    }

    // Function to show/hide loading modal
    function toggleLoading(show) {
        if (show) {
            loadingModal.classList.remove('hidden');
        } else {
            loadingModal.classList.add('hidden');
        }
    }

    // Event listener for sending chat messages
    sendBtn.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (query) {
            addMessage('user', query);
            userInput.value = ''; // Clear input field
            toggleLoading(true);

            // Use AbortController for fetch timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), CHAT_TIMEOUT_MS);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query }),
                    signal: controller.signal // Attach the signal
                });
                clearTimeout(timeoutId); // Clear timeout if request completes

                const data = await response.json();

                if (response.ok) {
                    addMessage('bot', data.answer, data.source_context);
                } else {
                    addMessage('bot', `Error: ${data.message || 'Something went wrong.'}`);
                    showMessageBox(`Chat error: ${data.message || 'Something went wrong.'}`, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                if (error.name === 'AbortError') {
                    addMessage('bot', 'The request timed out. Please try again or simplify your query.');
                    showMessageBox('Chat request timed out.', 'error');
                } else {
                    addMessage('bot', 'Sorry, I could not connect to the server.');
                    showMessageBox('Network error: Could not connect to the server.', 'error');
                }
            } finally {
                toggleLoading(false);
            }
        }
    });

    // Allow sending message with Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    // Event listener for document upload
    documentUpload.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length === 0) {
            uploadStatus.textContent = '';
            return;
        }

        uploadStatus.innerHTML = '<span class="text-yellow-600">Uploading and processing...</span>';
        toggleLoading(true);

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('file', files[i]); // Append each file
        }

        // Use AbortController for fetch timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), UPLOAD_TIMEOUT_MS);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                signal: controller.signal // Attach the signal
            });
            clearTimeout(timeoutId); // Clear timeout if request completes

            const data = await response.json();

            if (response.ok) {
                uploadStatus.innerHTML = `<span class="text-green-600">${data.message}</span>`;
                showMessageBox(data.message, 'success');
            } else {
                uploadStatus.innerHTML = `<span class="text-red-600">${data.message}</span>`;
                showMessageBox(data.message, 'error');
            }
        } catch (error) {
            console.error('Error during upload:', error);
            if (error.name === 'AbortError') {
                uploadStatus.innerHTML = `<span class="text-red-600">Upload timed out. File might be too large or complex.</span>`;
                showMessageBox('Upload timed out. File might be too large or complex.', 'error');
            } else {
                uploadStatus.innerHTML = `<span class="text-red-600">Network error during upload.</span>`;
                showMessageBox('Network error during upload.', 'error');
            }
        } finally {
            toggleLoading(false);
            documentUpload.value = ''; // Clear the file input
        }
    });

    // Event listener for clearing all data
    clearDataBtn.addEventListener('click', async () => {
        const confirmClear = confirm("Are you sure you want to clear all uploaded documents and indexed data? This action cannot be undone.");
        if (!confirmClear) {
            return;
        }

        toggleLoading(true);
        try {
            const response = await fetch('/clear_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();
            if (response.ok) {
                showMessageBox(data.message, 'success');
                chatMessages.innerHTML = `
                    <div class="message bot-message">
                        <div class="message-bubble bg-blue-100 text-blue-800 rounded-lg p-3 shadow-sm max-w-md">
                            Hello! Upload some documents to get started, then ask me questions about them.
                        </div>
                    </div>`; // Clear chat history
            } else {
                showMessageBox(data.message, 'error');
            }
        } catch (error) {
            console.error('Error clearing data:', error);
            showMessageBox('Network error: Could not clear data.', 'error');
        } finally {
            toggleLoading(false);
        }
    });
});
