"""
TTS API Server using Edge TTS (Microsoft Neural Voices)
Run this separately: python tts_server.py
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
import edge_tts
import asyncio

app = Flask(__name__)
CORS(app)

# Use Microsoft's en-IN (Indian English) neural voice for "Namaskar" greeting
# Options: en-IN-NeerjaNeural (Female), en-IN-PrabhatNeural (Male)
VOICE = "en-IN-NeerjaNeural"  # Natural Indian English female voice

async def generate_speech_async(text: str, output_path: str):
    """Generate speech using Edge TTS"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)

def generate_speech(text: str, output_path: str):
    """Sync wrapper for generate_speech_async"""
    asyncio.run(generate_speech_async(text, output_path))

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_path = temp_file.name
        temp_file.close()
        
        # Generate speech
        generate_speech(text, output_path)
        
        # Verify file was created
        if not os.path.exists(output_path):
            return jsonify({"error": "Failed to generate audio"}), 500
        
        # Send the audio file
        return send_file(
            output_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'tts': 'edge-tts', 'voice': VOICE})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🎙️ TTS Server starting...")
    print(f"📍 Running on http://localhost:{port}")
    print(f"🔊 Using Edge TTS with voice: {VOICE}")
    print("💡 Ultra-realistic Microsoft Neural Voice")
    app.run(host='0.0.0.0', port=port, debug=False)
