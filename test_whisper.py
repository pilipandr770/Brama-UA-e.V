"""
A simple test script to verify the whisper endpoint.
This simulates a POST request with audio data to test OpenAI Whisper integration.
"""

import requests
import sys
import os

def test_whisper_endpoint(audio_file_path):
    """Test the whisper API endpoint with an audio file."""
    
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file '{audio_file_path}' not found")
        return
    
    url = "http://localhost:5000/api/whisper"
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            files = {"audio": audio_file}
            print(f"Sending request to {url} with file: {audio_file_path}")
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Transcribed text: {result['text']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_whisper.py <path_to_audio_file>")
        print("Example: python test_whisper.py test_audio.wav")
        sys.exit(1)
    
    test_whisper_endpoint(sys.argv[1])
