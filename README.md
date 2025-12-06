# Agrimater TTS Backend

Flask-based Text-to-Speech server using OpenAI TTS.

## Features
- OpenAI TTS with "nova" voice (natural, friendly female voice)
- REST API endpoint for text-to-speech conversion
- CORS enabled for frontend integration
- Production-ready for Render deployment

## Endpoints
- `GET /` - Service information
- `GET /health` - Health check
- `POST /api/tts` - Text-to-Speech conversion

## Local Development

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_api_key_here
python tts_server.py
```

Server runs on http://localhost:5001

## Test TTS Endpoint

```bash
curl -X POST http://localhost:5001/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Agrimater"}' \
  --output test.mp3
```

## Deployment to Render

1. Push this backend folder to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` configuration
5. Service deploys automatically
6. Add `OPENAI_API_KEY` environment variable in Render dashboard

Health check: `https://your-app.onrender.com/health`

## Dependencies
- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - CORS support
- openai 1.58.1 - OpenAI TTS API

## Environment Variables
- `PORT` - Server port (default: 5001)
- `OPENAI_API_KEY` - Your OpenAI API key (required)
