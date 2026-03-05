#!/usr/bin/env python3
"""
Test sound playback to diagnose audio issues.
"""
import sys
import time
sys.path.insert(0, '.')

import pygame

print("Initializing pygame...")
pygame.init()
print(f"Pygame mixer initialized: {pygame.mixer.get_init()}")

from src.ui_pygame.assets.sound_manager import get_sound_manager
from src.core.events import get_event_bus

# Get sound manager
event_bus = get_event_bus()
sm = get_sound_manager(event_bus=event_bus)

print(f"\nSound Manager Status:")
print(f"  Enabled: {sm.enabled}")
print(f"  Sounds directory: {sm.sounds_dir}")
print(f"  Sounds directory exists: {sm.sounds_dir.exists()}")
print(f"  Master volume: {sm.master_volume}")
print(f"  SFX volume: {sm.sfx_volume}")

# List available sound files
import os
sound_files = [f for f in os.listdir(sm.sounds_dir) if f.endswith('.wav')]
print(f"\nFound {len(sound_files)} sound files")
print(f"First few: {sound_files[:5]}")

# Test playing a sound
print("\n" + "="*50)
print("AUDIO TEST - Playing 'menu_select' sound")
print("="*50)
print("\nIf you can hear a beep in the next 2 seconds, audio is working!")
print("Playing...")

# Set volume to maximum for testing
sm.set_master_volume(1.0)
sm.set_sfx_volume(1.0)

# Play the sound
sm.play_sfx('menu_select', volume=1.0)

# Keep the program alive while sound plays
# Need to process pygame events to keep audio playing
print("Waiting for sound to finish...")
for i in range(20):  # 2 seconds at 100ms intervals
    pygame.event.pump()  # Process events to keep audio alive
    time.sleep(0.1)

print("\nTest complete!")
print("\nIf you didn't hear anything:")
print("  1. Check your system volume/audio settings")
print("  2. Make sure speakers/headphones are connected")
print("  3. Check if audio is working in other applications")
print("  4. Try: paplay /usr/share/sounds/alsa/Front_Center.wav")
print(f"  5. Or try playing the file directly: aplay {sm.sounds_dir}/menu_select.wav")

pygame.quit()
