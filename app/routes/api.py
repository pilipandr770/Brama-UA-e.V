from flask import Blueprint, request, jsonify, send_file, after_this_request
import os
import time
from openai import OpenAI
import openai
from werkzeug.utils import secure_filename
import io
import tempfile

api_bp = Blueprint('api', __name__)

# Get API key and Assistant ID from environment
api_key = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')

# Явно задаем ID ассистента, если его нет в переменных окружения
if not ASSISTANT_ID:
    ASSISTANT_ID = "asst_Kk4rpHVSHMy91b3Nz162cbcJ"
    print(f"[assistant] Використовую хардкодний ASSISTANT_ID: {ASSISTANT_ID}")

# Вывод в лог текущих значений
print(f"[assistant] API ключ: {'Присутній' if api_key else 'Відсутній'}")
print(f"[assistant] ID асистента: {ASSISTANT_ID}")

# Create a client instance
openai.api_key = api_key
client = OpenAI(api_key=api_key)

@api_bp.route('/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Use OpenAI TTS API to convert text to speech
        response = client.audio.speech.create(
            model="tts-1", # or "tts-1-hd" for higher quality
            voice="alloy", # options: alloy, echo, fable, onyx, nova, and shimmer
            input=text
        )
        
        # Save the audio to the temporary file
        response.stream_to_file(temp_file_path)
        
        # Instead of trying to delete after response, create a copy of the data
        with open(temp_file_path, 'rb') as f:
            audio_data = f.read()
        
        # Remove the file immediately after reading
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"Error removing temporary file: {e}")
        
        # Return the data as a response from memory
        return send_file(
            io.BytesIO(audio_data),
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )
        
    except Exception as e:
        print(f"TTS API Error: {str(e)}")
        return jsonify({
            'error': f"Failed to generate speech: {str(e)}",
            'success': False
        }), 500

@api_bp.route('/api/whisper', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    
    # Validate file extension
    filename = audio_file.filename
    if not filename or '.' not in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    # Make sure extension is supported by OpenAI Whisper
    valid_extensions = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext not in valid_extensions:
        ext = 'mp3'  # Default to mp3 if unsupported extension
    
    # Save the received audio to a temporary file with correct extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
    audio_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # Check if file is too short (minimum 0.1 seconds)
        file_size = os.path.getsize(temp_file.name)
        if file_size < 1000:  # Arbitrary small size check (less than 1KB)
            return jsonify({
                'text': '',
                'success': True,
                'warning': 'Audio too short to transcribe'
            })

        # Open the file for reading before passing to the API
        with open(temp_file.name, "rb") as audio_data:
            # Use OpenAI Whisper API to transcribe the audio
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data
            )

        # Cleanup temporary file
        os.unlink(temp_file.name)

        # Return transcription result
        return jsonify({
            'text': transcript.text,
            'success': True
        })
    except Exception as e:
        # Cleanup temporary file in case of error
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        
        print(f"Whisper API Error: {str(e)}")
        return jsonify({
            'error': f"Failed to transcribe audio: {str(e)}",
            'success': False
        }), 500

@api_bp.route('/api/assistant', methods=['POST'])
def assistant():
    print("[assistant] Запит отримано")
    data = request.json
    if not data:
        print("[assistant] Помилка: Invalid JSON content")
        return jsonify({'error': 'Invalid JSON content'}), 400
    
    user_message = data.get('message')
    thread_id = data.get('thread_id')
    print(f"[assistant] Отримано текст: {user_message}")
    print(f"[assistant] thread_id з фронта: {thread_id}")
    if not user_message:
        print("[assistant] Помилка: No message provided")
        return jsonify({'error': 'No message provided'}), 400

    # 2. Використовуємо існуючий thread або створюємо новий
    client = OpenAI(api_key=api_key)
    try:
        if thread_id:
            print(f"[assistant] Використовую thread_id: {thread_id}")
            thread = client.beta.threads.retrieve(thread_id=thread_id)
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
            print(f"[assistant] Створено новий thread_id: {thread_id}")

        # 3. Додаємо повідомлення користувача у thread
        print(f"[assistant] Додаю повідомлення у thread {thread_id}")
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # 4. Запускаємо асистента
        print(f"[assistant] Запускаю асистента {ASSISTANT_ID} для thread {thread_id}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # 5. Чекаємо завершення run (polling)
        for i in range(30):
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"[assistant] Polling {i}: run status = {run_status.status}")
            if run_status.status in ["completed", "failed", "cancelled"]:
                break
            time.sleep(1)

        if run_status.status != "completed":
            print(f"[assistant] Run не завершено: {run_status.status}")
            return jsonify({'error': f'Assistant run status: {run_status.status}'}), 500

        # 6. Отримуємо відповідь асистента
        messages = client.beta.threads.messages.list(thread_id=thread_id)
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
    except Exception as e:
        print(f"[assistant] Error: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500