from flask import Blueprint, request, jsonify
import os
import openai
from werkzeug.utils import secure_filename
import io

api_bp = Blueprint('api', __name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')

@api_bp.route('/api/assistant', methods=['POST'])
def assistant():
    print("[assistant] Запит отримано")
    data = request.json
    user_message = data.get('message')
    thread_id = data.get('thread_id')
    print(f"[assistant] Отримано текст: {user_message}")
    print(f"[assistant] thread_id з фронта: {thread_id}")
    if not user_message:
        print("[assistant] Помилка: No message provided")
        return jsonify({'error': 'No message provided'}), 400

    # 2. Використовуємо існуючий thread або створюємо новий
    if thread_id:
        print(f"[assistant] Використовую thread_id: {thread_id}")
        thread = openai.beta.threads.retrieve(thread_id=thread_id)
    else:
        thread = openai.beta.threads.create()
        thread_id = thread.id
        print(f"[assistant] Створено новий thread_id: {thread_id}")

    # 3. Додаємо повідомлення користувача у thread
    print(f"[assistant] Додаю повідомлення у thread {thread_id}")
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    # 4. Запускаємо асистента
    print(f"[assistant] Запускаю асистента {ASSISTANT_ID} для thread {thread_id}")
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    # 5. Чекаємо завершення run (polling)
    import time
    for i in range(30):
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f"[assistant] Polling {i}: run status = {run_status.status}")
        if run_status.status in ["completed", "failed", "cancelled"]:
            break
        time.sleep(1)

    if run_status.status != "completed":
        print(f"[assistant] Run не завершено: {run_status.status}")
        return jsonify({'error': f'Assistant run status: {run_status.status}'}), 500

    # 6. Отримуємо відповідь асистента
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    print(f"[assistant] Отримано {len(messages.data)} повідомлень у thread")
    # Беремо останнє повідомлення від асистента
    answer = None
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            answer = msg.content[0].text.value
            print(f"[assistant] Відповідь асистента: {answer}")
            break
    if not answer:
        print("[assistant] Помилка: No answer from assistant")
        return jsonify({'error': 'No answer from assistant'}), 500

    print(f"[assistant] Повертаю відповідь у фронт. thread_id: {thread_id}")
    return jsonify({
        'answer': answer,
        'thread_id': thread_id
    }) 