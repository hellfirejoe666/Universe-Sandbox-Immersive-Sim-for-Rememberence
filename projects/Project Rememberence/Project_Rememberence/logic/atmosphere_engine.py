import random
import json
import os

class AtmosphereEngine:
    """
    Senses and triggers environmental audio/visual cues based on 
    the current world state and narrative tension.
    """
    def __init__(self, audio_root=r'D:\GPT4All\AIPlus\KARI2\DDLC\custom_bgm', suno_root=r'D:\Cards\Albums'):
        self.audio_root = audio_root
        self.suno_root = suno_root
        self.current_mood = "Neutral"
        
        # Mapping moods to folders/artists
        self.mood_map = {
            "Tension": "Tech N9ne",
            "Melancholy": "UNDERTALE Soundtrack",
            "Chaos": "Taking Back Sunday",
            "Ethereal": "Three Days Grace",
            "Resilience": "Stevie Ray Vaughan and Double Trouble",
            "Divine": "Gnosis",
            "Awakening": "Embryo",
            "Void": "HallowGram"
        }
        
        # Direct song mappings for key game events
        self.event_tracks = {
            "combat_start": "Battle For Souls (Remix).mp3",
            "critical_failure": "Broken Silence (Remix).mp3",
            "divine_intervention": "Divine Spark.mp3",
            "world_shift": "Through the Looking Glass (Remix).mp3",
            "death_echo": "Echoes in the Mirror.mp3"
        }

    def update_mood(self, state_value):
        """
        Adjusts the world mood based on the aggregate state of the Weave.
        state_value: The sum of thoughts/stability.
        """
        if state_value > 50: self.current_mood = "Resilience"
        elif state_value > 10: self.current_mood = "Ethereal"
        elif state_value < -50: self.current_mood = "Chaos"
        elif state_value < -10: self.current_mood = "Tension"
        else: self.current_mood = "Melancholy"
        
        return self.current_mood

    def get_audio_cue(self):
        """Returns a suggested audio track/artist to match the current mood."""
        artist = self.mood_map.get(self.current_mood, "UNDERTALE Soundtrack")
        # In a full implementation, this would pick a random file from the identified directories
        return f"🎵 Audio Layer Shift: Now playing {artist} - Mood: {self.current_mood}"

oracle_audio = AtmosphereEngine()
