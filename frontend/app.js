/**
 * Mathematical Question Refinement Chatbot - Frontend
 * Manages the conversation flow: validation -> refinement -> similarity check
 */

const API_BASE_URL = 'http://localhost:8000';

// Conversation state
let conversationState = {
    phase: 'initial', // 'initial', 'validating', 'valid', 'refining', 'refined', 'checking_similarity', 'complete'
    currentQuestion: '',
    refinedQuestion: '',
    validationAttempts: 0
};

// DOM elements
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const statusBar = document.getElementById('status-text');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    sendButton.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
});

/**
 * Handle user message sending
 */
async function handleSend() {
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    userInput.value = '';
    setStatus('Processing...', 'loading');

    try {
        // Handle different conversation phases
        if (conversationState.phase === 'initial' || conversationState.phase === 'validating') {
            await handleValidation(message);
        } else if (conversationState.phase === 'refining') {
            await handleRefinement(message);
        } else if (conversationState.phase === 'refined') {
            await handleRefinementResponse(message);
        } else if (conversationState.phase === 'checking_similarity') {
            // Similarity check is automatic after acceptance
            setStatus('Ready', '');
        } else {
            // Reset for new question
            conversationState = {
                phase: 'initial',
                currentQuestion: '',
                refinedQuestion: '',
                validationAttempts: 0
            };
            await handleValidation(message);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', `Error: ${error.message}. Please try again.`);
        setStatus('Error occurred', 'error');
    }
}

/**
 * Handle validation phase
 */
async function handleValidation(message) {
    conversationState.phase = 'validating';
    conversationState.currentQuestion = message;
    conversationState.validationAttempts++;

    try {
        const response = await fetch(`${API_BASE_URL}/api/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (data.is_valid) {
            conversationState.phase = 'valid';
            addMessage('bot', data.message);
            if (data.reasoning) {
                addReasoning(data.reasoning);
            }
            
            // Proceed to refinement
            setTimeout(async () => {
                await handleRefinement(message);
            }, 500);
        } else {
            conversationState.phase = 'initial';
            addMessage('bot', data.message);
            if (data.reasoning) {
                addReasoning(data.reasoning);
            }
            if (data.suggestions) {
                addMessage('bot', `💡 Suggestions: ${data.suggestions}`);
            }
            addMessage('bot', 'Please revise your question and try again.');
            setStatus('Waiting for revised question...', '');
        }
    } catch (error) {
        throw new Error(`Validation failed: ${error.message}`);
    }
}

/**
 * Handle refinement phase
 */
async function handleRefinement(question) {
    conversationState.phase = 'refining';
    setStatus('Refining question...', 'loading');

    try {
        const response = await fetch(`${API_BASE_URL}/api/refine`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: question })
        });

        const data = await response.json();
        conversationState.refinedQuestion = data.refined_question;
        conversationState.phase = 'refined';

        addMessage('bot', '✅ Here is the refined version of your question:');
        addMessage('bot', `"${data.refined_question}"`);
        
        if (data.changes_made) {
            addMessage('bot', `📝 Changes made: ${data.changes_made}`);
        }
        if (data.reasoning) {
            addReasoning(data.reasoning);
        }

        // Add action buttons
        addActionButtons();
        setStatus('Review the refinement above', '');
    } catch (error) {
        throw new Error(`Refinement failed: ${error.message}`);
    }
}

/**
 * Handle user response to refinement
 */
async function handleRefinementResponse(message) {
    const lowerMessage = message.toLowerCase().trim();
    
    if (lowerMessage === 'accept' || lowerMessage === 'yes' || lowerMessage === 'ok' || lowerMessage === 'confirm') {
        conversationState.phase = 'checking_similarity';
        addMessage('user', 'Accept');
        addMessage('bot', 'Great! Checking for similar questions...');
        setStatus('Checking similarity...', 'loading');
        
        await checkSimilarity(conversationState.refinedQuestion);
    } else if (lowerMessage === 'reject' || lowerMessage === 'no' || lowerMessage === 'revise' || lowerMessage === 'change') {
        conversationState.phase = 'refining';
        addMessage('user', 'Request revision');
        addMessage('bot', 'Please provide your revised question or describe what changes you\'d like.');
        setStatus('Waiting for revision...', '');
    } else {
        // Treat as a new question for refinement
        await handleRefinement(message);
    }
}

/**
 * Check for similar questions
 */
async function checkSimilarity(question) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/similarity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: question })
        });

        const data = await response.json();

        if (data.similar_questions && data.similar_questions.length > 0) {
            addMessage('bot', `🔍 Found ${data.similar_questions.length} similar question(s) (similarity ≥ ${(data.threshold * 100).toFixed(0)}%):`);
            
            const similarityDiv = document.createElement('div');
            similarityDiv.className = 'similarity-results';
            
            data.similar_questions.forEach((item, index) => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'similarity-item';
                itemDiv.innerHTML = `
                    <span class="similarity-score">${(item.similarity_score * 100).toFixed(1)}%</span>
                    <strong>Q${item.question_id}:</strong> ${item.question}
                    <br><small style="color: #666;">Domain: ${item.domain} | Subdomain: ${item.subdomain}</small>
                `;
                similarityDiv.appendChild(itemDiv);
            });
            
            const lastBotMessage = chatMessages.querySelector('.bot-message:last-child .message-content');
            lastBotMessage.appendChild(similarityDiv);
        } else {
            addMessage('bot', '✅ No similar questions found. Your question appears to be unique!');
        }

        conversationState.phase = 'complete';
        addMessage('bot', '🎉 Process complete! You can enter a new question to start over.');
        setStatus('Ready for new question', 'success');
    } catch (error) {
        throw new Error(`Similarity check failed: ${error.message}`);
    }
}

/**
 * Add message to chat
 */
function addMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Bot'}:</strong> ${escapeHtml(content)}`;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Add reasoning to last bot message
 */
function addReasoning(reasoning) {
    const lastBotMessage = chatMessages.querySelector('.bot-message:last-child .message-content');
    if (lastBotMessage) {
        const reasoningDiv = document.createElement('div');
        reasoningDiv.className = 'reasoning';
        reasoningDiv.textContent = `Reasoning: ${reasoning}`;
        lastBotMessage.appendChild(reasoningDiv);
    }
}

/**
 * Add action buttons for accepting/rejecting refinement
 */
function addActionButtons() {
    const lastBotMessage = chatMessages.querySelector('.bot-message:last-child .message-content');
    if (lastBotMessage) {
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'action-buttons';
        
        const acceptBtn = document.createElement('button');
        acceptBtn.className = 'action-button accept-button';
        acceptBtn.textContent = '✓ Accept';
        acceptBtn.onclick = () => {
            userInput.value = 'accept';
            handleSend();
        };
        
        const rejectBtn = document.createElement('button');
        rejectBtn.className = 'action-button reject-button';
        rejectBtn.textContent = '✗ Request Changes';
        rejectBtn.onclick = () => {
            userInput.value = 'reject';
            handleSend();
        };
        
        buttonsDiv.appendChild(acceptBtn);
        buttonsDiv.appendChild(rejectBtn);
        lastBotMessage.appendChild(buttonsDiv);
    }
}

/**
 * Set status bar text and style
 */
function setStatus(text, type = '') {
    statusBar.textContent = text;
    statusBar.className = type ? `status-${type}` : '';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

