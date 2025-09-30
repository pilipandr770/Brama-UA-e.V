document.addEventListener('DOMContentLoaded', () => {
    createChatWidget();

    let threadId = null;
    const chatMessages = document.getElementById('brama-chat-messages');
    const messageInput = document.getElementById('brama-message-input');
    const sendButton = document.getElementById('brama-send-button');

    function addSystemMessage(text) {
        const el = document.createElement('div');
        el.className = 'brama-message brama-system-message';
        el.textContent = text;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addUserMessage(text) {
        const el = document.createElement('div');
        el.className = 'brama-message brama-user-message';
        el.textContent = text;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addAssistantMessage(text) {
        const el = document.createElement('div');
        el.className = 'brama-message brama-assistant-message';
        el.textContent = text;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoader() {
        const el = document.createElement('div');
        el.className = 'brama-message brama-system-message';
        el.textContent = 'Асистент думає…';
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return el;
    }

    async function pollStatus(threadId, loaderEl) {
        let keepPolling = true;
        while (keepPolling) {
            await new Promise(r => setTimeout(r, 800));
            const res = await fetch(`/api/assistant/status?thread_id=${encodeURIComponent(threadId)}`);
            const data = await res.json();
            if (data.error) {
                loaderEl.textContent = 'Помилка: ' + data.error;
                break;
            }
            if (data.status === 'done' && data.answer) {
                loaderEl.remove();
                addAssistantMessage(data.answer);
                keepPolling = false;
                break;
            }
            // if processing — продовжуємо
        }
    }

    async function sendMessage() {
        const text = (messageInput.value || '').trim();
        if (!text) return;

        addUserMessage(text);
        messageInput.value = '';
        const loaderEl = addLoader();

        try {
            const res = await fetch('/api/assistant', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ question: text, thread_id: threadId })
            });
            const data = await res.json();

            if (data.error) {
                loaderEl.textContent = 'Помилка: ' + data.error;
                return;
            }

            if (data.thread_id) threadId = data.thread_id;

            if (data.status === 'done' && data.answer) {
                loaderEl.remove();
                addAssistantMessage(data.answer);
            } else if (data.status === 'processing') {
                // Не блокуємо: починаємо опитування статусу
                await pollStatus(threadId, loaderEl);
            } else {
                loaderEl.textContent = 'Невідомий статус відповіді.';
            }
        } catch (e) {
            loaderEl.textContent = 'Помилка мережі: ' + e.message;
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

/* Простий генератор DOM віджета (залиш як у тебе, якщо вже є) */
function createChatWidget() {
    if (document.getElementById('brama-chat-container')) return;
    const container = document.createElement('div');
    container.id = 'brama-chat-container';
    container.innerHTML = `
      <div id="brama-chat-box">
        <div id="brama-chat-messages" class="brama-chat-messages"></div>
        <div class="brama-chat-input">
          <input id="brama-message-input" type="text" placeholder="Напишіть повідомлення..." />
          <button id="brama-send-button">▶</button>
        </div>
      </div>
    `;
    document.body.appendChild(container);
}