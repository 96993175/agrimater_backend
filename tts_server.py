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
import time

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
