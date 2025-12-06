"""
TTS API Server with OpenAI TTS (primary) and FishAudio TTS (fallback)
Run this separately: python tts_server.py
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
from openai import OpenAI
import time
import requests

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Voice configuration
OPENAI_VOICE = "nova"  # Natural, friendly female voice
FISH_VOICE = "fishaudio_v1_female"  # FishAudio female voice

def generate_speech_openai(text: str, output_path: str):
    """Generate speech using OpenAI TTS"""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice=OPENAI_VOICE,
            input=text
        )
        response.stream_to_file(output_path)
        print(f"[OpenAI TTS] Generated successfully for text: {text[:30]}...")
        return True
    except Exception as e:
        print(f"[OpenAI TTS] Error: {str(e)}")
        return False

def generate_speech_fishaudio(text: str, output_path: str):
    """Generate speech using FishAudio TTS as fallback"""
    try:
        # FishAudio API endpoint (free, no API key required)
        url = "https://api.fish.audio/v1/tts"
        
        payload = {
            "text": text,
            "voice": FISH_VOICE,
            "format": "mp3"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"[FishAudio TTS] Generated successfully for text: {text[:30]}...")
            return True
        else:
            print(f"[FishAudio TTS] Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[FishAudio TTS] Error: {str(e)}")
        return False

def generate_speech(text: str, output_path: str):
    """Generate speech with automatic fallback"""
    # Try OpenAI first
    if generate_speech_openai(text, output_path):
        return
    
    # Fallback to FishAudio if OpenAI fails
    print("[TTS] OpenAI failed, trying FishAudio fallback...")
    if generate_speech_fishaudio(text, output_path):
        return
    
    # Both failed
    raise Exception("All TTS providers failed")

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API info"""
    return jsonify({
        'service': 'Agrimater TTS Server',
        'status': 'running',
        'primary_provider': 'OpenAI',
        'fallback_provider': 'FishAudio',
        'voice': OPENAI_VOICE,
        'endpoints': {
            'health': '/health',
            'tts': '/api/tts (POST)'
        }
    })

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    output_path = None
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
            
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        print(f"[TTS] Received request for text: {text[:50]}...")
        
        # Create temporary file for audio in /tmp (Render compatible)
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"tts_{os.getpid()}_{int(time.time() * 1000)}.mp3")
        
        print(f"[TTS] Output path: {output_path}")
        print(f"[TTS] Output path: {output_path}")
        
        # Generate speech
        try:
            generate_speech(text, output_path)
        except Exception as gen_error:
            print(f"[TTS] Generation error: {str(gen_error)}")
            raise
        
        # Verify file was created and has content
        if not os.path.exists(output_path):
            print(f"[TTS] ERROR: File not created at {output_path}")
            return jsonify({"error": "Failed to generate audio file"}), 500
            
        file_size = os.path.getsize(output_path)
        print(f"[TTS] Audio file created successfully: {output_path} ({file_size} bytes)")
        
        if file_size == 0:
            print(f"[TTS] ERROR: Generated file is empty")
            os.unlink(output_path)
            return jsonify({"error": "Generated audio file is empty"}), 500
        
        # Read file into memory and delete immediately
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Clean up temp file
        try:
            os.unlink(output_path)
            print(f"[TTS] Cleaned up temp file: {output_path}")
        except Exception as cleanup_error:
            print(f"[TTS] Cleanup warning: {cleanup_error}")
        
        # Return audio data from memory
        from io import BytesIO
        return send_file(
            BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        print(f"[TTS] ERROR in endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[TTS] Traceback: {traceback.format_exc()}")
        
        # Cleanup on error
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
                print(f"[TTS] Cleaned up temp file after error: {output_path}")
            except:
                pass
                
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'TTS Server',
        'primary_provider': 'OpenAI',
        'fallback_provider': 'FishAudio',
        'voice': OPENAI_VOICE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🎙️ TTS Server starting...")
    print(f"📍 Running on http://localhost:{port}")
    print(f"🔊 Using Edge TTS with voice: {VOICE}")
    print("💡 Ultra-realistic Microsoft Neural Voice")
    app.run(host='0.0.0.0', port=port, debug=False)
