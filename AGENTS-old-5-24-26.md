Project Documentation: Dungeon Closer V3
1. Project Identity & Purpose
A dedicated, localized automation controller for an offsite environment. It manages environmental transitions, audio announcements, and role-based staff authentication with zero reliance on cloud services.

2. Hardware Stack
Controller: Raspberry Pi 5 (8GB).

Storage: MSI GeForce RTX 3060 (Server AI tasks) + High-speed NVMe (Main Boot).

Audio: Audio Injector Zero HAT (I2S).

HMI/Interface: M5Stack Dial (ESP32-S3) via USB-Serial.

Timekeeping: Internal Pi 5 RTC with dedicated battery backup for offline scheduling.

Resilience: "Lifeboat" SD Card with a bootable clone and nightly config snapshots.

3. Software & Environment
OS: Raspberry Pi OS 64-bit Lite (Strict Linux/Ubuntu workflow).

UI Framework: NiceGUI (Pure Python/FastAPI) for local kiosk and remote mobile web.

Audio Engine: PipeWire (WirePlumber) for multi-channel routing and software-based fading.

Development: VSCodium with Remote-SSH and MicroPico extension for MicroPython.

Storage Config: PCIe Gen 3 enabled (dtparam=pciex1_gen=3).

4. System Logic & Automation
The Anchor: All scheduling is calculated as End Time (Start Time + Duration). This prevents "Midnight Crossover" errors.

Triggers: Actions fire at global offsets defined in config.cfg:

-30, -15, -10, -5 mins: Automated warning messages with dynamic $now and $minutes variables.

0 min: Triggers the "Closing Sequence" and plays a defined MP3 playlist in order.

+5 min: Final "Cleanup" message and audio reset.

Persistence: Global mechanics in config.cfg; User/Staff data in users.yaml.

5. Security & Roles
Access Levels: 1.  User: Default kiosk view (Mute/Volume only).
2.  Admin: Schedule management and scene selection.
3.  Superuser: Staff management (RFID/Passwords) and File/Music uploads.

Authentication: Dual-method via hashed web login or physical RFID/NFC tap on the M5Dial.

6. Logging Strategy (Hybrid Rotation)
To protect the NVMe while maintaining audit trails:

Volatile (zram): High-chatter data (M5Dial serial heartbeats, DEBUG logs).

Persistent (NVMe): Critical data (Access logs, ERROR/CRITICAL events).

Rotation: Automated "dumps" from zram to NVMe archives once buffers reach 5MB.

7. Python Module Architecture
main.py: NiceGUI entry point and FastAPI server.

m5_bridge.py: Serial handler for the M5Dial (Encoder/RFID/Buttons).

audio_logic.py: PipeWire/WirePlumber interface for volume and playlist control.

calendar_engine.py: Background task monitoring the schedule and firing offsets.

auth_manager.py: Role-based access control and YAML parser for users.yaml.

Note for Devs: Always interpret "mm" as millimeters. The M5Dial must be flashed with UIFlow 2.0 (MicroPython) via M5Burner before use with the MicroPico extension.
