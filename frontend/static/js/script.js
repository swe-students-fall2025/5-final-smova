// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Chat functionality
    initChat();
});

// Chat initialization
function initChat() {
    const chatForm = document.getElementById('chatForm');
    if (!chatForm) return;
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (message) {
            addUserMessage(message);
            input.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Simulate AI response with movie recommendation
            setTimeout(() => {
                hideTypingIndicator();
                
                // Check if message is asking for a movie recommendation
                if (isMovieRequest(message)) {
                    addBotMovieRecommendation(message);
                } else {
                    addBotMessage("I'm here to help you find great movies! Try asking me things like:\n\n• 'Recommend a scary horror movie'\n• 'I want to watch a comedy'\n• 'Give me an action movie like John Wick'\n\nWhat kind of movie are you in the mood for? 🎬");
                }
            }, 1500);
        }
    });
}

// Check if message is requesting a movie
function isMovieRequest(message) {
    const keywords = ['movie', 'recommend', 'watch', 'film', 'show', 'suggest', 'horror', 'comedy', 'action', 'drama', 'thriller', 'romance', 'sci-fi', 'documentary', 'scary'];
    const lowerMessage = message.toLowerCase();
    return keywords.some(keyword => lowerMessage.includes(keyword));
}

// Add user message to chat
function addUserMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message to chat
function addBotMessage(text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add bot message with movie recommendation
function addBotMovieRecommendation(userMessage) {
    // TODO: Backend integration - Uncomment when ready
    /*
    const userEmail = document.querySelector('.user-email').textContent;
    
    fetch('/api/chat/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_email: userEmail,
            message: userMessage
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const aiResponse = data.response;
            
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${escapeHtml(aiResponse).replace(/\n/g, '<br>')}</p>
                    <p>Would you like to add this to your watchlist?</p>
                    <button onclick="handleAddFromChat('Movie Name', 'Description', 120)" 
                            class="btn btn-primary btn-sm rec-btn">
                        ➕ Add to Watchlist
                    </button>
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addBotMessage('Sorry, I encountered an error. Please try again.');
    });
    return;
    */
    
    // TEMPORARY: Mock movie recommendations (remove when backend is connected)
    const movies = getMockRecommendation(userMessage);
    const movie = movies[0];
    
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>Great choice! I'd recommend:</p>
            <div class="recommendation-card">
                <h4>🎬 ${escapeHtml(movie.name)}</h4>
                <p class="rec-description">${escapeHtml(movie.description)}</p>
                <p class="rec-runtime">⏱️ Runtime: ${movie.runtime} minutes</p>
                <a href="/confirm?movie_name=${encodeURIComponent(movie.name)}&description=${encodeURIComponent(movie.description)}&runtime=${movie.runtime}" 
                   class="btn btn-primary btn-sm rec-btn">
                    ➕ Add to Watchlist
                </a>
            </div>
            <p>Would you like another recommendation?</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Get mock movie recommendation based on user message
function getMockRecommendation(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('horror') || lowerMessage.includes('scary')) {
        return [{
            name: 'The Conjuring',
            description: 'Paranormal investigators work to help a family terrorized by a dark presence in their farmhouse.',
            runtime: 112
        }];
    } else if (lowerMessage.includes('comedy') || lowerMessage.includes('funny')) {
        return [{
            name: 'The Grand Budapest Hotel',
            description: 'A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy.',
            runtime: 99
        }];
    } else if (lowerMessage.includes('action')) {
        return [{
            name: 'Mad Max: Fury Road',
            description: 'In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland.',
            runtime: 120
        }];
    } else if (lowerMessage.includes('sci-fi') || lowerMessage.includes('science fiction')) {
        return [{
            name: 'Blade Runner 2049',
            description: 'A young blade runner discovers a secret that could plunge society into chaos and leads him on a quest to find a former blade runner.',
            runtime: 164
        }];
    } else if (lowerMessage.includes('drama')) {
        return [{
            name: '12 Years a Slave',
            description: 'In the antebellum United States, a free black man from upstate New York is kidnapped and sold into slavery.',
            runtime: 134
        }];
    } else {
        return [{
            name: 'The Shawshank Redemption',
            description: 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            runtime: 142
        }];
    }
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
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
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper function to navigate to confirm page with movie details
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