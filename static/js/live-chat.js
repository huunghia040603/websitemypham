(function() {
    const chatBody = document.getElementById('chatBody');
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPanel = document.getElementById('emojiPanel');
    const chatContent = document.getElementById('chatContent');
    const loginPrompt = document.getElementById('loginPrompt');
    
    console.log('DOM elements found:', {
        chatBody: !!chatBody,
        input: !!input,
        sendBtn: !!sendBtn,
        emojiBtn: !!emojiBtn,
        emojiPanel: !!emojiPanel,
        chatContent: !!chatContent,
        loginPrompt: !!loginPrompt
    });
    
    // Check if chatBody is visible
    if (chatBody) {
        console.log('chatBody visibility:', {
            display: chatBody.style.display,
            computedDisplay: window.getComputedStyle(chatBody).display,
            parentDisplay: chatContent ? window.getComputedStyle(chatContent).display : 'chatContent not found'
        });
    }
    
    // Test function to check if appendMessage works
    window.testAppendMessage = function() {
        console.log('Testing appendMessage...');
        if (chatBody) {
            appendMessage('test_user', 'Test message', null, 'test_id', false);
        } else {
            console.error('chatBody not found for test');
        }
    };
    
    let currentUserId = null;
    let currentUserName = null; // Thêm biến để lưu tên người dùng
    let currentUserAvatar = null; // Thêm biến để lưu avatar người dùng
    let currentToken = null;
    let isEmojiPanelOpen = false;
    let isSending = false; // Flag to prevent duplicate sends
    let isClearing = false; // Flag to prevent event listener interference
    let sentMessages = new Set(); // Track sent messages to prevent duplicates
    let displayedMessages = new Set(); // Track displayed messages to prevent duplicates
    let hasLoadedExistingMessages = false; // Flag to track if existing messages have been loaded
    
    // Cleanup old sent messages to prevent memory leak
    function cleanupSentMessages() {
        if (sentMessages.size > 50) {
            const messagesArray = Array.from(sentMessages);
            sentMessages.clear();
            // Keep only the last 25 messages
            messagesArray.slice(-25).forEach(msg => sentMessages.add(msg));
        }
        
        if (displayedMessages.size > 100) {
            const messagesArray = Array.from(displayedMessages);
            displayedMessages.clear();
            // Keep only the last 50 messages
            messagesArray.slice(-50).forEach(msg => displayedMessages.add(msg));
        }
    }
    
    // Debug function to check for duplicates
    function debugDuplicates() {
        console.log('=== DUPLICATE DEBUG ===');
        console.log('Sent messages:', Array.from(sentMessages));
        console.log('Displayed messages:', Array.from(displayedMessages));
        console.log('DOM messages:', document.querySelectorAll('.message').length);
        console.log('User messages in DOM:', document.querySelectorAll('.message.user').length);
        console.log('========================');
    }

    // Hàm để tạo và thêm một tin nhắn vào giao diện người dùng
    function appendMessage(senderId, text, timestamp, messageId = null, isSending = false) {
        console.log('appendMessage called:', { senderId, text, timestamp, messageId, isSending, currentUserId, chatBody });
        
        if (!chatBody) {
            console.error('chatBody not found! Cannot append message.');
            return;
        }
        
        const isUserMessage = (senderId === currentUserId);
        console.log('isUserMessage:', isUserMessage);
        
        // TEMPORARILY DISABLE DUPLICATE DETECTION FOR TESTING
        // Check if this message was already displayed
        if (messageId && displayedMessages.has(messageId)) {
            console.log('Skipping duplicate message in appendMessage:', messageId);
            // return; // TEMPORARILY COMMENTED OUT FOR TESTING
        }
        
        // Additional check: if this is our own message, check if we have the same text recently
        // But only if we don't have a messageId (meaning it's from Firebase without proper ID)
        if (isUserMessage && !isSending && !messageId) {
            const recentMessages = Array.from(document.querySelectorAll('.message.user .message-bubble'));
            const hasRecentSameText = recentMessages.some(msgEl => {
                const msgText = msgEl.textContent.trim();
                return msgText === text.trim();
            });
            
            if (hasRecentSameText) {
                console.log('Skipping duplicate user message in appendMessage - same text already displayed:', text);
                // return; // TEMPORARILY COMMENTED OUT FOR TESTING
            }
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUserMessage ? 'user' : 'agent'}`;
        
        // Add messageId as data attribute for tracking
        if (messageId) {
            messageDiv.setAttribute('data-message-id', messageId);
            displayedMessages.add(messageId); // Track as displayed
        }
        
        // Add sending status class for visual feedback
        if (isSending) {
            messageDiv.classList.add('sending');
        }

        const displayTime = timestamp ? new Date(timestamp.seconds * 1000).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : (isSending ? 'Đang gửi...' : 'Vừa xong');

        // Convert links to clickable links
        const processedText = convertLinksToClickable(text);

        let messageHTML = '';
        if (isUserMessage) {
            // Sử dụng avatar và tên đã lấy được
            const avatarUrl = currentUserAvatar || '/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg';
            messageHTML = `
                <div class="message-avatar">
                    <img src="${avatarUrl}" alt="${currentUserName || 'Người dùng'}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" onerror="this.src='/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg'">
                </div>
                <div class="message-content">
                    <div class="message-bubble">${processedText}</div>
                    <div class="message-time">${displayTime}</div>
                </div>`;
        } else {
            // Use logo.png for agent
            messageHTML = `
                <div class="message-avatar">
                    <img src="/static/image/logo.png" alt="BuddySkincare" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" onerror="this.src='/static/image/logo.png'">
                </div>
                <div class="message-content">
                    <div class="message-bubble">${processedText}</div>
                    <div class="message-time">${displayTime}</div>
                </div>`;
        }

        messageDiv.innerHTML = messageHTML;
        chatBody.appendChild(messageDiv);
        
        console.log('Message added to DOM:', messageDiv);
        console.log('Total messages in chatBody:', chatBody.children.length);
        
        // Auto scroll to bottom with smooth animation
        setTimeout(() => {
            chatBody.scrollTo({
                top: chatBody.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    // Convert links to clickable links
    function convertLinksToClickable(text) {
        // Escape HTML first to prevent XSS
        const escapedText = text.replace(/&/g, '&amp;')
                               .replace(/</g, '&lt;')
                               .replace(/>/g, '&gt;')
                               .replace(/"/g, '&quot;')
                               .replace(/'/g, '&#39;');
        
        // URL regex pattern - matches http, https, www, and common domains
        const urlRegex = /(https?:\/\/[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)/g;
        
        return escapedText.replace(urlRegex, (url) => {
            // Ensure URL has protocol
            let href = url;
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                href = 'https://' + url;
            }
            
            return `<a href="${href}" target="_blank" rel="noopener noreferrer" style="color: #007bff; text-decoration: underline; word-break: break-all;">${url}</a>`;
        });
    }

    // Auto-resize textarea
    function autoResize() {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }

    // Force clear input function - Giống chat modal
    function forceClearInput() {
        isClearing = true; // Set flag to prevent event listener interference
        
        const tempValue = input.value;
        
        // Method 1: Direct value clear
        input.value = '';
        
        // Method 2: Clear all possible properties
        input.innerHTML = '';
        input.textContent = '';
        input.innerText = '';
        
        // Method 3: Force clear using setAttribute
        input.setAttribute('value', '');
        
        // Method 4: Reset height to default
        input.style.height = '35px';
        
        // Method 5: Force focus and select all then clear
        input.focus();
        input.select();
        
        // Method 6: Use document.execCommand for textarea
        if (input.tagName.toLowerCase() === 'textarea') {
            try {
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
            } catch (e) {
                // Fallback if execCommand fails
            }
        }
        
        console.log('Input cleared. Previous value:', tempValue, 'New value:', input.value);
        
        // Verify it's actually cleared
        if (input.value !== '') {
            console.warn('Input still has value after clear:', input.value);
            // Force clear one more time
            input.value = '';
        }
        
        // Reset flag after a short delay
        setTimeout(() => {
            isClearing = false;
        }, 50);
    }

    // Toggle emoji panel
    function toggleEmojiPanel() {
        isEmojiPanelOpen = !isEmojiPanelOpen;
        emojiPanel.style.display = isEmojiPanelOpen ? 'block' : 'none';
    }

    // Add emoji to input
    function addEmoji(emoji) {
        const cursorPos = input.selectionStart;
        const textBefore = input.value.substring(0, cursorPos);
        const textAfter = input.value.substring(input.selectionEnd);
        input.value = textBefore + emoji + textAfter;
        input.selectionStart = input.selectionEnd = cursorPos + emoji.length;
        input.focus();
        autoResize();
    }

    // Show error message to user
    function showErrorMessage(message) {
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message agent error-message';
        errorDiv.style.backgroundColor = '#ffebee';
        errorDiv.style.border = '1px solid #f44336';
        errorDiv.style.color = '#d32f2f';
        errorDiv.innerHTML = `
            <div class="message-content">
                <div class="message-bubble">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        
        chatBody.appendChild(errorDiv);
        
        // Auto scroll to bottom
        setTimeout(() => {
            chatBody.scrollTo({
                top: chatBody.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    // Update message status from "sending" to "sent"
    function updateMessageStatus(messageId, success = true) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.classList.remove('sending');
            if (success) {
                messageElement.classList.add('sent');
                // Update time display
                const timeElement = messageElement.querySelector('.message-time');
                if (timeElement) {
                    timeElement.textContent = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                }
            } else {
                messageElement.classList.add('failed');
                // Update time display
                const timeElement = messageElement.querySelector('.message-time');
                if (timeElement) {
                    timeElement.textContent = 'Gửi thất bại';
                }
            }
        }
    }

    // Send message
    function sendMessage() {
        const text = (input.value || '').trim();
        console.log('sendMessage called:', { text, isSending, currentUserId });
        
        if (!text) {
            console.log('No text to send');
            return;
        }
        
        if (isSending) {
            console.log('Already sending, preventing duplicate');
            return;
        }

        isSending = true; // Set flag to prevent duplicate sends
        console.log('Starting to send message, isSending set to true');

        // Create unique message ID to track duplicates
        const messageId = `${currentUserId}_${text}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sentMessages.add(messageId);
        
        // Also add to displayedMessages to prevent immediate re-display
        displayedMessages.add(messageId);
        
        // Store the messageId in a global variable for Firebase matching
        window.lastSentMessageId = messageId;

        // OPTIMISTIC UI UPDATE - Hiển thị tin nhắn ngay lập tức với trạng thái "đang gửi"
        console.log("Optimistic UI update - showing message immediately");
        appendMessage(currentUserId, text, null, messageId, true); // true = isSending
        
        // Debug duplicates
        debugDuplicates();

        // Clear input immediately for better UX
        forceClearInput();
        
        // Force clear multiple times to ensure it's cleared
        setTimeout(() => {
            forceClearInput();
        }, 10);
        
        setTimeout(() => {
            forceClearInput();
        }, 50);
        
        setTimeout(() => {
            forceClearInput();
        }, 100);

        const messageData = {
            text: text,
            senderId: currentUserId,
            senderName: currentUserName, // Gửi tên người dùng
            senderAvatar: currentUserAvatar, // Gửi avatar người dùng
            receiverId: "admin_001",
            authToken: currentToken,
            messageId: messageId // Add unique ID to track
        };

        console.log("Sending message:", messageData);

        // Send to API in background
        fetch('https://buddyhotro.pythonanywhere.com/api/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(messageData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error from Flask:', data.error);
                // Update message status to failed
                updateMessageStatus(messageId, false);
                // Show error message to user
                showErrorMessage('Không thể gửi tin nhắn. Vui lòng thử lại.');
                // Restore input if error
                input.value = text;
                autoResize();
            } else {
                console.log('Message sent successfully.');
                // Update message status to sent
                updateMessageStatus(messageId, true);
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            // Update message status to failed
            updateMessageStatus(messageId, false);
            // Show error message to user
            showErrorMessage('Lỗi kết nối. Vui lòng kiểm tra internet và thử lại.');
            // Restore input if error
            input.value = text;
            autoResize();
        })
        .finally(() => {
            console.log('Message send completed, resetting isSending flag');
            isSending = false; // Reset flag after request completes
            cleanupSentMessages(); // Cleanup old sent messages
        });
    }

    // Event listeners - only add if not already added
    if (!input.hasAttribute('data-events-added')) {
        input.addEventListener('input', function(e) {
            // Only auto-resize if input has content and we're not clearing or sending
            if (e.target.value.length > 0 && !isSending && !isClearing) {
                autoResize();
            }
        });
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        input.setAttribute('data-events-added', 'true');
    }
    
    if (!sendBtn.hasAttribute('data-events-added')) {
        sendBtn.addEventListener('click', sendMessage);
        sendBtn.setAttribute('data-events-added', 'true');
    }
    
    if (!emojiBtn.hasAttribute('data-events-added')) {
        emojiBtn.addEventListener('click', toggleEmojiPanel);
        emojiBtn.setAttribute('data-events-added', 'true');
    }
    
    // Emoji panel event listeners
    emojiPanel.addEventListener('click', function(e) {
        if (e.target.classList.contains('emoji-btn')) {
            addEmoji(e.target.textContent);
            toggleEmojiPanel();
        }
    });
    
    // Close emoji panel when clicking outside
    document.addEventListener('click', function(e) {
        if (!emojiPanel.contains(e.target) && !emojiBtn.contains(e.target)) {
            if (isEmojiPanelOpen) {
                toggleEmojiPanel();
            }
        }
    });

    console.log('Checking login status:', {
        isLoggedInFunction: typeof isLoggedIn,
        isLoggedInResult: typeof isLoggedIn === 'function' ? isLoggedIn() : 'function not available'
    });
    
    if (typeof isLoggedIn === 'function' && isLoggedIn()) {
        console.log("User logged in. Showing chat interface.");
        chatContent.style.display = 'block';
        loginPrompt.style.display = 'none';

        const userProfile = getUserProfile();
        console.log('User profile from getUserProfile():', userProfile);
        
        currentUserId = userProfile.id ? String(userProfile.id) : null;
        currentUserName = userProfile.name; // Gán tên người dùng
        currentUserAvatar = userProfile.avatar; // Gán avatar người dùng
        currentToken = userProfile.access_token ? String(userProfile.access_token) : null;
        const adminId = "admin_001";
        
        console.log(`Current user ID: ${currentUserId}, Name: ${currentUserName}, Avatar: ${currentUserAvatar}`);
        console.log(`Current token: ${currentToken}`);
        
        // Check if we have required data
        if (!currentUserId) {
            console.error('No currentUserId found! Cannot send messages.');
            return;
        }
        
        if (!currentToken) {
            console.error('No currentToken found! Cannot send messages.');
            return;
        }

        const firebaseConfig = {
            apiKey: "AIzaSyBl_8N53eSIGEbBN2TBSGW36vabMdq2lbI",
            authDomain: "buddyskincare-ec603.firebaseapp.com",
            projectId: "buddyskincare-ec603",
            storageBucket: "buddyskincare-ec603.firebasestorage.app",
            messagingSenderId: "151445800213",
            appId: "1:151445800213:web:62dafa29093235e913151c",
            measurementId: "G-5PLJ2MQ9PW"
        };
        
        firebase.initializeApp(firebaseConfig);
        const db = firebase.firestore();
        console.log("Firebase initialized.");
        
        const chatId = [currentUserId, adminId].sort().join('_');
        const messagesRef = db.collection('chats').doc(chatId).collection('messages');
        
        // First, load existing messages
        console.log('Loading existing messages...');
        messagesRef.orderBy('timestamp').get().then(snapshot => {
            console.log('Loaded existing messages:', snapshot.size);
            snapshot.forEach(doc => {
                const message = doc.data();
                const messageId = message.messageId || `${message.senderId}_${message.text}_${message.timestamp?.seconds || Date.now()}`;
                
                // Check if we already have this message displayed in DOM
                const existingMessage = document.querySelector(`[data-message-id="${messageId}"]`);
                if (!existingMessage) {
                    console.log('Loading existing message:', { messageId, senderId: message.senderId, text: message.text });
                    appendMessage(message.senderId, message.text, message.timestamp, messageId);
                }
            });
            hasLoadedExistingMessages = true;
            console.log('Finished loading existing messages. hasLoadedExistingMessages = true');
        }).catch(error => {
            console.error('Error loading existing messages:', error);
            hasLoadedExistingMessages = true; // Set to true even on error to prevent infinite loading
        });
        
        // Then, listen for new messages
        messagesRef.orderBy('timestamp').onSnapshot(snapshot => {
            console.log('Firebase snapshot received:', {
                size: snapshot.size,
                docChanges: snapshot.docChanges().length,
                hasLoadedExistingMessages: hasLoadedExistingMessages,
                changes: snapshot.docChanges().map(change => ({ type: change.type, docId: change.doc.id }))
            });
            
            snapshot.docChanges().forEach(change => {
                if (change.type === 'added') {
                    const message = change.doc.data();
                    console.log(`New message from Firebase. Sender: ${message.senderId}, Content: ${message.text}, MessageId: ${message.messageId}`);
                    
                    // Use the messageId from Firebase, or create a fallback
                    const messageId = message.messageId || `${message.senderId}_${message.text}_${message.timestamp?.seconds || Date.now()}`;
                    
                    // Check if we already have this message displayed in DOM
                    const existingMessage = document.querySelector(`[data-message-id="${messageId}"]`);
                    if (existingMessage) {
                        console.log('Skipping duplicate message - already in DOM:', messageId);
                        return;
                    }
                    
                    // Check if we already displayed this message
                    if (displayedMessages.has(messageId)) {
                        console.log('Skipping duplicate message - already in displayedMessages:', messageId);
                        return;
                    }
                    
                    // For our own messages, check if we already showed optimistically
                    if (message.senderId === currentUserId && sentMessages.has(messageId)) {
                        console.log('Skipping own message - already shown optimistically:', messageId);
                        return;
                    }
                    
                    console.log('Adding new message to chat:', { messageId, senderId: message.senderId, text: message.text });
                    appendMessage(message.senderId, message.text, message.timestamp, messageId);
                    
                    // Debug duplicates after adding message
                    if (message.senderId === currentUserId) {
                        debugDuplicates();
                    }
                }
            });
        }, error => {
            console.error('Firebase listener error:', error);
        });

        // Welcome message
        appendMessage(adminId, 'Chào bạn! Mình có thể hỗ trợ gì cho bạn hôm nay? 😊', null);
        appendMessage(adminId, 'Chúng tôi có nhiều sản phẩm mỹ phẩm thanh lý với giá tốt. Bạn quan tâm đến sản phẩm nào?', null);
        
        
    } else {
        console.log("User not logged in. Showing login prompt.");
        chatContent.style.display = 'none';
        loginPrompt.style.display = 'block';
    }
    
    // Initialize social messaging buttons
    initializeSocialButtons();
})();

// Initialize social messaging buttons
function initializeSocialButtons() {
    // Zalo button
    const zaloBtn = document.querySelector('.social-btn.zalo');
    if (zaloBtn) {
        zaloBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // You can customize the Zalo link here
            const zaloLink = 'https://zalo.me/0123456789';
            window.open(zaloLink, '_blank');
        });
    }
    
    // Facebook button
    const facebookBtn = document.querySelector('.social-btn.facebook');
    if (facebookBtn) {
        facebookBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // You can customize the Facebook Messenger link here
            const facebookLink = 'https://m.me/buddyskincare';
            window.open(facebookLink, '_blank');
        });
    }
}