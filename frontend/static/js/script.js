let currentConvoId = null;
let currentUserEmail = null;

const API_BASE_URL = 'ttp://app:8000/api';

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash');

    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Get user email from DOM (e.g. <span class="user-email">user@example.com</span>)
    const emailEl = document.querySelector('.user-email');
    if (emailEl) {
        currentUserEmail = emailEl.textContent.trim();
    }

    // Chat functionality
    initChat();
});

// Chat initialization
function initChat() {
    const chatForm = document.getElementById('chatForm');
    if (!chatForm) return;

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        input.value = '';

        // Show typing indicator while backend processes and generates AI reply
        showTypingIndicator();

        // Send message to backend; backend auto-creates both user + model messages
        sendMessageToBackend(message);
    });
}

// Send message to backend and then load/render conversation
function sendMessageToBackend(userMessage) {
    if (!currentUserEmail) {
        hideTypingIndicator();
        addBotMessage("You're not logged in or email is missing.");
        return;
    }

    fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            role: 'user',
            message: userMessage,
            // IMPORTANT: only send convo_id if we actually have one
            convo_id: currentConvoId || null
        })
    })
        .then(async res => {
            let data = null;

            // Try to parse JSON; if it fails, show raw text & status
            try {
                const clone = res.clone(); // so we can inspect text if needed
                data = await res.json();
                console.log('/chat/message JSON response:', {
                    status: res.status,
                    data
                });
            } catch (jsonErr) {
                console.error('Failed to parse JSON from /chat/message response:', jsonErr);

                // Try to read raw text for debugging
                try {
                    const text = await res.text();
                    console.log('/chat/message raw response body:', text);
                    hideTypingIndicator();
                    addBotMessage(`Error ${res.status}: Server returned non-JSON response.`);
                } catch (textErr) {
                    console.error('Also failed to read raw text:', textErr);
                    hideTypingIndicator();
                    addBotMessage(`Error ${res.status}: Could not read server response.`);
                }
                return;
            }

            hideTypingIndicator();

            // If HTTP not OK or backend says success:false, show detailed error
            if (!res.ok || !data.success) {
                const errorCode = data.error_code ? ` (${data.error_code})` : '';
                const msg = data.message || 'Sorry, something went wrong. Please try again.';
                console.error('/chat/message returned error:', {
                    status: res.status,
                    data
                });
                addBotMessage(`Error ${res.status}${errorCode}: ${msg}`);
                return;
            }

            // Save/refresh conversation ID from backend
            currentConvoId = data.convo_id;

            // Now load the full conversation and render it
            loadConversation();
        })
        .catch(error => {
            // ONLY hits when fetch itself fails (network/CORS/URL)
            console.error('Network or fetch error calling /chat/message:', error);
            hideTypingIndicator();
            addBotMessage(`Network error: ${error.message}`);
        });
}

// Fetch the full conversation from backend and render messages
function loadConversation() {
    if (!currentConvoId || !currentUserEmail) return;

    fetch(`${API_BASE_URL}/chat/conversation/${currentConvoId}?user_email=${encodeURIComponent(currentUserEmail)}`)
        .then(async res => {
            let data;
            try {
                data = await res.json();
            } catch (e) {
                console.error('Failed to parse JSON from /chat/conversation response', e);
                addBotMessage(`Error ${res.status}: Could not parse server response.`);
                return;
            }

            console.log('/chat/conversation response:', {
                status: res.status,
                data
            });

            if (!res.ok) {
                const errorCode = data.error_code ? ` (${data.error_code})` : '';
                const msg = data.message || 'Could not load conversation.';
                addBotMessage(`Error ${res.status}${errorCode}: ${msg}`);
                return;
            }

            if (!data.success) {
                const errorCode = data.error_code ? ` (${data.error_code})` : '';
                addBotMessage(`${data.message || 'Could not load conversation.'}${errorCode}`);
                return;
            }

            const convo = data.conversation;
            const messages = convo.messages || [];
            renderConversation(messages);
        })
        .catch(error => {
            console.error('Error loading conversation:', error);
            addBotMessage('Sorry, I had trouble loading the conversation.');
        });
}

// Render all messages in the conversation based on role
function renderConversation(messages) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // Clear and re-render full conversation
    chatMessages.innerHTML = '';

    messages.forEach(msg => {
        if (msg.role === 'user') {
            addUserMessage(msg.content, false);
        } else if (msg.role === 'model') {
            addBotMessage(msg.content, false);
        } else {
            // Fallback if role unknown
            addBotMessage(msg.content, false);
        }
    });

    scrollToBottom();
}

// Add user message to chat
// scroll = whether to auto-scroll after adding
function addUserMessage(text, scroll = true) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    if (scroll) scrollToBottom();
}

// Add bot message to chat
function addBotMessage(text, scroll = true) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    if (scroll) scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // Avoid duplicating typing indicator
    if (document.getElementById('typingIndicator')) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper function to navigate to confirm page with movie details (still usable)
function handleAddFromChat(movieName, description, runtime) {
    window.location.href = `/confirm?movie_name=${encodeURIComponent(movieName)}&description=${encodeURIComponent(description)}&runtime=${runtime}`;
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
