const tg = window.Telegram?.WebApp;
if (tg) tg.expand();
let currentUser = null, socket = null;

async function init() {
    const res = await fetch("/api/user/me", { headers: { "X-Telegram-Init-Data": tg?.initData || "" } });
    currentUser = await res.json();
    document.getElementById("user-name").innerText = currentUser.first_name;
    loadMessages();
    connectWebSocket();
}

async function loadMessages() {
    const res = await fetch("/api/messages");
    const messages = await res.json();
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";
    messages.forEach(appendMessage);
}

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/chat?user_id=${currentUser.telegram_id}`);
    socket.onmessage = (e) => appendMessage(JSON.parse(e.data));
}

function appendMessage(msg) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    const isMy = msg.sender_id === currentUser.telegram_id;
    div.className = `message ${isMy ? "my" : "other"}`;
    div.innerHTML = `<b>${isMy ? "" : (msg.sender_name || "User") + ": "}</b>${msg.text}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("send-btn").addEventListener("click", () => {
    const input = document.getElementById("message-input");
    if (input.value.trim() && socket) {
        socket.send(JSON.stringify({ text: input.value.trim() }));
        input.value = "";
    }
});
init();
