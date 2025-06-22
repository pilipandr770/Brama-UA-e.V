// 📁 static/voice-widget.js — повна версія з мікрофоном, TTS, текстовим полем і компактним чатом

document.addEventListener("DOMContentLoaded", () => {
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordTimeout;
    let autoplay = true;
    let interactionMode = "voice+chat";
    let isExpanded = false;

    const assistantUI = document.createElement("div");
    assistantUI.id = "main-assistant-chat";
    assistantUI.style.display = "none";
    assistantUI.style.opacity = "0";
    assistantUI.innerHTML = `
      <div id="assistant-header">
        <span>🤖 Асистент</span>
        <div class="header-controls">
          <button id="toggle-size">📐</button>
          <button id="close-assistant">❌</button>
        </div>
      </div>
      <div id="chat-box"></div>
      <div id="assistant-controls">
        <label><input type="checkbox" id="autoplay-check" checked /> 🔊 Автовідтворення</label>
        <div id="text-input-wrapper">
          <input type="text" id="text-input" placeholder="Напишіть повідомлення...">
          <button id="send-text">📨</button>
          <button id="voice-btn" class="voice-button">🎤</button>
        </div>
        <div id="processing-indicator" style="display: none;">
          <div class="spinner"></div>
          <p>Розпізнавання мовлення...</p>
        </div>
      </div>
    `;
    document.body.appendChild(assistantUI);

    const registerButtonInChat = document.createElement("button");
    registerButtonInChat.className = "register-button-in-chat";
    registerButtonInChat.innerHTML = "📅 Записаться на прием";
    registerButtonInChat.title = "Записаться на прием";
    document.getElementById("assistant-controls").appendChild(registerButtonInChat);

    registerButtonInChat.addEventListener("click", () => {
      const bookingForm = document.createElement("div");
      bookingForm.className = "booking-form";
      bookingForm.innerHTML = `
        <div class="form-header">
          <span>Запись на прием</span>
          <button class="close-form">❌</button>
        </div>
        <form id="booking-form">
          <label>Имя: <input type="text" name="name" required /></label>
          <label>Email: <input type="email" name="email" required /></label>
          <label>Телефон: <input type="tel" name="phone" required /></label>
          <label>Дата: <input type="date" name="date" required /></label>
          <label>Время: <input type="time" name="time" required /></label>
          <label>Тема: <input type="text" name="topic" required /></label>
          <button type="submit">Отправить</button>
        </form>
      `;
      document.body.appendChild(bookingForm);

      bookingForm.querySelector(".close-form").addEventListener("click", () => {
        document.body.removeChild(bookingForm);
      });

      bookingForm.querySelector("#booking-form").addEventListener("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        fetch("/booking", {
          method: "POST",
          body: formData
        }).then(() => {
          alert("Спасибо! Ваша заявка принята.");
          document.body.removeChild(bookingForm);
        });
      });
    });

    const chatStyle = document.createElement("style");
    chatStyle.innerHTML = `
      .register-button-in-chat {
        background: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 10px;
      }

      .register-button-in-chat:hover {
        background: #45a049;
      }

      .voice-button {
        background: #2196F3;
        color: white;
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        cursor: pointer;
        margin-left: 5px;
      }

      .voice-button.recording {
        background: #ff4136;
        animation: pulse 1.5s infinite;
      }

      @keyframes pulse {
        0% {
          box-shadow: 0 0 0 0 rgba(255, 65, 54, 0.7);
        }
        70% {
          box-shadow: 0 0 0 10px rgba(255, 65, 54, 0);
        }
        100% {
          box-shadow: 0 0 0 0 rgba(255, 65, 54, 0);
        }
      }

      #processing-indicator {
        text-align: center;
        margin-top: 10px;
      }

      #processing-indicator .spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #2196F3;
        animation: spin 1s ease-in-out infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(chatStyle);

    function appendMessage(text, isUser = false) {
      const msg = document.createElement("div");
      msg.className = isUser ? "chat-message user" : "chat-message assistant";
      msg.textContent = text;
      document.getElementById("chat-box").appendChild(msg);
      document.getElementById("chat-box").scrollTop = 999999;
    }

    function appendAudioPlayer(audioUrl, label) {
      const container = document.createElement("div");
      container.className = "audio-container";
      const labelEl = document.createElement("div");
      labelEl.className = "audio-label";
      labelEl.textContent = label;
      const audio = document.createElement("audio");
      audio.controls = true;
      audio.src = audioUrl;
      container.appendChild(labelEl);
      container.appendChild(audio);
      document.getElementById("chat-box").appendChild(container);
      if (autoplay) audio.play().catch(() => {});
    }

    function playAudioFromBlob(blob) {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      if (autoplay) {
        audio.play().catch(() => {});
      }
    }

    function sendTextMessage() {
      const input = document.getElementById("text-input");
      const text = input.value.trim();
      if (!text) return;
      const clientId = localStorage.getItem("client_id") || Math.random().toString(36).substring(2);
      localStorage.setItem("client_id", clientId);
      appendMessage(text, true);
      input.value = "";
      const threadId = localStorage.getItem("assistant_thread_id") || null;      fetch("/api/assistant", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ message: text, thread_id: threadId })
      })
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            appendMessage('⚠️ ' + data.error);
            return;
          }
          if (data.thread_id) localStorage.setItem("assistant_thread_id", data.thread_id);
          appendMessage(data.answer);
          if (autoplay) {
            const audio = new Audio(`/tts?text=${encodeURIComponent(data.answer)}`);
            audio.play().catch(() => {});
          }
        });
    }

    document.addEventListener("click", e => {
      if (e.target.id === "send-text") sendTextMessage();
    });
    document.addEventListener("keydown", e => {
      if (e.key === "Enter" && document.activeElement.id === "text-input") sendTextMessage();
    });

    function showAssistantUI() {
      assistantUI.style.display = "flex";
      requestAnimationFrame(() => {
        assistantUI.style.opacity = "1";
      });
    }

    function hideAssistantUI() {
      assistantUI.style.opacity = "0";
      setTimeout(() => {
        assistantUI.style.display = "none";
      }, 300); // Час анімації в мс
    }

    // Функції для запису голосу
    let mediaRecorderVoice;
    let audioChunksVoice = [];
    let isRecordingVoice = false;    // Simplify the recording function
    let audioStream = null;
    
    function startRecording() {
        console.log("Починаю запис...");
        audioChunksVoice = [];
        
        // Show feedback first
        document.getElementById('voice-btn').classList.add('recording');
        document.getElementById('voice-btn').textContent = '⏹️';
        
        // Add visual feedback in chat
        const recordingStartMsg = document.createElement('div');
        recordingStartMsg.className = 'chat-message system';
        recordingStartMsg.id = 'recording-status-msg';
        recordingStartMsg.textContent = '🎤 Запис голосу...';
        document.getElementById('chat-box').appendChild(recordingStartMsg);
        document.getElementById('chat-box').scrollTop = 999999;
        
        // Get audio with simple settings
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            console.log("Аудіо потік отримано");
            audioStream = stream;
            
            // Create a simple recorder with default settings
            mediaRecorderVoice = new MediaRecorder(stream);
            
            // Log the media recorder info
            console.log("MediaRecorder створено:", mediaRecorderVoice.mimeType);
            
            // Collect audio data
            mediaRecorderVoice.ondataavailable = function(event) {
                console.log("Отримано аудіо фрагмент розміром:", event.data.size);
                
                // Only add if there's actual data
                if (event.data && event.data.size > 0) {
                    audioChunksVoice.push(event.data);
                    console.log("Додано аудіо фрагмент, всього:", audioChunksVoice.length);
                    
                    // Update the recording status message
                    const statusMsg = document.getElementById('recording-status-msg');
                    if (statusMsg) {
                        statusMsg.textContent = `🎤 Запис голосу... (${audioChunksVoice.length} фрагментів)`;
                    }
                }
            };
            
            // Start recording with larger chunks
            mediaRecorderVoice.start(1000); // Collect 1-second chunks
            isRecordingVoice = true;
            
            // Add visual pulse
            const voiceBtn = document.getElementById('voice-btn');
            voiceBtn.style.animation = 'pulse 1s infinite';
            
            // Set a timeout to prevent infinite recording
            setTimeout(() => {
                if (isRecordingVoice) {
                    console.log("Автоматично зупиняю запис після 15 секунд");
                    stopRecording();
                }
            }, 15000); // Auto-stop after 15 seconds
        })
        .catch(error => {
            console.error("Помилка доступу до мікрофона:", error);
            
            // Reset UI
            document.getElementById('voice-btn').classList.remove('recording');
            document.getElementById('voice-btn').textContent = '🎤';
            
            // Show error
            const errorMsg = document.getElementById('recording-status-msg') || 
                document.createElement('div');
            errorMsg.className = 'chat-message system error';
            errorMsg.textContent = '⚠️ Помилка доступу до мікрофона. Перевірте налаштування браузера.';
            if (!document.getElementById('recording-status-msg')) {
                document.getElementById('chat-box').appendChild(errorMsg);
            }
            document.getElementById('chat-box').scrollTop = 999999;
        });
    }    function stopRecording() {
        console.log("Зупиняю запис...");
        
        // Check if we're actually recording
        if (!mediaRecorderVoice || !isRecordingVoice) {
            console.log("Запис не був активний");
            return;
        }
        
        try {
            // Update UI immediately
            document.getElementById('voice-btn').classList.remove('recording');
            document.getElementById('voice-btn').textContent = '🎤';
            document.getElementById('voice-btn').style.animation = '';
            
            // Stop recorder only if it's recording
            if (mediaRecorderVoice.state === "recording") {
                console.log("Зупиняю MediaRecorder...");
                mediaRecorderVoice.stop();
                
                // Force a final dataavailable event if we haven't got any data yet
                if (audioChunksVoice.length === 0) {
                    console.log("Немає аудіо даних, примусово отримуємо останній фрагмент");
                    mediaRecorderVoice.requestData();
                }
            }
            
            // Stop and release the audio stream
            if (audioStream) {
                audioStream.getTracks().forEach(track => {
                    console.log("Зупиняю аудіо трек:", track.kind);
                    track.stop();
                });
                audioStream = null;
            }
            
            isRecordingVoice = false;
            
            // Update status message
            const statusMsg = document.getElementById('recording-status-msg');
            if (statusMsg) {
                statusMsg.textContent = '⏳ Розпізнаю мовлення...';
            }
            
            // Show processing indicator
            document.getElementById('processing-indicator').style.display = 'block';
            
            // Check if we have audio data to send
            console.log("Перевірка аудіо даних:", audioChunksVoice.length);
            
            // Add a small delay to ensure all audio chunks are collected
            setTimeout(() => {
                console.log("Відправляю аудіо після зупинки...");
                sendAudioToServer();
            }, 500);
            
        } catch (error) {
            console.error("Помилка при зупинці запису:", error);
            
            // Reset state
            isRecordingVoice = false;
            
            // Show error message
            const statusMsg = document.getElementById('recording-status-msg');
            if (statusMsg) {
                statusMsg.className = 'chat-message system error';
                statusMsg.textContent = '⚠️ Помилка при зупинці запису. Спробуйте ще раз.';
            } else {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'chat-message system error';
                errorMsg.textContent = '⚠️ Помилка запису. Спробуйте ще раз.';
                document.getElementById('chat-box').appendChild(errorMsg);
            }
            document.getElementById('chat-box').scrollTop = 999999;
        }
    }function sendAudioToServer() {
        console.log("Відправляю аудіо на сервер...");
        
        // Verify we have audio data
        if (!audioChunksVoice.length) {
            console.warn('Немає записаного аудіо');
            document.getElementById('processing-indicator').style.display = 'none';
            
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message system error';
            errorMsg.textContent = '⚠️ Запис аудіо не відбувся. Спробуйте ще раз.';
            document.getElementById('chat-box').appendChild(errorMsg);
            document.getElementById('chat-box').scrollTop = 999999;
            return;
        }
        
        console.log(`Отримано ${audioChunksVoice.length} аудіо чанків`);
        
        // Determine MIME type from the recorded data if possible
        let detectedMimeType = null;
        if (audioChunksVoice[0] && audioChunksVoice[0].type) {
            detectedMimeType = audioChunksVoice[0].type;
            console.log(`Визначено MIME тип з даних: ${detectedMimeType}`);
        }
        
        // Choose the best MIME type for OpenAI compatibility
        let mimeType = detectedMimeType || 'audio/webm';
        let fileExt = 'webm';  // Default
        
        // Set proper extension based on detected mime type
        if (mimeType.includes('webm')) {
            fileExt = 'webm';
        } else if (mimeType.includes('ogg')) {
            fileExt = 'ogg';
        } else if (mimeType.includes('mp3')) {
            fileExt = 'mp3';
        } else if (mimeType.includes('mp4')) {
            fileExt = 'mp4';
        } else if (mimeType.includes('wav')) {
            fileExt = 'wav';
        } else {
            // If we can't determine a compatible type, force MP3 which is widely supported
            mimeType = 'audio/mp3';
            fileExt = 'mp3';
        }
        
        console.log(`Використовую MIME тип: ${mimeType}, розширення: ${fileExt}`);
        
        // Create audio blob
        const audioBlob = new Blob(audioChunksVoice, { type: mimeType });
        console.log(`Створено Blob розміром: ${audioBlob.size} байтів`);
        
        // Check if the blob is empty or too small
        if (audioBlob.size < 1000) {
            console.warn('Запис аудіо дуже короткий');
            document.getElementById('processing-indicator').style.display = 'none';
            
            const warningMsg = document.createElement('div');
            warningMsg.className = 'chat-message system';
            warningMsg.textContent = '⚠️ Запис занадто короткий. Спробуйте говорити довше.';
            document.getElementById('chat-box').appendChild(warningMsg);
            document.getElementById('chat-box').scrollTop = 999999;
            return;
        }
        
        // Create a FormData object
        const formData = new FormData();
        
        // Create a File object with the proper MIME type
        const audioFile = new File([audioBlob], `recording.${fileExt}`, { 
            type: mimeType,
            lastModified: new Date().getTime()
        });
        
        // Check file before appending
        console.log(`Файл створено: ${audioFile.name}, тип: ${audioFile.type}, розмір: ${audioFile.size} байтів`);
        
        // Append to FormData
        formData.append('audio', audioFile);
        
        // Remove any previous processing messages
        const processingMsgs = document.querySelectorAll('.chat-message.system');
        processingMsgs.forEach(msg => {
            if (msg.textContent.includes('Розпізнаю мовлення')) {
                msg.textContent = '🎤 Відправляю аудіо...';
            }
        });
        
        // Send request to server
        console.log('Відправляю запит на сервер...');
        fetch('/api/whisper', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log(`Отримано відповідь зі статусом: ${response.status}`);
            if (!response.ok) {
                throw new Error(`Помилка відправки аудіо: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide processing indicator
            document.getElementById('processing-indicator').style.display = 'none';
            
            // Remove processing message
            const processingMsgs = document.querySelectorAll('.chat-message.system');
            processingMsgs.forEach(msg => {
                if (msg.textContent.includes('Відправляю аудіо') || 
                    msg.textContent.includes('Розпізнаю мовлення')) {
                    msg.remove();
                }
            });
            
            console.log('Отримано відповідь від сервера:', data);
            
            // Check for warnings
            if (data.warning) {
                console.warn('Попередження від транскрипції:', data.warning);
                const warningMsg = document.createElement('div');
                warningMsg.className = 'chat-message system';
                warningMsg.textContent = `⚠️ ${data.warning}`;
                document.getElementById('chat-box').appendChild(warningMsg);
            }
            
            // Process the transcribed text
            if (data.text && data.text.trim()) {
                const transcribedText = data.text.trim();
                console.log(`Розпізнано текст: ${transcribedText}`);
                
                // Add user message with transcribed text
                appendMessage(`🎤 ${transcribedText}`, true);
                
                // Also put in text input (but don't auto-send)
                document.getElementById('text-input').value = transcribedText;
                
                // Send message to the assistant
                const threadId = localStorage.getItem("assistant_thread_id") || null;
                
                console.log(`Відправляю текст асистенту: ${transcribedText}`);
                fetch("/api/assistant", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ 
                        message: transcribedText, 
                        thread_id: threadId 
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        appendMessage('⚠️ ' + data.error);
                        return;
                    }
                    if (data.thread_id) localStorage.setItem("assistant_thread_id", data.thread_id);
                    appendMessage(data.answer);
                    
                    if (autoplay) {
                        const audio = new Audio(`/tts?text=${encodeURIComponent(data.answer)}`);
                        audio.play().catch(err => {
                            console.error('Помилка відтворення TTS:', err);
                        });
                    }
                })
                .catch(err => {
                    console.error('Помилка відправки до асистента:', err);                    appendMessage("⚠️ Помилка з'єднання з асистентом");
                });
            } else {
                console.warn('Не отримано тексту від API');
                const noTextMsg = document.createElement('div');
                noTextMsg.className = 'chat-message system';
                noTextMsg.textContent = '⚠️ Не вдалося розпізнати мовлення. Спробуйте ще раз.';
                document.getElementById('chat-box').appendChild(noTextMsg);
                document.getElementById('chat-box').scrollTop = 999999;
            }
        })
        .catch(error => {
            console.error('Помилка при розпізнаванні мовлення:', error);
            document.getElementById('processing-indicator').style.display = 'none';
            
            // Remove processing message
            const processingMsgs = document.querySelectorAll('.chat-message.system');
            processingMsgs.forEach(msg => {
                if (msg.textContent.includes('Відправляю аудіо') || 
                    msg.textContent.includes('Розпізнаю мовлення')) {
                    msg.remove();
                }
            });
            
            // Show error message
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message system error';
            errorMsg.textContent = '❌ Помилка розпізнавання мовлення. Спробуйте використати текстовий ввід.';
            document.getElementById('chat-box').appendChild(errorMsg);
            document.getElementById('chat-box').scrollTop = 999999;
        });
    }    function toggleRecording() {
        console.log("Переключення запису. Поточний стан:", isRecordingVoice);
        
        // Show the assistant UI if it's not already visible
        if (assistantUI.style.display === "none") {
            showAssistantUI();
            
            // Give the UI a moment to appear before starting recording
            setTimeout(() => {
                if (isRecordingVoice) {
                    stopRecording();
                } else {
                    startRecording();
                }
            }, 300);
        } else {
            if (isRecordingVoice) {
                stopRecording();
            } else {
                startRecording();
            }
        }
    }

    // Додаємо обробник для кнопки голосового вводу
    function setupVoiceButton() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.log('API для запису аудіо не підтримується у цьому браузері');
            document.getElementById('voice-btn').style.display = 'none';
            return;
        }
        
        document.getElementById('voice-btn').addEventListener('click', toggleRecording);
    }

    // Викликаємо setupVoiceButton, щоб налаштувати функціональність голосового вводу
    setupVoiceButton();    const recordButton = document.createElement("button");
    recordButton.className = "voice-button";
    recordButton.innerHTML = "🎤";
    recordButton.title = "Натисніть, щоб відкрити чат";
    document.body.appendChild(recordButton);

    recordButton.style.display = "block";  // Always display the button
    assistantUI.style.display = "none";    // Add click event to open the chatbot widget
    recordButton.addEventListener("click", function(e) {
      e.preventDefault();
      showAssistantUI();
    });
    
    // Add special double-click event to start recording directly
    recordButton.addEventListener("dblclick", function(e) {
      e.preventDefault();
      showAssistantUI();
      // Start recording after UI is shown
      setTimeout(() => {
        startRecording();
      }, 300);
    });

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      // Check microphone access without keeping the stream
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          console.log("Доступ до мікрофона отримано для тестування");
          
          // Setup long-press for recording
          let pressTimer;
          let isLongPress = false;
          
          recordButton.addEventListener("mousedown", function(e) {
            pressTimer = setTimeout(() => {
              isLongPress = true;
              showAssistantUI();
              setTimeout(() => startRecording(), 300);
            }, 500);  // Long press threshold: 500ms
          });
          
          recordButton.addEventListener("touchstart", function(e) {
            pressTimer = setTimeout(() => {
              isLongPress = true;
              showAssistantUI();
              setTimeout(() => startRecording(), 300);
            }, 500);  // Long press threshold: 500ms
          });
          
          recordButton.addEventListener("mouseup", function(e) {
            clearTimeout(pressTimer);
            if (isLongPress) {
              stopRecording();
              isLongPress = false;
            }
          });
          
          recordButton.addEventListener("touchend", function(e) {
            clearTimeout(pressTimer);
            if (isLongPress) {
              stopRecording();
              isLongPress = false;
            }
          });
          
          recordButton.addEventListener("mouseleave", function(e) {
            clearTimeout(pressTimer);
            if (isLongPress) {
              stopRecording();
              isLongPress = false;
            }
          });
          
          // Release microphone
          stream.getTracks().forEach(track => track.stop());
        })
        .catch(err => {
          console.error("Microphone access error:", err);
          // Still show button but add a warning when they open the chat
          document.getElementById("voice-btn").style.display = "none";
          
          // Add a listener to show warning when chat opens
          const showWarningOnce = () => {
            appendMessage("⚠️ Немає доступу до мікрофона. Ви можете використовувати текстовий чат.");
            assistantUI.removeEventListener("transitionend", showWarningOnce);
          };
          assistantUI.addEventListener("transitionend", showWarningOnce);
        });
    } else {
      console.error("getUserMedia not supported");
      document.getElementById("voice-btn").style.display = "none";
      
      // Add a listener to show warning when chat opens
      const showWarningOnce = () => {
        appendMessage("⚠️ Ваш браузер не підтримує запис голосу. Ви можете використовувати текстовий чат.");
        assistantUI.removeEventListener("transitionend", showWarningOnce);
      };
      assistantUI.addEventListener("transitionend", showWarningOnce);
    }

    document.getElementById("autoplay-check").addEventListener("change", e => {
      autoplay = e.target.checked;
    });
    document.getElementById("close-assistant").addEventListener("click", hideAssistantUI);

    document.getElementById("toggle-size").addEventListener("click", () => {
      isExpanded = !isExpanded;
      if (isExpanded) {
        assistantUI.classList.add("expanded");
      } else {
        assistantUI.classList.remove("expanded");
      }
    });

    fetch("/static/widget_settings.json")
      .then(r => r.json())
      .then(cfg => {
        interactionMode = cfg.interaction_mode || "voice+chat";
        if (cfg.button) {
          const btn = cfg.button;
          if (btn.text) recordButton.innerHTML = btn.text;
          if (btn.color) recordButton.style.color = btn.color;
          if (btn.background) recordButton.style.backgroundColor = btn.background;
          if (btn.size) {
            recordButton.style.width = btn.size;
            recordButton.style.height = btn.size;
            recordButton.style.fontSize = `calc(${btn.size} * 0.5)`;
          }
          if (btn.position) {
            if (btn.position.includes("bottom")) recordButton.style.bottom = "20px";
            if (btn.position.includes("top")) recordButton.style.top = "20px";
            if (btn.position.includes("left")) recordButton.style.left = "20px";
            if (btn.position.includes("right")) recordButton.style.right = "20px";
          }
        }
      });

    const style = document.createElement("style");
    style.innerHTML = `
    #main-assistant-chat {
      position: fixed;
      bottom: 100px;
      right: 20px;
      width: 320px;
      height: 400px;
      background: white;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      border-radius: 12px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      transition: all 0.3s ease;
      max-height: 80vh;
      opacity: 1;
      transform-origin: bottom right;
    }

    #main-assistant-chat.expanded {
      width: 90%;
      height: 90vh;
      bottom: 5vh;
      right: 5%;
    }

    #assistant-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #4CAF50;
      color: white;
      padding: 10px 20px;
      font-size: 18px;
      border-radius: 12px 12px 0 0;
    }

    .header-controls {
      display: flex;
      gap: 10px;
    }

    .header-controls button {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      font-size: 16px;
      padding: 4px;
    }

    #chat-box {
      flex: 1;
      overflow-y: auto;
      padding: 15px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .chat-message {
      padding: 10px 14px;
      border-radius: 12px;
      max-width: 85%;
      white-space: pre-wrap;
      font-size: 14px;
      line-height: 1.4;
      animation: slideIn 0.3s ease;
    }

    .chat-message.user {
      align-self: flex-end;
      background: #e3f2fd;
      text-align: right;
    }    .chat-message.assistant {
      align-self: flex-start;
      background: #f5f5f5;
      text-align: left;
    }
    
    .chat-message.system {
      align-self: center;
      background: #f0f0f0;
      color: #666;
      font-size: 0.9em;
      padding: 5px 10px;
      border-radius: 10px;
      max-width: 80%;
      text-align: center;
      margin: 5px 0;
    }
    
    .chat-message.error {
      background: #fff0f0;
      color: #d32f2f;
    }

    .audio-container {
      margin-top: 5px;
      width: 100%;
    }

    .audio-label {
      font-size: 0.85em;
      margin-bottom: 3px;
      color: #333;
    }

    #assistant-controls {
      padding: 10px;
      border-top: 1px solid #ddd;
      background: #f9f9f9;
      border-radius: 0 0 12px 12px;
    }

    #text-input-wrapper {
      display: flex;
      gap: 8px;
      margin-top: 8px;
    }

    #text-input {
      flex: 1;
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 20px;
      font-size: 14px;
    }

    #send-text {
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 50%;
      width: 36px;
      height: 36px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .voice-button {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      font-size: 24px;
      border-radius: 50%;
      border: none;
      background-color: #4CAF50;
      color: white;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
      cursor: pointer;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .voice-button:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
    }

    .voice-button:active {
      transform: scale(0.95);
    }

    .voice-button.recording {
      background-color: #f44336;
      animation: pulse 1s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(244,67,54,0.4); }
      70% { box-shadow: 0 0 0 10px rgba(244,67,54,0); }
      100% { box-shadow: 0 0 0 0 rgba(244,67,54,0); }
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    audio {
      width: 100%;
      margin-top: 5px;
    }

    @media (max-width: 768px) {
      #main-assistant-chat {
        width: 90%;
        right: 5%;
        bottom: 80px;
      }
    }

    .register-button-in-chat {
      background: #4CAF50;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 10px;
    }

    .register-button-in-chat:hover {
      background: #45a049;
    }

    .booking-form {
      position: fixed;
      bottom: 20%;
      right: 20%;
      width: 300px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      padding: 20px;
      z-index: 10000;
    }

    .form-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }

    .form-header button {
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
    }

    .booking-form label {
      display: block;
      margin-bottom: 10px;
    }

    .booking-form input {
      width: 100%;
      padding: 8px;
      margin-top: 5px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }

    .booking-form button {
      width: 100%;
      padding: 10px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    .booking-form button:hover {
      background: #45a049;
    }
    `;
    document.head.appendChild(style);

    const registerButton = document.querySelector(".register-button");
    if (registerButton) {
        registerButton.remove();
    }
  });