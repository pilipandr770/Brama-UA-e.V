"""
A simple test script to verify the text-to-speech endpoint.
This simulates a GET request with text parameter to test OpenAI TTS integration.
"""

import requests
import sys
import os
from urllib.parse import quote

def test_tts_endpoint(text, output_file="test_tts_output.mp3"):
    """Test the TTS API endpoint with text and save the audio output."""
    
    # URL-encode the text parameter
    encoded_text = quote(text)
    url = f"http://localhost:5000/tts?text={encoded_text}"
    
    try:
        print(f"Sending request to {url}")
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            # Save the audio file
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            
            print("✅ Success!")
            print(f"Audio saved to: {output_file}")
            
            # On Windows, try to play the audio file
            if os.name == 'nt':
                try:
                    import os
                    os.system(f'start {output_file}')
                    print("Attempting to play the audio file...")
                except:
                    print("Could not automatically play the audio file.")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tts.py <text_to_convert> [output_file.mp3]")
        print("Example: python test_tts.py \"Hello, this is a test.\" output.mp3")
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "test_tts_output.mp3"
    
    test_tts_endpoint(text, output_file)
