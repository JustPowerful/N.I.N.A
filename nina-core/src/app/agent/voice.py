from openai import OpenAI
from app.config import settings

# created eagerly to avoid creating a new client for each request, which can be inefficient
client = OpenAI(
            api_key=settings.edge_tts_api_key,
            base_url=settings.edge_tts_base_url
        )

class VoiceClient:
    async def generate_tts(self, text: str, voice: str = "en-US-JennyNeural", format: str = "mp3"):
        try:
            response = client.audio.speech.with_streaming_response.create(
                        model="tts-1",
                        voice=voice,
                        input=text
                    )
            
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to generate TTS: {e}")

def get_voice_client() -> VoiceClient:
    return VoiceClient()