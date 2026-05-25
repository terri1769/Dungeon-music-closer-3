# Project Documentation: Dungeon Closer V3

---

## 1. Project Identity & Purpose

A dedicated, localized automation controller for an offsite BDSM dungeon environment. It manages timed closing announcements, music ducking, ambient volume compensation, and role-based staff authentication with zero reliance on cloud services. The system progressively warns patrons at configurable intervals before scheduled close time, then plays an unwanted "clearing" playlist to vacate the space. Multiple events per day are supported.

---

## 2. Hardware Stack

| Component | Specification | Notes |
|---|---|---|
| Controller | Raspberry Pi 5 (4GB) | PCIe Gen 3 enabled: `dtparam=pciex1_gen=3` |
| Storage | NVMe SSD (PCIe) | Main OS boot drive |
| Audio HAT | Audio Injector Zero (PPI0) | I2S HAT; stereo line in/out; mic preamp; 24-bit/192kHz |
| HMI | M5Stack Dial (ESP32-S3) | USB-Serial connection; rotary encoder + button + display + NFC reader |
| Display | DSI 7" Touchscreen | Uses DSI ribbon cable; leaves full 40-pin GPIO header available |
| Ambient Sensing | MEMS Microphone | Second I2S channel on Audio Injector; used for real-time ambient level monitoring and audio subtraction |
| Timekeeping | Pi 5 internal RTC + battery backup | Offline scheduling; NTP sync when internet is available |
| Resilience | "Lifeboat" SD card | Bootable clone with nightly config snapshots |

**Audio sources supported:**
- Line in (aux) via Audio Injector Zero
- Bluetooth (A2DP sink)
- USB thumb drive (local playback)
- Downloaded Spotify (offline clearing playlist)

---

## 3. Software & Environment

| Layer | Technology | Notes |
|---|---|---|
| OS | Raspberry Pi OS 64-bit Lite (Bookworm) | Headless base; Wayland display server |
| UI Framework | NiceGUI (Pure Python / FastAPI) | Serves both local touchscreen kiosk and remote mobile web UI |
| Audio Engine | PipeWire + WirePlumber | Multi-channel routing; software fading; Bluetooth A2DP sink |
| TTS Engine | Piper TTS | Local neural TTS; streams raw audio directly to PipeWire — no WAV file written |
| M5 Dial Firmware | MicroPython via UIFlow 2.0 | Flashed with M5Burner before use |
| Development | VSCodium + Remote-SSH + MicroPico extension | MicroPico handles M5 Dial MicroPython workflow |
| Config Storage | PCIe Gen 3 | `dtparam=pciex1_gen=3` in boot config |

**Logging Strategy (Hybrid Rotation):**
- **Volatile (zram):** High-chatter data — M5 Dial serial heartbeats, DEBUG-level logs
- **Persistent (NVMe):** Critical data — access logs, ERROR/CRITICAL events
- **Rotation:** Automated dumps from zram to NVMe archives when buffers reach 5MB

---

## 4. Networking

The system is designed for **offline operation** during events. No internet is available at the venue.

- **During development:** SSH access enabled
- **During operation:** Pi becomes a **standalone WiFi Access Point**
- **AP behavior:** If a known WiFi network is not found within ~30 seconds, the Pi switches to AP mode automatically (via RaspAP or a systemd script)
- **Mobile control:** Staff connects their phone to the Pi's AP and accesses the NiceGUI web interface via browser
- **Same interface** serves both the local DSI touchscreen and the mobile web client

---

## 5. System Logic & Automation

### The Anchor Rule
All scheduling is calculated as **End Time = Start Time + Duration**. This prevents "Midnight Crossover" errors. The system supports multiple events per day; each event has its own independent alarm series identified by event ID.

### Closing Sequence Triggers
Configurable time offsets are defined globally in `config.cfg`. Default offsets:

| Offset | Action |
|---|---|
| -30 min | TTS announcement; music ducks then restores |
| -15 min | TTS announcement; music ducks then restores |
| -10 min | TTS announcement; music ducks then restores |
| -5 min | TTS announcement; music ducks then restores |
| 0 min (Close) | TTS announcement; music ducks; clearing playlist begins |
| +5 min | Final "Cleanup" TTS message; audio reset |

Announcement messages support dynamic variables: `$now`, `$minutes`.

### Ambient Sound Compensation
The MEMS microphone on the second I2S channel monitors real-time ambient sound levels. The outgoing audio signal is subtracted from the ambient reading to prevent hysteresis feedback loops (where increasing volume causes the system to increase volume further). TTS announcement volume and music ducking depth are adjusted dynamically based on the compensated ambient level. A baseline noise profile is captured at system startup.

### Music Ducking
Handled by PipeWire/WirePlumber via per-node volume control. Music is ducked to **complete silence (zero)** on every announcement — duck depth is always zero, no exceptions. The pre-duck volume level is saved and fully restored after the announcement completes.

1. Save current music node volume
2. Ramp music node to zero
3. Piper TTS audio plays
4. Restore music node to saved volume level

### Ambient Sound Compensation (Separate from Ducking)
The MEMS microphone is used for **live music volume adjustment during normal playback** — not for controlling duck depth. Duck depth is always zero regardless of ambient conditions. The ambient sensing system monitors room noise levels in real time, subtracts the known outgoing audio signal to prevent feedback loops, and adjusts the music playback volume up or down to maintain consistent perceived loudness as the crowd noise changes throughout an event. A baseline noise profile is captured at system startup.

### Early Close / Cancel Toggle
- A configurable time window before close allows manual trigger of the closing sequence
- **Trigger method:** M5 Dial physical button press
- **Confirmation required:** GUI confirmation dialog must be acknowledged before the sequence executes (two-action safety — prevents accidental triggers)
- **Cancel method:** If the closing sequence is already running, the same button press + GUI confirmation cancels the entire active alarm series for that event only (does not affect other scheduled events)

---

## 6. Security & Access Control

### Access Levels

| Level | Name | Capabilities |
|---|---|---|
| 1 | User | Default kiosk view; mute/unmute music; adjust music volume |
| 2 | Admin | All User capabilities + TTS volume control + schedule editing + scene selection |
| 3 | Owner (Superuser) | All Admin capabilities + user/staff management + RFID/NFC credential management + file/music uploads |

### Authentication Methods
- **Web interface:** Hashed password login
- **M5 Dial (physical):** NFC/RFID card tap — Admin and Owner staff are issued NFC cards
- NFC card UIDs stored in `users.yaml`; matched against whitelist

---

## 7. Configuration Files

| File | Purpose |
|---|---|
| `config.cfg` | Global settings: time offsets, announcement messages, playlist paths, audio defaults |
| `schedule.yaml` | Event schedule: event names, start times, durations, per-event overrides |
| `users.yaml` | Staff credentials: hashed passwords, NFC UIDs, access levels |

All files are human-readable YAML/INI. The NiceGUI web interface provides forms for editing `schedule.yaml` and `users.yaml` without manual file editing.

---

## 8. Python Module Architecture

| Module | Responsibility |
|---|---|
| `main.py` | NiceGUI entry point; FastAPI server; AP mode detection and startup |
| `m5_bridge.py` | Serial handler for M5 Dial (encoder input, NFC reads, button events, display output) |
| `audio_logic.py` | PipeWire/WirePlumber interface: volume control, music ducking, playlist management, Piper TTS streaming, ambient level processing |
| `calendar_engine.py` | Background task: loads `schedule.yaml`, monitors time, fires offset triggers, manages per-event alarm series, handles early close/cancel |
| `auth_manager.py` | Role-based access control; parses `users.yaml`; validates passwords and NFC UIDs |
| `network_manager.py` | WiFi detection; AP mode switching; NiceGUI serves same UI to touchscreen and mobile clients |
| `log_manager.py` | Hybrid zram/NVMe logging; rotation logic; access audit trail; debug logging |

---

## 9. M5 Dial (ESP32-S3) Responsibilities

- **Rotary encoder:** Primary volume control for house music
- **Display:** Countdown timer to next closing alarm; current volume level ring indicator
- **NFC reader:** Admin/Owner authentication via card tap
- **Button:** Early close trigger (requires GUI confirmation) / closing sequence cancel (requires GUI confirmation)
- **Communication:** USB-Serial to Pi; MicroPython firmware via UIFlow 2.0

---

## 10. Piper TTS — Voice Announcement Pipeline

### Overview
Piper TTS is a local neural text-to-speech engine optimized for ARM hardware. It runs entirely offline, produces natural-sounding speech, and streams raw PCM audio directly into PipeWire without writing any intermediate files. This eliminates SD card / NVMe wear and minimizes announcement latency.

### Installation
```bash
# Install Piper via pip (recommended for Pi OS Bookworm)
pip3 install piper-tts --break-system-packages

# Download a voice model — use medium quality for best balance on Pi 5
mkdir -p ~/piper/models
cd ~/piper/models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

Other available voices are listed at: https://huggingface.co/rhasspy/piper-voices

### Streaming Pipeline (No WAV Files)
Piper outputs raw 16-bit PCM audio via `--output-raw`. This is piped directly to `aplay` (or a PipeWire virtual sink) without touching disk:

```bash
echo "The dungeon closes in 30 minutes." \
  | piper --model ~/piper/models/en_US-lessac-medium.onnx --output-raw \
  | aplay -r 22050 -f S16_LE -t raw -
```

### Python Integration in `audio_logic.py`
Piper should be launched as a **persistent subprocess** so the model is pre-loaded and ready. This eliminates the cold-start delay on each announcement.

```python
import subprocess

class PiperTTS:
    def __init__(self, model_path: str):
        # Launch Piper once; keep stdin open for repeated use
        self._piper = subprocess.Popen(
            ['piper', '--model', model_path, '--output-raw'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        # aplay reads from Piper's stdout
        self._player = subprocess.Popen(
            ['aplay', '-r', '22050', '-f', 'S16_LE', '-t', 'raw', '-'],
            stdin=self._piper.stdout,
        )

    def speak(self, text: str):
        """Send text to the running Piper process. Non-blocking write."""
        self._piper.stdin.write((text.strip() + '\n').encode())
        self._piper.stdin.flush()

    def shutdown(self):
        self._piper.stdin.close()
        self._piper.wait()
        self._player.wait()
```

### Integration with Music Ducking
The `calendar_engine.py` announcement trigger calls into `audio_logic.py` using the following sequence:

1. Resolve the announcement text — substitute `$minutes` and `$now` variables
2. Save current music node volume
3. Call `duck_music()` to ramp the PipeWire music node to **zero**
4. Call `tts.speak(resolved_text)` — audio streams immediately
5. Wait for Piper output to complete (monitor subprocess or use a timed estimate)
6. Call `restore_music()` to ramp music back to the saved pre-duck volume level

Duck depth is always zero. The ambient sensing system operates independently and handles live volume adjustment during normal playback — it does not influence ducking behavior.

### Message Template Resolution
Announcement message templates are stored in `config.cfg`. Example:

```ini
msg_30 = Attention. The dungeon will be closing in $minutes minutes.
msg_0  = The dungeon is now closed. Please make your way to the exit.
```

Resolution is handled in `calendar_engine.py` before passing to `tts.speak()`:

```python
def resolve_message(template: str, minutes: int) -> str:
    now_str = datetime.now().strftime('%I:%M %p')
    return template.replace('$minutes', str(minutes)).replace('$now', now_str)
```

### Voice Model Notes
- **Recommended model:** `en_US-lessac-medium` — good quality, reasonable inference speed on Pi 5
- **Faster option:** `en_US-lessac-low` — use if latency becomes an issue
- Model files (`.onnx` + `.onnx.json`) must be present on the NVMe at the path configured in `config.cfg`
- Model path key in config: `piper_model_path`

---

## 12. Developer Notes

- M5 Dial **must** be flashed with UIFlow 2.0 (MicroPython) via M5Burner before use with the MicroPico extension
- Use `snake_case` for all Python function and variable names
- Use `snake_case` for all Python module filenames
- Piper TTS must stream raw audio output directly to PipeWire — do **not** write intermediate WAV files
- Audio subtraction logic for ambient sensing is new in v3; v2/v2.5 used static ducking only
- Resource limits for any containerized services follow the `deploy` key pattern used in Komodo Stacks

---

## 11. Version History

| Version | Key Changes |
|---|---|
| v1 | Google Calendar backend; LCD menu and single rotary encoder |
| v2 | Google Calendar backend; Complete rewrite; Used touch-screen Nextion display instead of LCD |
| v2.5 | Google Calendar replaced with local ODS schedule file; |
| **v3 (current)** | Complete rewrite; Pi 5; NVMe; M5 Dial for music volume; NiceGUI web UI; PipeWire audio; Piper TTS; YAML config; MEMS ambient sensing with audio subtraction; NFC auth; WiFi AP mode; multi-event support; early close/cancel with dual confirmation |
