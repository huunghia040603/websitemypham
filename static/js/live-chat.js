(function() {
    const chatBody = document.getElementById('chatBody');
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPanel = document.getElementById('emojiPanel');
    const chatContent = document.getElementById('chatContent');
    const loginPrompt = document.getElementById('loginPrompt');
    
    let currentUserId = null;
    let currentToken = null;
    let isEmojiPanelOpen = false;
    let isSending = false; // Flag to prevent duplicate sends
    let isClearing = false; // Flag to prevent event listener interference
    let sentMessages = new Set(); // Track sent messages to prevent duplicates
    let displayedMessages = new Set(); // Track displayed messages to prevent duplicates
    
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

    // Hàm để tạo và thêm một tin nhắn vào giao diện người dùng
    function appendMessage(senderId, text, timestamp, messageId = null) {
        const isUserMessage = (senderId === currentUserId);
        
        // Check if this message was already displayed
        if (messageId && displayedMessages.has(messageId)) {
            console.log('Skipping duplicate message in appendMessage:', messageId);
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUserMessage ? 'user' : 'agent'}`;
        
        // Add messageId as data attribute for tracking
        if (messageId) {
            messageDiv.setAttribute('data-message-id', messageId);
            displayedMessages.add(messageId); // Track as displayed
        }

        const displayTime = timestamp ? new Date(timestamp.seconds * 1000).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : 'Vừa xong';

        // Escape HTML để tránh lỗi hiển thị
        const escapedText = text.replace(/&/g, '&amp;')
                               .replace(/</g, '&lt;')
                               .replace(/>/g, '&gt;')
                               .replace(/"/g, '&quot;')
                               .replace(/'/g, '&#39;');

        let messageHTML = '';
        if (isUserMessage) {
            // Get user avatar from API login response
            const userProfile = getUserProfile();
            const userAvatar = userProfile?.avatar || '/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg';
            messageHTML = `
                <div class="message-avatar">
                    <img src="${userAvatar}" alt="User" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" onerror="this.src='/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg'">
                </div>
                <div class="message-content">
                    <div class="message-bubble">${escapedText}</div>
                    <div class="message-time">${displayTime}</div>
                </div>`;
        } else {
            // Use logo.png for agent
            messageHTML = `
                <div class="message-avatar">
                    <img src="/static/image/logo.png" alt="BuddySkincare" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" onerror="this.src='/static/image/logo.png'">
                </div>
                <div class="message-content">
                    <div class="message-bubble">${escapedText}</div>
                    <div class="message-time">${displayTime}</div>
                </div>`;
        }

        messageDiv.innerHTML = messageHTML;
        chatBody.appendChild(messageDiv);
        
        // Auto scroll to bottom with smooth animation
        setTimeout(() => {
            chatBody.scrollTo({
                top: chatBody.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    // Auto-resize textarea
    function autoResize() {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }
    
    // Force clear input function
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
        input.style.height = '30px';
        
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

    // Send message
    function sendMessage() {
        const text = (input.value || '').trim();
        if (!text || isSending) return; // Prevent duplicate sends

        isSending = true; // Set flag to prevent duplicate sends

        // Create unique message ID to track duplicates
        const messageId = `${currentUserId}_${text}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sentMessages.add(messageId);

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
            receiverId: "admin_001",
            timestamp: firebase.firestore.FieldValue.serverTimestamp(),
            authToken: currentToken,
            messageId: messageId // Add unique ID to track
        };

        console.log("Sending message:", messageData);

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
                // Restore input if error
                input.value = text;
                autoResize();
            } else {
                console.log('Message sent successfully.');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            // Restore input if error
            input.value = text;
            autoResize();
        })
        .finally(() => {
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

    if (typeof isLoggedIn === 'function' && isLoggedIn()) {
        console.log("User logged in. Showing chat interface.");
        chatContent.style.display = 'block';
        loginPrompt.style.display = 'none';

        const userProfile = getUserProfile();
        currentUserId = userProfile.id ? String(userProfile.id) : null;
        currentToken = userProfile.access_token ? String(userProfile.access_token) : null;
        const adminId = "admin_001";
        
        console.log(`Current user ID: ${currentUserId}`);
        console.log(`Current token: ${currentToken}`);

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
        
        messagesRef.orderBy('timestamp').onSnapshot(snapshot => {
            snapshot.docChanges().forEach(change => {
                if (change.type === 'added') {
                    const message = change.doc.data();
                    console.log(`New message from Firebase. Sender: ${message.senderId}, Content: ${message.text}, MessageId: ${message.messageId}`);
                    
                    // Use the messageId from Firebase, or create a fallback
                    const messageId = message.messageId || `${message.senderId}_${message.text}_${message.timestamp?.seconds || Date.now()}`;
                    
                    // Check if we already displayed this message
                    if (displayedMessages.has(messageId)) {
                        console.log('Skipping duplicate message - already in displayedMessages:', messageId);
                        return;
                    }
                    
                    // Check if we already have this message displayed in DOM
                    const existingMessage = document.querySelector(`[data-message-id="${messageId}"]`);
                    if (existingMessage) {
                        console.log('Skipping duplicate message - already in DOM:', messageId);
                        return;
                    }
                    
                    appendMessage(message.senderId, message.text, message.timestamp, messageId);
                }
            });
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