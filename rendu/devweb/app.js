// App Configuration and State
const API_URL = ''; // Proxied through our Python server, so relative paths work
let isConnected = false;
let chatHistory = [];
let availableModels = [];

// DOM Elements
const modelSelect = document.getElementById('model-select');
const connectionIndicator = document.getElementById('connection-indicator');
const connectionText = document.getElementById('connection-text');
const pingText = document.getElementById('ping-text');
const headerStatusBadge = document.getElementById('header-status-badge');
const messagesArea = document.getElementById('messages-area');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat');
const typingIndicator = document.getElementById('typing-indicator');
const suggestionChips = document.querySelectorAll('.suggestion-chip');
const welcomeCard = document.querySelector('.system-welcome');
const scrollBottomBtn = document.getElementById('scroll-bottom-btn');

// ==========================================================================
// MARKED.JS CUSTOM RENDERER (Code block containers & Copy Buttons)
// ==========================================================================
if (typeof marked !== 'undefined') {
    const renderer = new marked.Renderer();
    
    // Customize code block rendering to wrap it with headers & copy triggers
    renderer.code = function(code, language) {
        const validLang = language || 'txt';
        
        // Escape HTML tags to prevent execution/xss
        const escapedCode = code
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
            
        return `
            <div class="code-block-container">
                <div class="code-block-header">
                    <span>${validLang}</span>
                    <button type="button" class="copy-code-btn" onclick="copyCodeText(this)">Copier</button>
                </div>
                <pre><code class="language-${validLang}">${escapedCode}</code></pre>
            </div>
        `;
    };
    
    marked.use({ renderer });
}

// Global function to handle copying individual code block contents
window.copyCodeText = function(btn) {
    const container = btn.closest('.code-block-container');
    if (!container) return;
    
    const codeEl = container.querySelector('code');
    if (!codeEl) return;
    
    const textToCopy = codeEl.textContent;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        btn.textContent = 'Copié !';
        btn.style.borderColor = 'var(--success)';
        btn.style.color = 'var(--success)';
        
        setTimeout(() => {
            btn.textContent = 'Copier';
            btn.style.borderColor = '';
            btn.style.color = '';
        }, 1500);
    }).catch(err => {
        console.error('Failed to copy code: ', err);
    });
};

// ==========================================================================
// UTILITY FUNCTIONS & LOGIC
// ==========================================================================

// Check Server Connection
async function checkConnection() {
    const startTime = performance.now();
    try {
        const response = await fetch(`${API_URL}/api/tags`, { method: 'GET' });
        const duration = Math.round(performance.now() - startTime);
        
        if (response.ok) {
            const data = await response.json();
            pingText.textContent = `${duration} ms`;
            
            if (!isConnected) {
                setConnectedState(true);
                updateModelsList(data.models || []);
            }
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        pingText.textContent = '-- ms';
        setConnectedState(false);
    }
}

function setConnectedState(connected) {
    isConnected = connected;
    if (connected) {
        connectionIndicator.className = 'status-dot connected';
        connectionText.textContent = 'En ligne';
        connectionText.style.color = 'var(--success)';
        
        headerStatusBadge.textContent = 'Sécurisé • Connecté';
        headerStatusBadge.style.color = 'var(--text-white)';
        
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.placeholder = "Posez votre question financière ici...";
    } else {
        connectionIndicator.className = 'status-dot disconnected';
        connectionText.textContent = 'Hors ligne';
        connectionText.style.color = 'var(--danger)';
        
        headerStatusBadge.textContent = 'Non connecté';
        headerStatusBadge.style.color = 'var(--text-muted)';
        
        sendBtn.disabled = true;
        userInput.disabled = true;
        userInput.placeholder = "Ollama est hors ligne. Lancez Ollama pour démarrer.";
        
        modelSelect.innerHTML = '<option value="" disabled selected>Serveur injoignable</option>';
        availableModels = [];
    }
}

// Update the models dropdown list
function updateModelsList(models) {
    availableModels = models;
    if (models.length === 0) {
        modelSelect.innerHTML = '<option value="" disabled selected>Aucun modèle trouvé</option>';
        return;
    }
    
    modelSelect.innerHTML = '';
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        
        let displayName = model.name;
        if (model.name.includes('phi')) {
            displayName = `Phi-3.5 Financial (Local)`;
        }
        option.textContent = displayName;
        modelSelect.appendChild(option);
    });

    const preferredIndex = models.findIndex(m => m.name.includes('phi') || m.name.includes('financial'));
    if (preferredIndex !== -1) {
        modelSelect.selectedIndex = preferredIndex;
    } else {
        modelSelect.selectedIndex = 0;
    }
}

// Append a message to the messages container
function appendMessage(role, content) {
    // Hide welcome card if visible
    if (welcomeCard && welcomeCard.style.display !== 'none') {
        welcomeCard.style.display = 'none';
    }

    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${role === 'user' ? 'user' : 'bot'}`;

    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';

    const messageMeta = document.createElement('div');
    messageMeta.className = 'message-meta';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messageMeta.textContent = role === 'user' ? `Vous • ${time}` : `TechCorp AI • ${time}`;

    const bubbleContainer = document.createElement('div');
    bubbleContainer.className = 'message-bubble-container';

    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    
    // Parse Markdown if bot and marked is loaded
    if (role === 'bot' && typeof marked !== 'undefined') {
        messageBubble.innerHTML = marked.parse(content);
    } else {
        messageBubble.textContent = content;
    }

    bubbleContainer.appendChild(messageBubble);

    // If bot, add a hover copy button & tooltip next to the bubble
    if (role === 'bot') {
        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.className = 'copy-msg-btn';
        copyBtn.ariaLabel = 'Copier le message';
        copyBtn.innerHTML = `
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
        `;

        const tooltip = document.createElement('div');
        tooltip.className = 'copy-tooltip';
        tooltip.textContent = 'Copié !';

        // Copy button event listener (reads dynamically updated bubble text)
        copyBtn.addEventListener('click', () => {
            const textToCopy = messageBubble.textContent;
            navigator.clipboard.writeText(textToCopy).then(() => {
                tooltip.classList.add('show');
                setTimeout(() => tooltip.classList.remove('show'), 1500);
            }).catch(err => {
                console.error('Failed to copy message:', err);
            });
        });

        bubbleContainer.appendChild(copyBtn);
        bubbleContainer.appendChild(tooltip);
    }

    messageWrapper.appendChild(messageMeta);
    messageWrapper.appendChild(bubbleContainer);
    messageRow.appendChild(messageWrapper);
    messagesArea.appendChild(messageRow);
    
    autoScroll();
    
    return messageBubble;
}

function autoScroll() {
    // Only auto scroll if the user is near the bottom
    const threshold = 150;
    const currentScroll = messagesArea.scrollTop;
    const totalHeight = messagesArea.scrollHeight;
    const visibleHeight = messagesArea.clientHeight;
    
    if (totalHeight - visibleHeight - currentScroll < threshold) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

// Send Message Flow
async function sendMessage(text) {
    if (!text.trim() || !isConnected) return;
    
    const selectedModel = modelSelect.value;
    if (!selectedModel) {
        alert('Veuillez sélectionner un modèle avant d\'envoyer un message.');
        return;
    }

    // Add User Message
    appendMessage('user', text);
    chatHistory.push({ role: 'user', content: text });
    
    // Clear & reset textarea height
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Show typing indicator
    typingIndicator.style.display = 'flex';
    messagesArea.scrollTop = messagesArea.scrollHeight;
    
    // Create bot bubble placeholder
    const botBubble = appendMessage('bot', '');
    let botContent = '';

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: selectedModel,
                messages: chatHistory,
                stream: true
            })
        });

        // Hide typing indicator
        typingIndicator.style.display = 'none';

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Failed to generate response');
        }

        // Read stream of data
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            
            buffer = lines.pop(); 
            
            for (const line of lines) {
                if (line.trim() === '') continue;
                
                try {
                    const parsed = JSON.parse(line);
                    if (parsed.message && parsed.message.content) {
                        botContent += parsed.message.content;
                        
                        // Render streaming content
                        if (typeof marked !== 'undefined') {
                            botBubble.innerHTML = marked.parse(botContent);
                        } else {
                            botBubble.textContent = botContent;
                        }
                        autoScroll();
                    }
                } catch (e) {
                    console.warn('Failed to parse streaming line:', line, e);
                }
            }
        }

        chatHistory.push({ role: 'assistant', content: botContent });

    } catch (error) {
        console.error('Error during streaming chat:', error);
        typingIndicator.style.display = 'none';
        botBubble.innerHTML = `<span style="color: var(--danger)">Erreur : ${error.message}</span>`;
    }
}

// ==========================================================================
// INTERACTIVE EVENT LISTENERS
// ==========================================================================

// Auto-grow textarea functionality
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    // Constrain height expansion based on scrollHeight
    this.style.height = (this.scrollHeight) + 'px';
});

// Keypress listener: Enter sends, Shift+Enter insert line break
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Form submission handler
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

// Clear chat history
clearChatBtn.addEventListener('click', () => {
    messagesArea.innerHTML = '';
    welcomeCard.style.display = 'flex';
    messagesArea.appendChild(welcomeCard);
    chatHistory = [];
    scrollBottomBtn.classList.remove('visible');
});

// Setup prompt chips trigger
suggestionChips.forEach(chip => {
    chip.addEventListener('click', () => {
        if (isConnected) {
            sendMessage(chip.textContent);
        }
    });
});

// Floating Scroll Button Scroll event
messagesArea.addEventListener('scroll', () => {
    const threshold = 200;
    const currentScroll = messagesArea.scrollTop;
    const totalHeight = messagesArea.scrollHeight;
    const visibleHeight = messagesArea.clientHeight;
    
    if (totalHeight - visibleHeight - currentScroll > threshold) {
        scrollBottomBtn.classList.add('visible');
    } else {
        scrollBottomBtn.classList.remove('visible');
    }
});

// Floating Scroll Button click action
scrollBottomBtn.addEventListener('click', () => {
    messagesArea.scrollTo({
        top: messagesArea.scrollHeight,
        behavior: 'smooth'
    });
});

// Initial Connection Check and Loop
checkConnection();
setInterval(checkConnection, 5000);
