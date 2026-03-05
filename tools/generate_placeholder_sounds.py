#!/usr/bin/env python3
"""
Generate simple placeholder sound effects for Dungeon Crawl.

Creates basic beep/tone sounds for development until proper sound assets are added.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.io import wavfile


def generate_tone(
    frequency: float,
    duration: float,
    sample_rate: int = 44100,
    amplitude: float = 0.3,
) -> np.ndarray:
    """Generate a simple sine wave tone."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    tone = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Apply envelope (fade in/out to avoid clicks)
    fade_samples = int(sample_rate * 0.01)  # 10ms fade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    tone[:fade_samples] *= fade_in
    tone[-fade_samples:] *= fade_out
    
    return tone


def generate_multi_tone(
    frequencies: list[float],
    duration: float,
    sample_rate: int = 44100,
    amplitude: float = 0.3,
) -> np.ndarray:
    """Generate a sound from multiple frequencies mixed together."""
    tones = [generate_tone(f, duration, sample_rate, amplitude / len(frequencies))
             for f in frequencies]
    return np.sum(tones, axis=0)


def generate_noise(
    duration: float,
    sample_rate: int = 44100,
    amplitude: float = 0.2,
) -> np.ndarray:
    """Generate white noise."""
    samples = int(sample_rate * duration)
    noise = amplitude * np.random.uniform(-1, 1, samples)
    
    # Apply envelope
    fade_samples = int(sample_rate * 0.01)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    noise[:fade_samples] *= fade_in
    noise[-fade_samples:] *= fade_out
    
    return noise


def save_sound(filename: Path, audio: np.ndarray, sample_rate: int = 44100):
    """Save audio data to WAV file."""
    # Convert to 16-bit PCM
    audio_int16 = np.int16(audio * 32767)
    wavfile.write(str(filename), sample_rate, audio_int16)
    print(f"Created: {filename.name}")


def generate_all_sounds(output_dir: Path):
    """Generate all placeholder sound effects."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Combat sounds
    save_sound(output_dir / "combat_start.wav",
               generate_multi_tone([440, 550, 660], 0.3))
    
    save_sound(output_dir / "hit.wav",
               generate_tone(300, 0.1))
    
    save_sound(output_dir / "heavy_hit.wav",
               generate_multi_tone([200, 250], 0.15, amplitude=0.4))
    
    save_sound(output_dir / "critical_hit.wav",
               generate_multi_tone([500, 700, 900], 0.2, amplitude=0.5))
    
    save_sound(output_dir / "miss.wav",
               generate_tone(200, 0.08, amplitude=0.2))
    
    save_sound(output_dir / "block.wav",
               generate_tone(350, 0.12))
    
    save_sound(output_dir / "victory.wav",
               generate_multi_tone([523, 659, 784, 1047], 0.5))
    
    save_sound(output_dir / "defeat.wav",
               generate_multi_tone([400, 350, 300, 250], 0.6, amplitude=0.35))
    
    save_sound(output_dir / "flee.wav",
               generate_tone(600, 0.15, amplitude=0.3))
    
    # Spell sounds
    save_sound(output_dir / "spell_cast.wav",
               generate_multi_tone([800, 1000, 1200], 0.25, amplitude=0.3))
    
    save_sound(output_dir / "spell_fire.wav",
               generate_multi_tone([600, 700, 800], 0.3, amplitude=0.35) + 
               generate_noise(0.3, amplitude=0.1))
    
    save_sound(output_dir / "spell_ice.wav",
               generate_multi_tone([1200, 1400], 0.25, amplitude=0.3))
    
    save_sound(output_dir / "spell_lightning.wav",
               generate_noise(0.15, amplitude=0.4))
    
    save_sound(output_dir / "spell_heal.wav",
               generate_multi_tone([880, 1100, 1320], 0.3, amplitude=0.3))
    
    save_sound(output_dir / "spell_buff.wav",
               generate_multi_tone([700, 900, 1100], 0.25))
    
    save_sound(output_dir / "spell_debuff.wav",
               generate_multi_tone([400, 300, 200], 0.25))
    
    # Status effects
    save_sound(output_dir / "poison.wav",
               generate_tone(250, 0.2, amplitude=0.25))
    
    save_sound(output_dir / "stun.wav",
               generate_multi_tone([450, 475], 0.2))
    
    save_sound(output_dir / "burn.wav",
               generate_noise(0.2, amplitude=0.3))
    
    # Character sounds
    save_sound(output_dir / "heal.wav",
               generate_multi_tone([660, 880, 1100], 0.25))
    
    save_sound(output_dir / "level_up.wav",
               generate_multi_tone([523, 659, 784, 1047, 1319], 0.6))
    
    save_sound(output_dir / "player_death.wav",
               generate_multi_tone([440, 400, 350, 300], 0.8, amplitude=0.3))
    
    save_sound(output_dir / "enemy_death.wav",
               generate_multi_tone([350, 300], 0.3))
    
    # UI sounds
    save_sound(output_dir / "menu_select.wav",
               generate_tone(440, 0.05))
    
    save_sound(output_dir / "menu_confirm.wav",
               generate_multi_tone([523, 659], 0.1))
    
    save_sound(output_dir / "menu_cancel.wav",
               generate_tone(330, 0.08))
    
    save_sound(output_dir / "item_pickup.wav",
               generate_multi_tone([660, 880], 0.12))
    
    save_sound(output_dir / "item_equip.wav",
               generate_multi_tone([440, 554, 659], 0.15))
    
    save_sound(output_dir / "coin.wav",
               generate_multi_tone([1100, 1320], 0.1))
    
    save_sound(output_dir / "door_open.wav",
               generate_tone(200, 0.2, amplitude=0.25))
    
    save_sound(output_dir / "chest_open.wav",
               generate_multi_tone([300, 400, 500], 0.25))
    
    print(f"\nGenerated {len(list(output_dir.glob('*.wav')))} placeholder sounds")


def main():
    """Generate placeholder sound effects."""
    parser = argparse.ArgumentParser(
        description="Generate placeholder sound effects for Dungeon Crawl"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="src/ui_pygame/assets/sounds",
        help="Output directory for sound files",
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output)
    
    try:
        generate_all_sounds(output_dir)
        print("\n✅ Placeholder sounds generated successfully!")
        print(f"   Location: {output_dir.absolute()}")
        print("\n⚠️  These are simple placeholder sounds.")
        print("   Replace with proper sound assets for production.")
    except ImportError as e:
        print(f"❌ Error: Missing required package")
        print(f"   {e}")
        print("\nInstall required packages:")
        print("   pip install numpy scipy")
        return 1
    except Exception as e:
        print(f"❌ Error generating sounds: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
