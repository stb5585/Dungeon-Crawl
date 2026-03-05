#!/usr/bin/env python3
"""
Sound System Diagnostic Tool
Checks common audio issues and provides troubleshooting steps.
"""
import sys
import os
import subprocess
sys.path.insert(0, '.')

print("="*60)
print("DUNGEON CRAWL - SOUND DIAGNOSTIC TOOL")
print("="*60)

# Check 1: System audio configuration
print("\n[1] Checking system audio...")
try:
    # Check if pulseaudio is running
    result = subprocess.run(['pulseaudio', '--check'], capture_output=True)
    if result.returncode == 0:
        print("  ✓ PulseAudio is running")
    else:
        print("  ✗ PulseAudio is not running")
        print("    Try: pulseaudio --start")
except FileNotFoundError:
    print("  ? PulseAudio not found (may be using ALSA instead)")

# Check 2: Test system audio with a simple command
print("\n[2] Testing system audio capability...")
test_sound = "/usr/share/sounds/alsa/Front_Center.wav"
if os.path.exists(test_sound):
    print(f"  Found test sound: {test_sound}")
    print("  Attempting to play test sound...")
    try:
        result = subprocess.run(['aplay', test_sound], capture_output=True, timeout=3)
        if result.returncode == 0:
            print("  ✓ System audio works! (You should have heard a test sound)")
        else:
            print(f"  ✗ aplay failed: {result.stderr.decode()}")
    except FileNotFoundError:
        print("  ✗ 'aplay' command not found")
    except subprocess.TimeoutExpired:
        print("  ⏱ aplay timed out (but might have played)")
else:
    print("  ? No system test sound found")

# Check 3: Test our generated sounds
print("\n[3] Testing Dungeon Crawl sound files...")
sound_file = "src/ui_pygame/assets/sounds/menu_select.wav"
if os.path.exists(sound_file):
    print(f"  Found: {sound_file}")
    size = os.path.getsize(sound_file)
    print(f"  Size: {size} bytes")
    if size < 100:
        print("  ⚠ File is suspiciously small!")
    
    print("  Attempting to play with aplay...")
    try:
        result = subprocess.run(['aplay', sound_file], capture_output=True, timeout=2)
        if result.returncode == 0:
            print("  ✓ File played successfully!")
            print("    >> Did you hear a beep? If yes, Pygame mixer might be the issue.")
            print("    >> If no, your system audio might be muted/disconnected.")
        else:
            print(f"  ✗ aplay error: {result.stderr.decode()}")
    except FileNotFoundError:
        print("  ⚠ 'aplay' not available, trying paplay...")
        try:
            result = subprocess.run(['paplay', sound_file], capture_output=True, timeout=2)
            if result.returncode == 0:
                print("  ✓ File played with paplay!")
        except:
            print("  ✗ Could not play file")
    except subprocess.TimeoutExpired:
        print("  ⏱ Playback timed out")
else:
    print(f"  ✗ Sound file not found: {sound_file}")
    print("    Run: python3 tools/generate_placeholder_sounds.py")

# Check 4: Pygame audio test
print("\n[4] Testing Pygame mixer...")
try:
    import pygame
    pygame.init()
    mixer_info = pygame.mixer.get_init()
    if mixer_info:
        print(f"  ✓ Pygame mixer initialized: {mixer_info}")
        print(f"    Frequency: {mixer_info[0]} Hz")
        print(f"    Channels: {mixer_info[2]} (stereo)")
        
        # Try loading and playing a sound
        if os.path.exists(sound_file):
            print("  Loading sound into pygame...")
            sound = pygame.mixer.Sound(sound_file)
            print(f"  ✓ Sound loaded, length: {sound.get_length():.2f}s")
            print("  Playing sound with pygame...")
            sound.set_volume(1.0)
            channel = sound.play()
            if channel:
                print("  ✓ Sound playing on channel", channel)
                print("    >> Listening for 2 seconds...")
                import time
                time.sleep(2)
                print("    >> Did you hear it?")
            else:
                print("  ✗ Failed to play sound (no channel available)")
        
        pygame.quit()
    else:
        print("  ✗ Pygame mixer failed to initialize")
except Exception as e:
    print(f"  ✗ Pygame error: {e}")

# Check 5: Environment variables
print("\n[5] Checking audio environment...")
audio_vars = ['SDL_AUDIODRIVER', 'AUDIODEV', 'AUDIODRIVER']
for var in audio_vars:
    value = os.environ.get(var)
    if value:
        print(f"  {var} = {value}")
    else:
        print(f"  {var} = (not set)")

# Summary and recommendations
print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)
print("""
1. If aplay/paplay worked but pygame didn't:
   - This is a pygame/SDL audio driver issue
   - Try setting: export SDL_AUDIODRIVER=alsa
   - Or try: export SDL_AUDIODRIVER=pulseaudio
   
2. If nothing played audio:
   - Check system volume: alsamixer or pavucontrol
   - Verify audio device: aplay -l
   - Check if speakers/headphones are plugged in
   
3. If you're on SSH/remote session:
   - Audio may not be forwarded
   - Try running locally on the machine
   
4. Check game integration:
   - Run the game and press arrow keys in menus
   - Each key press should trigger menu_select.wav
   - Watch for errors in terminal output
""")

print("\n" + "="*60)
