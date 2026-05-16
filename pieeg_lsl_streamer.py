#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pieeg_lsl_streamer.py
=====================
Runs on the Raspberry Pi 5.

Reads 16-channel EEG data from the PiEEG board (two ADS1299 chips) via SPI
and broadcasts it as a Lab Streaming Layer (LSL) stream on the local network.

Requirements (Pi side):
    pip install spidev gpiozero pylsl

Run this script on the Raspberry Pi that has the PiEEG board attached:
    python3 pieeg_lsl_streamer.py

Then run DB-BMI.py on Windows. The experiment will auto-discover the LSL stream
named "PiEEG" and save one EEG CSV per song trial.
"""

from __future__ import annotations

import argparse
import signal
import sys
from typing import Optional

from pieeg_lsl_helper import (
    CS_PIN_2,
    DRDY_PIN,
    DRDY_PIN_2,
    SAMPLE_RATE,
    SPI_MAX_SPEED_HZ,
    STREAM_NAME,
    PiEEGLSLStreamer,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stream PiEEG data over LSL.")
    parser.add_argument("--stream-name", default=STREAM_NAME, help="LSL stream name.")
    parser.add_argument("--sample-rate", type=int, default=SAMPLE_RATE, help="Nominal LSL sample rate.")
    parser.add_argument("--drdy-pin", type=int, default=DRDY_PIN, help="BCM GPIO pin connected to ADS1299 chip 1 DRDY.")
    parser.add_argument("--drdy-pin2", type=int, default=DRDY_PIN_2, help="BCM GPIO pin connected to ADS1299 chip 2 DRDY.")
    parser.add_argument("--cs-pin2", type=int, default=CS_PIN_2, help="BCM GPIO pin connected to ADS1299 chip 2 CS.")
    parser.add_argument("--spi-hz", type=int, default=SPI_MAX_SPEED_HZ, help="SPI max speed in Hz.")
    parser.set_defaults(send_start=True)
    parser.add_argument(
        "--send-start",
        dest="send_start",
        action="store_true",
        help="Send ADS1299 START over SPI. This is enabled by default for PiEEG-16.",
    )
    parser.add_argument(
        "--no-send-start",
        dest="send_start",
        action="store_false",
        help="Do not send ADS1299 START over SPI.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        streamer = PiEEGLSLStreamer(
            stream_name=args.stream_name,
            sample_rate=args.sample_rate,
            drdy_pin=args.drdy_pin,
            drdy_pin2=args.drdy_pin2,
            cs_pin2=args.cs_pin2,
            spi_max_speed_hz=args.spi_hz,
            send_start=args.send_start,
        )
    except ImportError as exc:
        print(
            "[PiEEG-LSL] Missing Pi-side dependency. On the Raspberry Pi run:\n"
            "    pip install spidev gpiozero pylsl\n"
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"[PiEEG-LSL] Failed to start streamer: {exc}", file=sys.stderr)
        return 1

    def request_shutdown(_signum, _frame):
        print("\n[PiEEG-LSL] Shutting down...")
        streamer.stop()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    streamer.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
