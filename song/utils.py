import mutagen


def calculate_song_duration(file_instance) -> str:
    """
    Return a string format of the duration of a song
    """
    audio = mutagen.File(file_instance)
    audio_length: float = audio.info.length
    hours: int = int(audio_length // 3600)
    minutes: int = int((audio_length - hours * 3600) // 60)
    seconds: float = audio_length - hours * 3600 - minutes * 60

    return f"0{hours}:0{minutes}:{round(seconds)}"
