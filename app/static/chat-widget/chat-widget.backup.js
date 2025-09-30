document.addEventListener('DOMContentLoaded', () => {
    console.log('Brama chat widget: initializing...');
    
    // Создаем и вставляем виджет в DOM
    createChatWidget();
    console.log('Brama chat widget: widget created');
    
    let threadId = null;
    
    // Получаем ссылки на элементы после их создания
    const chatContainer = document.getElementById('brama-chat-container');
    const chatMessages = document.getElementById('brama-chat-messages');
    const messageInput = document.getElementById('brama-message-input');
    const sendButton = document.getElementById('brama-send-button');
    const toggleButton = document.getElementById('brama-chat-toggle');
    const closeButton = document.getElementById('brama-chat-close');
    const clearButton = document.getElementById('brama-clear-chat');
    
    // Прячем/показываем чат по клику на кнопку
    toggleButton.addEventListener('click', () => {
        chatContainer.classList.toggle('brama-chat-open');
        if (chatContainer.classList.contains('brama-chat-open')) {
            messageInput.focus();
        }
    });
    
    // Закрываем чат по клику на кнопку закрытия
    closeButton.addEventListener('click', () => {
        chatContainer.classList.remove('brama-chat-open');
    });
    
    // Очищаем историю чата
    clearButton.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        threadId = null;
        addSystemMessage('Чат очищено');
    });
    
    // Отправка сообщения по клику на кнопку
    sendButton.addEventListener('click', sendMessage);
    
    // Отправка сообщения по нажатию Enter
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Функция отправки сообщения
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Очищаем поле ввода
        messageInput.value = '';
        
        // Добавляем сообщение пользователя в чат
        addUserMessage(message);
        
        // Показываем индикатор загрузки
        const loadingIndicator = addLoadingIndicator();
          try {
            // Отправляем запрос к API
            console.log('Brama chat widget: sending message to API', { message, threadId });
            const response = await fetch('/api/assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    thread_id: threadId
                })
            });
            
            if (!response.ok) {
                throw new Error(`Помилка відповіді сервера: ${response.status} ${response.statusText}`);
            }
            
            console.log('Brama chat widget: response received');
            const data = await response.json();
            console.log('Brama chat widget: parsed response', data);
            threadId = data.thread_id;
            
            // Удаляем индикатор загрузки
            loadingIndicator.remove();
            
            // Добавляем ответ ассистента
            addAssistantMessage(data.answer);
            
            // Прокручиваем к последнему сообщению
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
            
            // Удаляем индикатор загрузки
            loadingIndicator.remove();
            
            // Показываем сообщение об ошибке
            addSystemMessage('Помилка: ' + error.message);
        }
    }
    
    // Функция добавления сообщения от пользователя
    function addUserMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'brama-message brama-user-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Прокручиваем к последнему сообщению
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Функция добавления сообщения от ассистента
    function addAssistantMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'brama-message brama-assistant-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Прокручиваем к последнему сообщению
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Функция добавления системного сообщения
    function addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'brama-message brama-system-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Прокручиваем к последнему сообщению
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Функция добавления индикатора загрузки
    function addLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'brama-message brama-assistant-message brama-loading';
        loadingElement.innerHTML = '<div class="brama-loading-dots"><div></div><div></div><div></div></div>';
        chatMessages.appendChild(loadingElement);
        
        // Прокручиваем к индикатору загрузки
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return loadingElement;
    }
    
    // Функция для создания структуры виджета
    function createChatWidget() {
        // Создаем основной контейнер
        const widgetContainer = document.createElement('div');
        widgetContainer.id = 'brama-chat-widget';
        
        // Создаем кнопку для открытия/закрытия чата
        const toggleButton = document.createElement('button');
        toggleButton.id = 'brama-chat-toggle';
        toggleButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path fill="currentColor" d="M12 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2zm0 2a8 8 0 100 16 8 8 0 000-16zm0 12a1 1 0 110 2 1 1 0 010-2zm0-10a4 4 0 011.543 7.696l-.153.099A1 1 0 0112 14H9a1 1 0 010-2h2.585l.117-.116A2 2 0 1012 10a1 1 0 01-2 0 1 1 0 110-2z"/></svg>';
        
        // Создаем контейнер для окна чата
        const chatContainer = document.createElement('div');
        chatContainer.id = 'brama-chat-container';
        chatContainer.className = ''; // По умолчанию скрыт
        
        // Создаем заголовок чата
        const chatHeader = document.createElement('div');
        chatHeader.id = 'brama-chat-header';
        chatHeader.innerHTML = '<div>Асистент Brama</div>';
        
        // Добавляем кнопку закрытия
        const closeButton = document.createElement('button');
        closeButton.id = 'brama-chat-close';
        closeButton.innerHTML = '&times;';
        chatHeader.appendChild(closeButton);
        
        // Создаем контейнер для сообщений
        const chatMessages = document.createElement('div');
        chatMessages.id = 'brama-chat-messages';
        
        // Создаем контейнер для ввода сообщений
        const inputContainer = document.createElement('div');
        inputContainer.id = 'brama-input-container';
        
        const messageInput = document.createElement('textarea');
        messageInput.id = 'brama-message-input';
        messageInput.placeholder = 'Введіть повідомлення...';
        messageInput.rows = 1;
        messageInput.addEventListener('input', adjustTextareaHeight);
        
        const sendButton = document.createElement('button');
        sendButton.id = 'brama-send-button';
        sendButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path fill="currentColor" d="M3.4 20.4l17.45-7.48a1 1 0 000-1.84L3.4 3.6a.993.993 0 00-1.39.91L2 9.12c0 .5.37.93.87.99L17 12 2.87 13.88c-.5.07-.87.5-.87 1l.01 4.61c0 .71.73 1.2 1.39.91z"/></svg>';
        
        inputContainer.appendChild(messageInput);
        inputContainer.appendChild(sendButton);
        
        // Создаем кнопку очистки чата
        const clearButton = document.createElement('button');
        clearButton.id = 'brama-clear-chat';
        clearButton.textContent = 'Очистити чат';
        
        // Собираем компоненты вместе
        chatContainer.appendChild(chatHeader);
        chatContainer.appendChild(chatMessages);
        chatContainer.appendChild(inputContainer);
        chatContainer.appendChild(clearButton);
        
        widgetContainer.appendChild(toggleButton);
        widgetContainer.appendChild(chatContainer);
        
        // Добавляем виджет на страницу
        document.body.appendChild(widgetContainer);
        
        // Функция для динамического изменения высоты текстового поля
        function adjustTextareaHeight() {
            messageInput.style.height = 'auto';
            messageInput.style.height = (messageInput.scrollHeight) + 'px';
        }
    }
});
