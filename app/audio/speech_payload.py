from app.schemas.detection import AudioPayload


def build_audio_payload(message: str) -> AudioPayload:
    """Retorna metadados simples para o Flutter reproduzir via TTS."""

    return AudioPayload(text=message, language="pt-BR", mode="tts_client")
