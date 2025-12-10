require('dotenv').config();

let currentConvoId = null;
let currentUserEmail = null;

const API_BASE_URL = 'http://134.209.41.148:5001/api';

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

    const emailEl = document.querySelector('.user-email');
    if (emailEl) {
        currentUserEmail = emailEl.textContent.trim();
    }

    initChat();
});

function initChat() {
    const chatForm = document.getElementById('chatForm');
    if (!chatForm) return;

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        input.value = '';

        showTypingIndicator();

        sendMessageToBackend(message);
    });
}

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
            convo_id: currentConvoId || null,
            user_email: currentUserEmail
        })
    })
        .then(async res => {
            let data = null;

            try {
                const clone = res.clone();
                data = await res.json();
                console.log('/chat/message JSON response:', {
                    status: res.status,
                    data
                });
            } catch (jsonErr) {
                console.error('Failed to parse JSON from /chat/message response:', jsonErr);

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

            currentConvoId = data.convo_id;

            loadConversation();
        })
        .catch(error => {
            console.error('Network or fetch error calling /chat/message:', error);
            hideTypingIndicator();
            addBotMessage(`Network error: ${error.message}`);
        });
}

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

function renderConversation(messages) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    chatMessages.innerHTML = '';

    messages.forEach(msg => {
        if (msg.role === 'user') {
            addUserMessage(msg.content, false);
        } else if (msg.role === 'model') {
            if (isMovieRecommendation(msg.content)) {
                addBotMovieRecommendationFromText(msg.content, false);
            } else {
                addBotMessage(msg.content, false);
            }
        } else {
            addBotMessage(msg.content, false);
        }
    });

    scrollToBottom();
}

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

function isMovieRecommendation(text) {
    return /Movie Name:\s*/i.test(text) &&
           /Runtime:\s*\d+/i.test(text) &&
           /Description:\s*/i.test(text);
}

function parseMovieRecommendation(text) {
    const nameMatch = text.match(/Movie Name:\s*(.+)/i);
    const runtimeMatch = text.match(/Runtime:\s*([\d.]+)\s*minutes?/i);
    const descMatch = text.match(/Description:\s*([\s\S]*)/i);

    if (!nameMatch || !runtimeMatch || !descMatch) {
        return null;
    }

    const name = nameMatch[1].trim();
    const runtime = parseInt(runtimeMatch[1], 10);
    const description = descMatch[1].trim();

    return { name, runtime, description };
}

function addBotMovieRecommendationFromText(text, scroll = true) {
    const parsed = parseMovieRecommendation(text);
    if (!parsed) {
        addBotMessage(text, scroll);
        return;
    }

    const { name, runtime, description } = parsed;

    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>Great choice! I'd recommend:</p>
            <div class="recommendation-card">
                <h4>🎬 ${escapeHtml(name)}</h4>
                <p class="rec-description">${escapeHtml(description)}</p>
                <p class="rec-runtime">⏱️ Runtime: ${runtime} minutes</p>
                <a href="/confirm?movie_name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}&runtime=${runtime}" 
                   class="btn btn-primary btn-sm rec-btn">
                    ➕ Add to Watchlist
                </a>
            </div>
            <p>Would you like another recommendation?</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    if (scroll) scrollToBottom();
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

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

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleAddFromChat(movieName, description, runtime) {
    window.location.href = `/confirm?movie_name=${encodeURIComponent(movieName)}&description=${encodeURIComponent(description)}&runtime=${runtime}`;
}

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
