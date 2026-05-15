#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pieeg_lsl_streamer.py
=====================
Runs on the Raspberry Pi 5.

Reads 16-channel EEG data from the PiEEG board (two ADS1299 chips) via SPI
and broadcasts it as a Lab Streaming Layer (LSL) stream on the local network.

The MacBook Air M1 running DB-BMI.py will auto-discover and receive this stream.

Requirements (Pi side):
    pip install spidev gpiozero pylsl

Usage:
    python3 pieeg_lsl_streamer.py

Leave this running before launching DB-BMI.py on the Mac.
Press Ctrl+C to stop.
"""

import time
import signal
import sys

import spidev
from gpiozero import DigitalInputDevice
from pylsl import StreamInfo, StreamOutlet, local_clock

# ============================================================
# --- Configuration — must match DB-BMI.py on the Mac ---
# ============================================================
STREAM_NAME    = "PiEEG"       # LSL stream name (DB-BMI.py resolves by this)
STREAM_TYPE    = "EEG"
N_CHANNELS     = 16
SAMPLE_RATE    = 250           # Hz — ADS1299 default data rate (250 SPS)
CHANNEL_FORMAT = "float32"     # µV values fit comfortably in float32
SOURCE_ID      = "PiEEG_16ch"  # Unique identifier for this source

# ============================================================
# --- PiEEG Hardware Constants ---
# ============================================================
DRDY_PIN      = 24             # BCM GPIO pin for DRDY — try 17 or 25 if DRDY never fires
VREF          = 4.5            # ADS1299 reference voltage (V)
GAIN          = 24             # PGA gain setting
# Daisy-chain frame layout (54 bytes total):
#   [0–2]   Chip 1 status bytes
#   [3–26]  Chip 1 data: 8 channels × 3 bytes  (Ch 1–8)
#   [27–29] Chip 2 status bytes  ← must be SKIPPED during decode
#   [30–53] Chip 2 data: 8 channels × 3 bytes  (Ch 9–16)
BYTES_PER_SAMPLE = 54

# ============================================================
# --- GPIO & SPI Setup ---
# ============================================================
print("[PiEEG-LSL] Initialising GPIO and SPI...")

drdy = DigitalInputDevice(DRDY_PIN, pull_up=True)  # active_state inferred as False from pull_up=True

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000   # 1 MHz — more reliable than 2 MHz during init
spi.mode = 0b01

# --- ADS1299 Initialisation sequence ---
spi.xfer2([0x06])                                            # RESET
time.sleep(0.5)                                              # extended settle — was 0.1
spi.xfer2([0x11])                                            # SDATAC (stop continuous read)
time.sleep(0.2)                                              # extended settle — was 0.1
spi.xfer2([0x43, 0x00, 0xE0])                               # CONFIG3: enable internal reference
time.sleep(0.01)

# Configure GAIN=24 on both ADS1299 chips (8 channels each).
# Chip 1: channels 1–8  (register 0x05, 8 bytes)
spi.xfer2([0x45, 0x07, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x60])
time.sleep(0.01)

# Chip 2: channels 9–16 (same register set on second chip via daisy-chain)
# PiEEG 16-ch boards daisy-chain the second ADS1299 — the same SPI transaction
# reaches it automatically after the first chip's 8 bytes.  The xfer2 above
# already covers all 16 channels if the board is in daisy-chain mode.
# If your board requires a separate CS line, add spi.open(0, 1) config here.

# FIX: START command — tells the ADS1299 to begin continuous conversions.
# Without this, RDATAC puts the chip in continuous read mode but the ADC
# never actually converts, so every read returns 0x00 bytes → 0.0 µV.
# START command (0x08) is commented out because most PiEEG boards tie the
# hardware START pin permanently HIGH, meaning conversions begin automatically.
# Sending 0x08 via SPI on those boards can cause DRDY to never fire.
# Uncomment only if your board requires a software START.
# spi.xfer2([0x08])                                          # START conversions
# time.sleep(0.01)

spi.xfer2([0x10])                                            # RDATAC (start continuous read)
time.sleep(0.1)

print("[PiEEG-LSL] ADS1299 initialised.")

# ============================================================
# --- LSL Outlet Setup ---
# ============================================================
info = StreamInfo(
    name=STREAM_NAME,
    type=STREAM_TYPE,
    channel_count=N_CHANNELS,
    nominal_srate=SAMPLE_RATE,
    channel_format=CHANNEL_FORMAT,
    source_id=SOURCE_ID,
)

# Label the channels in LSL metadata (optional but good practice)
chns = info.desc().append_child("channels")
for i in range(1, N_CHANNELS + 1):
    ch = chns.append_child("channel")
    ch.append_child_value("label", f"Ch{i}")
    ch.append_child_value("unit", "microvolts")
    ch.append_child_value("type", "EEG")

outlet = StreamOutlet(info)
print(f"[PiEEG-LSL] LSL stream '{STREAM_NAME}' is live on the network.")
print(f"            {N_CHANNELS} channels | {SAMPLE_RATE} Hz | {CHANNEL_FORMAT}")
print("[PiEEG-LSL] Waiting for receiver (DB-BMI.py on Mac)... Press Ctrl+C to stop.\n")

# ============================================================
# --- Graceful Shutdown ---
# ============================================================
_running = True

def _shutdown(sig, frame):
    global _running
    print("\n[PiEEG-LSL] Shutting down...")
    _running = False

signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)

# ============================================================
# --- Main Streaming Loop ---
# ============================================================
sample_count  = 0
drdy_timeouts = 0
zero_frame_warnings = 0

try:
    while _running:
        # Block up to 0.1 s waiting for DRDY to go active
        if not drdy.wait_for_active(timeout=0.1):
            drdy_timeouts += 1
            continue

        # Read one 54-byte daisy-chain frame from both ADS1299 chips
        raw = spi.readbytes(BYTES_PER_SAMPLE)
        timestamp = local_clock()   # Use LSL clock for precise sync

        # DEBUG: warn if the entire frame is zero bytes.
        # If this floods the console, the ADS1299 is not converting —
        # check hardware connections and that the START command above took effect.
        if all(b == 0 for b in raw):
            zero_frame_warnings += 1
            if zero_frame_warnings <= 10 or zero_frame_warnings % 250 == 0:
                print(f"[PiEEG-LSL] WARNING: all-zero SPI frame #{zero_frame_warnings} "
                      f"— ADS1299 not converting? Check hardware.")
            continue

        # --- Decode 16 channels across two chips ---
        #
        # Chip 1  →  Ch 1–8   →  data starts at byte 3
        #                         offset formula: 3 + ch * 3   (ch = 0..7)
        #
        # Chip 2  →  Ch 9–16  →  data starts at byte 30
        #            (bytes 27-29 are Chip 2 status — skipped entirely)
        #                         offset formula: 30 + ch * 3  (ch = 0..7)
        channels = []

        # -- Chip 1: channels 1–8 (raw indices 0–7) --
        for ch in range(8):
            offset = 3 + ch * 3
            b1, b2, b3 = raw[offset], raw[offset + 1], raw[offset + 2]
            val = (b1 << 16) | (b2 << 8) | b3
            if val >= 0x800000:          # Two's complement sign extension
                val -= 0x1000000
            channels.append(round(val * (VREF / GAIN / (2**23 - 1)) * 1e6, 4))

        # -- Chip 2: channels 9–16 (raw indices 0–7 on second chip) --
        # Byte 27 is the FIRST byte of Chip 2's frame; bytes 27-29 are its
        # 3 status bytes, so channel data begins at byte 30.
        for ch in range(8):
            offset = 30 + ch * 3
            b1, b2, b3 = raw[offset], raw[offset + 1], raw[offset + 2]
            val = (b1 << 16) | (b2 << 8) | b3
            if val >= 0x800000:
                val -= 0x1000000
            channels.append(round(val * (VREF / GAIN / (2**23 - 1)) * 1e6, 4))

        # --- Push sample to LSL network ---
        outlet.push_sample(channels, timestamp)
        sample_count += 1

        # Heartbeat every ~1 second
        if sample_count % SAMPLE_RATE == 0:
            print(f"[PiEEG-LSL] {sample_count} samples pushed | "
                  f"Ch1: {channels[0]:7.2f} µV | Timeouts: {drdy_timeouts} | "
                  f"Zero-frames skipped: {zero_frame_warnings}")

finally:
    print("[PiEEG-LSL] Closing SPI and GPIO...")
    try:
        spi.xfer2([0x11])  # SDATAC — stop the ADS1299
        spi.close()
    except Exception:
        pass
    try:
        drdy.close()
    except Exception:
        pass
    print(f"[PiEEG-LSL] Done. Total samples pushed: {sample_count}")
