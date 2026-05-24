PROJECT: DUNGEON CLOSER V3
Version: 3.2.0 (Pi 5 + Pico 2 + Anvil Web Kiosk)

Audio Engine: Piper TTS (Offline-Only) + WM8960 Hardware Mixer

Status: Hardware Finalized / Software Architecture Phase

1. HARDWARE ARCHITECTURE
Core Compute & Audio
Main Controller: Raspberry Pi 5 (4GB).

Storage: 256GB NVMe SSD (Samsung PM9B1) via Bottom-mounted X1002 HAT.

Note: Enabled PCIe Gen 3 for "Fast Boot" (~12s boot time).

Cooling: Official Pi 5 Active Cooler.

Audio Interface: Waveshare WM8960 Audio HAT.

Inputs: Integrated Stereo MEMS Mics (Ambience) + 3.5mm Stereo Line-In (Aux).

Outputs: 3.5mm Stereo Out -> External PA Amp.

Timekeeping: Internal Pi 5 RTC + CR2032 Battery.

I/O & Peripheral Bridge (The Hardware Hub)
IO Controller: Raspberry Pi Pico 2 (MicroPython).

Responsibility: * Volume Knob: High-precision interrupts for the Rotary Encoder.

NFC Reader: MFRC522 polling (Gated Access).

Visuals: WS2812B (Neopixel) Ring management (Lag-free hardware timing).

Connection: USB-Serial to Pi 5.

Connectivity & Networking
Wireless: Internal Pi 5 Wi-Fi (5GHz Priority) & Bluetooth 5.0.

Strategy: No USB dongles needed (RP1 chip isolates I/O noise).

Identity: Bluetooth advertised as "Scrappy's Dungeon V3".

AP Mode: Secured Hotspot activates only if Shop Wi-Fi is unavailable (Local Dev Mode).

2. HARDWARE HUB WIRING (PICO 2)
NFC (MFRC522 SPI): SCK=GP2, MOSI=GP3, MISO=GP4, RST=GP5, SDA=GP1.

NEOPIXEL RING: GP6 (Data Line).

ROTARY ENCODER: A=GP7, B=GP8, SW=GP9 (Mute).

STATUS LED: GP25 (Onboard) pulses during active NFC scan.

3. MECHANICAL & ENCLOSURE
Enclosure: Apache 2800 Case
Display: 7" DSI Capacitive Touchscreen (Native Pi 5 DSI-to-Mini cable).

Layout: * Main Face: 7" Screen (Kiosk Mode) + Single Large Volume Knob (right of screen).

Side Port: USB-C Power (100W PD + Decoy Trigger), 3.5mm Aux-In, 3.5mm Line-Out.

NFC Target: Internal mount against sidewall; external "TAP HERE" sticker.

4. SOFTWARE LOGIC (THE "V3" STACK)
Access Levels (Anvil Data Tables + NFC)
Guest (Kiosk Only): View Dashboard, Basic Volume Knob, Progress Bar.

Admin (NFC): Access "Mixer" page (Aux/BT/TTS individual sliders), Upload schedule.csv.

Superuser (NFC/Web): Edit User DB (YAML), Terminal Access, Change Voice Models, Full System Config.

Security Strategy
Local: Auto-login via localhost (127.0.0.1) detection + Secret Header.

Remote: Forced Password Login for all non-local IP addresses.

Audio Sequence (The Closing Routine)
Adaptive Leveling: 5-second rolling average of MEMS Mic input to auto-scale PA Output.

Phase 1 (Warning): Music Duck (I2C Mixer Command) -> Piper TTS -> Music Ramp Up.

Phase 2 (Close): Music Total Duck -> Final Piper Announcement -> Trigger "Canned Music" from NVMe Cache.

Cancel Logic: * In Session: "End Session" -> Triggers Closing Sequence immediately.

In Closing: "Abort" -> Cancels all announcements; returns to Wait State.

5. UI & DESIGN (Anvil Web Kiosk)
Dashboard: Home page features a circular Progress Bar (Green -> Red gradient).

Kiosk Mode: Pi 5 boots to Chromium (Headless) targeting localhost:5000.

Music Cache: NVMe-based rolling 24-hour buffer of Bluetooth stream (Superuser access only).

Test Button: "Voice Check" button in Admin UI to trigger a dummy announcement & level check.

6. IMPLEMENTATION NOTES
Main Language: Python 3 (Pi 5) / MicroPython (Pico 2).

Database: users.yaml + schedule.yaml (Human-readable/Editable).

Logs: access_log.csv (Timestamp | User | NFC/Web | Action).

Comm: JSON-based serial protocol between Pi 5 and Pico 2.

Major Changes from V2 -> V3:
Ditched external USB dongles: Pi 5's internal RF is sufficient.

Swapped PyQt6 for Anvil: Provides a unified local/remote web-based interface.

Added Piper TTS: Replaced robotic TTS with human-sounding neural speech.

Bottom-Mount NVMe: Moved OS to SSD for reliability and high-speed voice model loading.

Hardware Hub: Dedicated Pico 2 for the Volume Knob to ensure zero-latency interrupts.
