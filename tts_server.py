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
import nest_asyncio

# Allow nested event loops (fixes issues in production environments)
nest_asyncio.apply()

app = Flask(__name__)
CORS(app)

# Use Microsoft's en-IN (Indian English) neural voice for "Namaskar" greeting
# Options: en-IN-NeerjaNeural (Female), en-IN-PrabhatNeural (Male)
VOICE = "en-IN-NeerjaNeural"  # Natural Indian English female voice

async def generate_speech_async(text: str, output_path: str):
    """Generate speech using Edge TTS"""
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
        print(f"TTS generated successfully for text: {text[:30]}...")
    except Exception as e:
        print(f"Error in generate_speech_async: {str(e)}")
        raise

def generate_speech(text: str, output_path: str):
    """Sync wrapper for generate_speech_async"""
    try:
        # Use asyncio.run which handles event loop creation/cleanup
        asyncio.run(generate_speech_async(text, output_path))
    except RuntimeError as e:
        # Fallback for environments with existing event loops
        print(f"RuntimeError, trying alternative approach: {e}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(generate_speech_async(text, output_path))
        finally:
            loop.close()
    except Exception as e:
        print(f"Error generating speech: {e}")
        raise

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API info"""
    return jsonify({
        'service': 'Agrimater TTS Server',
        'status': 'running',
        'voice': VOICE,
        'endpoints': {
            'health': '/health',
            'tts': '/api/tts (POST)'
        }
    })

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    output_path = None
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        print(f"Generating TTS for: {text[:50]}...")  # Log for debugging
        
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_path = temp_file.name
        temp_file.close()
        
        # Generate speech
        generate_speech(text, output_path)
        
        # Verify file was created
        if not os.path.exists(output_path):
            return jsonify({"error": "Failed to generate audio"}), 500
        
        print(f"Audio generated successfully: {output_path}")
        
        # Send the audio file and clean up after
        response = send_file(
            output_path,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )
        
        # Schedule cleanup
        @response.call_on_close
        def cleanup():
            try:
                if output_path and os.path.exists(output_path):
                    os.unlink(output_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error in TTS endpoint: {str(e)}")
        # Cleanup on error
        if output_path and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except:
                pass
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'TTS Server',
        'tts': 'edge-tts',
        'voice': VOICE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🎙️ TTS Server starting...")
    print(f"📍 Running on http://localhost:{port}")
    print(f"🔊 Using Edge TTS with voice: {VOICE}")
    print("💡 Ultra-realistic Microsoft Neural Voice")
    app.run(host='0.0.0.0', port=port, debug=False)
