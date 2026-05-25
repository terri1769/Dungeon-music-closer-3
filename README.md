# Dungeon Closer V3

A dedicated, offline automation controller for managing timed closing announcements at recurring venue events. It progressively warns patrons at configurable intervals before scheduled close time using text-to-speech over the house audio, ducks the music during announcements, and then plays a "clearing" playlist to vacate the space.

Designed to run entirely offline on a Raspberry Pi 5 with zero cloud dependencies.

## Features

- **Timed closing announcements** — configurable TTS messages at -30, -15, -10, -5, 0, and +5 minutes relative to close time
- **Music ducking** — automatically lowers music volume during announcements via PipeWire, then restores it
- **Ambient sound compensation** — MEMS microphone monitors room noise; announcement volume adjusts dynamically with audio subtraction to prevent feedback loops
- **Clearing playlist** — plays intentionally unwanted music after close to encourage patrons to leave
- **Multi-event support** — multiple events per day, each with independent alarm series
- **Early close / cancel** — manual trigger via M5 Dial button with two-action confirmation safety
- **Role-based access control** — three tiers (User, Admin, Owner) with password and NFC authentication
- **Offline-first networking** — Pi runs as a WiFi access point at the venue; staff control the system from their phones
- **Web UI** — NiceGUI serves the same interface to both the local 7" DSI touchscreen and mobile browsers

## Hardware

- Raspberry Pi 5 (4 GB) with NVMe SSD (PCIe Gen 3)
- Audio Injector Zero I2S HAT (line in/out, mic preamp, 24-bit/192 kHz)
- MEMS microphone for ambient sensing (second I2S channel)
- M5Stack Dial (ESP32-S3) — rotary encoder, NFC reader, button, display
- 7" DSI touchscreen
- Pi 5 internal RTC with battery backup

## Software Stack

- **OS:** Raspberry Pi OS 64-bit Lite (Bookworm)
- **UI:** NiceGUI (Python / FastAPI)
- **Audio:** PipeWire + WirePlumber
- **TTS:** Piper TTS (local neural TTS, raw PCM streamed directly to PipeWire)
- **M5 Dial firmware:** MicroPython via UIFlow 2.0

## Project Structure

```
app/
├── main.py              # NiceGUI entry point and FastAPI server
├── audiostuff.py        # Audio control and PipeWire interface
├── make_tts.py          # Piper TTS integration
├── display_stuff.py     # Display management
├── screenInterface.py   # Touchscreen UI
├── webInterface.py      # Web UI
├── set_schedule.py      # Event scheduling
├── set_get_clock.py     # RTC and time management
├── ods_editing.py       # Schedule file editing
├── requirements.txt     # Python dependencies
└── skeleton             # Template/scaffold
config/
├── config.cfg           # Global settings, announcement messages, audio defaults
└── configExample.cfg    # Example configuration
```

## Configuration

`config/config.cfg` defines announcement messages with dynamic variables (`$now`, `$minutes`), audio settings (master volume, fade time, mute behavior), and playlist paths. See `config/configExample.cfg` for a template.

## Deployment

The system runs as native systemd services (not Docker) for direct, low-latency access to audio hardware and peripherals. See `AGENTS.md` for full deployment architecture, service unit definitions, and dependency ordering.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
```

## Version History

| Version | Changes |
|---------|---------|
| v1 | Google Calendar backend; LCD menu and rotary encoder |
| v2 | Complete rewrite; Nextion touchscreen display |
| v2.5 | Local ODS schedule file replaces Google Calendar |
| **v3** | Complete rewrite — Pi 5, NVMe, M5 Dial, NiceGUI, PipeWire, Piper TTS, MEMS ambient sensing, NFC auth, WiFi AP mode, multi-event support |

## Author

Terri Talton — 2025

## License

This project is not currently licensed for redistribution.
