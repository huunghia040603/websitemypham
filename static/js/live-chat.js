(function() {
    const chatBody = document.getElementById('chatBody');
    const input = document.getElementById('messageInput');
    const form = document.getElementById('composer');
    const chatContent = document.getElementById('chatContent');
    const loginPrompt = document.getElementById('loginPrompt');
    const logoUrl = "{{ url_for('static', filename='image/logo.png') }}";
    
    let currentUserId = null;

    // Hàm để tạo và thêm một tin nhắn vào giao diện người dùng
    function appendMessage(senderId, text, timestamp) {
        const isUserMessage = (senderId === currentUserId);
        
        const wrap = document.createElement('div');
        wrap.className = `msg ${isUserMessage ? 'user' : 'agent'}`;

        const displayTime = timestamp ? new Date(timestamp.seconds * 1000).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : 'Vừa xong';

        let messageHTML = '';
        if (isUserMessage) {
            messageHTML = `
                <div class="msg-details">
                    <div class="bubble">${text}</div>
                    <div class="time">${displayTime}</div>
                </div>`;
        } else {
            messageHTML = `
                <img src="${logoUrl}" alt="BuddySkincare" class="avatar">
                <div class="msg-details">
                    <div class="bubble">${text}</div>
                    <div class="time">${displayTime}</div>
                </div>`;
        }

        wrap.innerHTML = messageHTML;
        chatBody.appendChild(wrap);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    if (typeof isLoggedIn === 'function' && isLoggedIn()) {
        console.log("Người dùng đã đăng nhập. Hiển thị khung chat.");
        chatContent.style.display = 'flex';
        loginPrompt.style.display = 'none';

        const userProfile = getUserProfile();
        // Lấy ID người dùng và đảm bảo rằng nó là một chuỗi
        currentUserId = userProfile.id ? String(userProfile.id) : null;
        const adminId = "admin_001";
        
        console.log(`Bước 2: Dữ liệu người dùng thực tế. currentUserId: ${currentUserId}`);

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
        console.log("Bước 1: Firebase đã được khởi tạo.");
        
        const chatId = [currentUserId, adminId].sort().join('_');
        const messagesRef = db.collection('chats').doc(chatId).collection('messages');
        
        messagesRef.orderBy('timestamp').onSnapshot(snapshot => {
            snapshot.docChanges().forEach(change => {
                if (change.type === 'added') {
                    const message = change.doc.data();
                    
                    console.log(`Bước 3: Nhận tin nhắn mới từ Firebase. Người gửi: ${message.senderId}, Nội dung: ${message.text}`);
                    
                    appendMessage(message.senderId, message.text, message.timestamp);
                }
            });
        });

        appendMessage(adminId, 'Chào bạn, mình có thể hỗ trợ gì cho bạn hôm nay?', null);

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const text = (input.value || '').trim();
            if (!text) return;

            const messageData = {
                text: text,
                senderId: currentUserId,
                receiverId: adminId,
                timestamp: firebase.firestore.FieldValue.serverTimestamp()
            };

            console.log("Bước 4: Chuẩn bị gửi tin nhắn tới Flask:", messageData);

            fetch('https://buddyhotro.pythonanywhere.com/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(messageData),
            })
            .then(response => {
                console.log(`Bước 4.1: Nhận phản hồi từ Flask. Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log('Bước 4.2: Dữ liệu phản hồi từ Flask:', data);
                if (data.error) {
                    console.error('Lỗi từ Flask:', data.error);
                } else {
                    console.log('Tin nhắn đã được Flask xử lý thành công.');
                }
            })
            .catch(error => {
                console.error('Lỗi khi gửi yêu cầu tới Flask:', error);
            });
            input.value = '';
        });
    } else {
        console.log("Người dùng chưa đăng nhập. Hiển thị thông báo.");
        chatContent.style.display = 'none';
        loginPrompt.style.display = 'block';
    }
})();