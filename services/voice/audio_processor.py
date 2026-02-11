"""
Audio preprocessing pipeline
Handles noise suppression, VAD, and format conversion
"""
import io
import numpy as np
from pydub import AudioSegment
import noisereduce as nr
import soundfile as sf
from typing import Optional
from shared.config import get_settings
from shared.logging_config import logger

settings = get_settings()


class AudioProcessor:
    """Audio preprocessing for rural CSC environments"""
    
    def __init__(self):
        self.sample_rate = settings.audio_sample_rate
        self.channels = settings.audio_channels
    
    async def preprocess(self, audio_bytes: bytes) -> bytes:
        """
        Complete preprocessing pipeline:
        1. Load audio
        2. Convert to mono if needed
        3. Resample to target rate
        4. Apply noise suppression
        5. Voice activity detection (trim silence)
        
        Args:
            audio_bytes: Raw audio data
        
        Returns:
            Processed WAV bytes
        """
        try:
            # Load audio using pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
                logger.debug("Converted to mono")
            
            # Resample to target rate
            if audio.frame_rate != self.sample_rate:
                audio = audio.set_frame_rate(self.sample_rate)
                logger.debug(f"Resampled to {self.sample_rate}Hz")
            
            # Convert to numpy array for processing
            samples = np.array(audio.get_array_of_samples()).astype(np.float32)
            samples = samples / (2**15)  # Normalize to [-1, 1]
            
            # Apply noise suppression if enabled
            if settings.enable_noise_suppression:
                samples = await self._reduce_noise(samples)
            
            # Voice activity detection (trim silence)
            samples = await self._trim_silence(samples)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            sf.write(
                output_buffer,
                samples,
                self.sample_rate,
                format='WAV',
                subtype='PCM_16'
            )
            output_buffer.seek(0)
            
            logger.info(
                "Audio preprocessing complete",
                duration_sec=len(samples) / self.sample_rate
            )
            
            return output_buffer.read()
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {str(e)}")
            # Return original audio if preprocessing fails
            return audio_bytes
    
    async def _reduce_noise(self, samples: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction using spectral gating
        Effective for fan noise, traffic, etc.
        """
        try:
            # Use noisereduce library
            reduced = nr.reduce_noise(
                y=samples,
                sr=self.sample_rate,
                stationary=True,  # Assume stationary noise (fan, AC)
                prop_decrease=0.8
            )
            logger.debug("Noise reduction applied")
            return reduced
        except Exception as e:
            logger.warning(f"Noise reduction failed: {str(e)}")
            return samples
    
    async def _trim_silence(self, samples: np.ndarray) -> np.ndarray:
        """
        Trim leading and trailing silence using energy-based VAD
        """
        try:
            # Calculate frame energy
            frame_length = int(0.025 * self.sample_rate)  # 25ms frames
            hop_length = int(0.010 * self.sample_rate)    # 10ms hop
            
            # Simple energy-based VAD
            energy = np.array([
                np.sum(samples[i:i+frame_length]**2)
                for i in range(0, len(samples) - frame_length, hop_length)
            ])
            
            # Threshold
            threshold = np.mean(energy) * settings.vad_threshold
            
            # Find speech boundaries
            speech_frames = energy > threshold
            if not np.any(speech_frames):
                # No speech detected, return original
                return samples
            
            start_frame = np.argmax(speech_frames)
            end_frame = len(speech_frames) - np.argmax(speech_frames[::-1])
            
            # Convert frame indices to sample indices
            start_sample = start_frame * hop_length
            end_sample = min(end_frame * hop_length + frame_length, len(samples))
            
            trimmed = samples[start_sample:end_sample]
            
            logger.debug(
                "Silence trimmed",
                original_duration=len(samples) / self.sample_rate,
                trimmed_duration=len(trimmed) / self.sample_rate
            )
            
            return trimmed
            
        except Exception as e:
            logger.warning(f"VAD trimming failed: {str(e)}")
            return samples
