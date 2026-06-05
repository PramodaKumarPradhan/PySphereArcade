document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Profile Setup
    const editProfileBtn = document.getElementById('editProfileBtn');
    const profileView = document.getElementById('profileView');
    const profileEdit = document.getElementById('profileEdit');
    const profileForm = document.getElementById('profileForm');
    
    // DOM Elements - Profile Display
    const displayUsername = document.getElementById('displayUsername');
    const displayAvatar = document.getElementById('displayAvatar');
    const displayBio = document.getElementById('displayBio');
    
    // DOM Elements - Profile Inputs
    const inputUsername = document.getElementById('inputUsername');
    const inputAvatar = document.getElementById('inputAvatar');
    const inputBio = document.getElementById('inputBio');
    
    // DOM Elements - Chat Interface
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatFeed = document.getElementById('chatFeed');
    
    // Initial User State
    // In a future full-stack implementation, this would be fetched from parsing JWTs or server sessions
    let currentUser = {
        username: inputUsername.value || "Guest User",
        avatar: inputAvatar.value,
        bio: inputBio.value
    };

    // --- Profile Editing Logic ---
    let isEditing = false;
    
    editProfileBtn.addEventListener('click', () => {
        isEditing = !isEditing;
        if (isEditing) {
            profileView.classList.add('hidden');
            profileEdit.classList.remove('hidden');
            editProfileBtn.innerHTML = '<i class="ri-close-line"></i>';
            editProfileBtn.title = "Cancel Editing";
        } else {
            profileEdit.classList.add('hidden');
            profileView.classList.remove('hidden');
            editProfileBtn.innerHTML = '<i class="ri-edit-line"></i>';
            editProfileBtn.title = "Edit Profile";
            
            // Revert unsaved changes in inputs
            inputUsername.value = currentUser.username;
            inputAvatar.value = currentUser.avatar;
            inputBio.value = currentUser.bio;
        }
    });

    profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const rawName = inputUsername.value.trim() || "Anonymous";
        const formAvatarUrl = inputAvatar.value.trim();
        
        // Auto-generate UI avatar if blank
        let finalAvatarUrl = formAvatarUrl;
        if (!finalAvatarUrl) {
            const encodedName = encodeURIComponent(rawName);
            finalAvatarUrl = `https://ui-avatars.com/api/?name=${encodedName}&background=random&size=128`;
            inputAvatar.value = finalAvatarUrl;
        }

        // Update internal state
        currentUser.username = rawName;
        currentUser.avatar = finalAvatarUrl;
        currentUser.bio = inputBio.value.trim();
        
        // Update View Layer (DOM Manipulation)
        displayUsername.textContent = currentUser.username;
        displayAvatar.src = currentUser.avatar;
        displayBio.textContent = currentUser.bio;
        
        // Return to read-only view
        isEditing = false;
        profileEdit.classList.add('hidden');
        profileView.classList.remove('hidden');
        editProfileBtn.innerHTML = '<i class="ri-edit-line"></i>';
        editProfileBtn.title = "Edit Profile";
    });

    // --- Chat Logic ---
    function formatTime(date) {
        let hours = date.getHours();
        let minutes = date.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // 0 becomes 12
        minutes = minutes < 10 ? '0' + minutes : minutes;
        return `${hours}:${minutes} ${ampm}`;
    }

    // Helper to prevent XSS in chat messages
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    function createMessageElement(messageData) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${messageData.isSelf ? 'sent' : 'received'}`;
        
        // Architecture Note: In a connected app, 'isSelf' would map to checking if msg.senderId === user.id
        const escapedContent = escapeHTML(messageData.text);

        msgDiv.innerHTML = `
            <img src="${messageData.avatar}" alt="${messageData.author}" class="message-avatar">
            <div class="message-content">
                <span class="message-author">${messageData.author}</span>
                <div class="message-bubble">
                    ${escapedContent}
                </div>
                <span class="message-time">${messageData.time}</span>
            </div>
        `;
        
        return msgDiv;
    }

    function scrollToBottom() {
        // Use smooth scrolling after a very slight delay to let DOM paint
        requestAnimationFrame(() => {
            chatFeed.scrollTo({
                top: chatFeed.scrollHeight,
                behavior: 'smooth'
            });
        });
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const text = messageInput.value.trim();
        if (!text) return;
        
        // Build Data Payload for Event
        const newMessage = {
            author: currentUser.username,
            avatar: currentUser.avatar,
            text: text,
            time: formatTime(new Date()),
            isSelf: true // Flag for local rendering logic
        };
        
        /* 
         * [FUTURE BACKEND HOOK]
         * socket.emit('sendMessage', newMessage);
         */
        
        // Render Immediately (Optimistic Update)
        const msgElement = createMessageElement(newMessage);
        chatFeed.appendChild(msgElement);
        
        // Reset and Scroll
        messageInput.value = '';
        messageInput.focus();
        scrollToBottom();
        
        // Demo feature: Bot responding
        simulateIncomingMessage();
    });

    function simulateIncomingMessage() {
        // Deliberately delay bot response to simulate network latency
        const delay = 1200 + Math.random() * 1000;
        
        setTimeout(() => {
            const replies = [
                "That's a very solid implementation. Adding Socket.io later will be a breeze.",
                "I completely agree! The glass UI is exceptionally polished.",
                "Have you tried editing your profile on the left? It updates everywhere instantly.",
                "Nexus Lounge is the place to be, indeed. 🚀",
                "Fascinating. Tell me more!"
            ];
            
            const replyMsg = {
                author: "Nexus Bot",
                avatar: "https://ui-avatars.com/api/?name=Nexus+Bot&background=10b981&color=fff",
                text: replies[Math.floor(Math.random() * replies.length)],
                time: formatTime(new Date()),
                isSelf: false
            };
            
            const replyElement = createMessageElement(replyMsg);
            chatFeed.appendChild(replyElement);
            scrollToBottom();
            
        }, delay);
    }
    
    // Setup complete: ensure view is at bottom out of the gate
    scrollToBottom();
    
    /*
     * [FUTURE BACKEND HOOK - Receiving messages]
     * socket.on('receiveMessage', (data) => {
     *     data.isSelf = false;
     *     const msgElement = createMessageElement(data);
     *     chatFeed.appendChild(msgElement);
     *     scrollToBottom();
     * });
     */
});
