(function() {
    const chatBody = document.getElementById('chatBody');
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPanel = document.getElementById('emojiPanel');
    const chatContent = document.getElementById('chatContent');
    const loginPrompt = document.getElementById('loginPrompt');
    
    let currentUserId = null;
    let currentUserName = null; // Thêm biến để lưu tên người dùng
    let currentUserAvatar = null; // Thêm biến để lưu avatar người dùng
    let currentToken = null;
    let isEmojiPanelOpen = false;
    let isSending = false; // Flag to prevent duplicate sends
    let sentMessages = new Set(); // Track sent messages to prevent duplicates

    // Hàm để tạo và thêm một tin nhắn vào giao diện người dùng
    function appendMessage(senderId, text, timestamp, senderName, senderAvatar) {
        const isUserMessage = (senderId === currentUserId);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUserMessage ? 'user' : 'agent'}`;

        const displayTime = timestamp ? new Date(timestamp.seconds * 1000).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : 'Vừa xong';

        // Escape HTML để tránh lỗi hiển thị
        const escapedText = text.replace(/&/g, '&amp;')
                               .replace(/</g, '&lt;')
                               .replace(/>/g, '&gt;')
                               .replace(/"/g, '&quot;')
                               .replace(/'/g, '&#39;');

        let messageHTML = '';
        if (isUserMessage) {
            // Sử dụng avatar và tên đã lấy được
            const avatarUrl = senderAvatar || '/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg';
            messageHTML = `
                <div class="message-avatar">
                    <img src="${avatarUrl}" alt="${senderName || 'Người dùng'}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" onerror="this.src='/static/image/khach/anh-avatar-nam-ca-tinh-nguoi-that.jpg'">
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
        const messageId = `${currentUserId}_${text}_${Date.now()}`;
        sentMessages.add(messageId);

        // Hiển thị tin nhắn ngay lập tức cho user
        appendMessage(currentUserId, text, null, currentUserName, currentUserAvatar); // Truyền tên và avatar

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
            } else {
                console.log('Message sent successfully.');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
        })
        .finally(() => {
            isSending = false; // Reset flag after request completes
            input.value = '';
            autoResize();
        });
    }

    // Event listeners - only add if not already added
    if (!input.hasAttribute('data-events-added')) {
        input.addEventListener('input', autoResize);
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
        currentUserName = userProfile.name; // Gán tên người dùng
        currentUserAvatar = userProfile.avatar; // Gán avatar người dùng
        currentToken = userProfile.access_token ? String(userProfile.access_token) : null;
        const adminId = "admin_001";
        
        console.log(`Current user ID: ${currentUserId}, Name: ${currentUserName}, Avatar: ${currentUserAvatar}`);
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
                    console.log(`New message from Firebase. Sender: ${message.senderId}, Content: ${message.text}`);
                    
                    // Check if this is a message we just sent (to avoid duplicates)
                    const messageId = message.messageId || `${message.senderId}_${message.text}_${message.timestamp?.seconds || Date.now()}`;
                    
                    if (message.senderId === currentUserId && sentMessages.has(messageId)) {
                        console.log('Skipping duplicate message from Firebase');
                        return; // Skip this message as we already displayed it
                    }
                    
                    // Thêm tham số tên và avatar khi hiển thị tin nhắn từ Firebase
                    appendMessage(message.senderId, message.text, message.timestamp, message.senderName, message.senderAvatar);
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