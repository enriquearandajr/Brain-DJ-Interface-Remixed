#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared PiEEG helpers for DB-BMI and the Raspberry Pi LSL streamer.

Windows should normally receive PiEEG samples over Lab Streaming Layer (LSL).
Run ``pieeg_lsl_streamer.py`` on the Raspberry Pi that has the PiEEG board
attached, then run ``DB-BMI.py`` on Windows.
"""

from __future__ import annotations

import csv
import math
import os
import random
import re
import threading
import time
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence, Union


STREAM_NAME = "PiEEG"
STREAM_TYPE = "EEG"
N_CHANNELS = 16
SAMPLE_RATE = 250
CHANNEL_FORMAT = "float32"
SOURCE_ID = "PiEEG_16ch"

DRDY_PIN = 26
DRDY_PIN_2 = 13
CS_PIN_2 = 19
VREF = 4.5
GAIN = 24
SPI_BUS = 0
SPI_DEVICE = 0
SPI_DEVICE_2 = 1
SPI_MAX_SPEED_HZ = 1_000_000
SPI_MODE = 0b01
BYTES_PER_ADS1299 = 27
BYTES_PER_SAMPLE = BYTES_PER_ADS1299 * 2

EEG_HEADER = ["timestamp_s"] + [f"ch{i}_uV" for i in range(1, N_CHANNELS + 1)]
PIEEG_MODE_ENV = "PIEEG_MODE"
PIEEG_LSL_TIMEOUT_ENV = "PIEEG_LSL_TIMEOUT"
PIEEG_SEND_START_ENV = "PIEEG_SEND_START"

_DEMO_FREQS = [8, 10, 12, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _noop(*_args, **_kwargs):
    pass


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def sanitize_filename_component(value: object, default: str = "untitled", max_length: int = 120) -> str:
    """Return a Windows-safe filename component."""
    text = str(value) if value is not None else ""
    text = _INVALID_FILENAME_CHARS.sub("_", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    text = re.sub(r"_+", "_", text)
    if not text:
        text = default
    return text[:max_length].rstrip(" .") or default


def write_eeg_csv(path: Union[os.PathLike[str], str], rows: Iterable[Sequence[object]]) -> None:
    """Write PiEEG trial rows with a stable 16-channel header."""
    filename = Path(path)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(EEG_HEADER)
        writer.writerows(rows)


def decode_ads1299_daisy_frame(
    raw: Sequence[int],
    *,
    vref: float = VREF,
    gain: float = GAIN,
) -> list[float]:
    """Decode one 54-byte two-ADS1299 daisy-chain frame into microvolts."""
    if len(raw) < BYTES_PER_SAMPLE:
        raise ValueError(f"Expected {BYTES_PER_SAMPLE} bytes, got {len(raw)}")

    channels: list[float] = []
    scale = (vref / gain / (2**23 - 1)) * 1e6

    # Chip 1: bytes 0-2 are status, channel data starts at byte 3.
    # Chip 2: bytes 27-29 are status, channel data starts at byte 30.
    for base in (3, 30):
        for ch in range(8):
            offset = base + ch * 3
            b1, b2, b3 = raw[offset], raw[offset + 1], raw[offset + 2]
            value = (b1 << 16) | (b2 << 8) | b3
            if value >= 0x800000:
                value -= 0x1000000
            channels.append(round(value * scale, 4))

    return channels


def decode_ads1299_frame(
    raw: Sequence[int],
    *,
    vref: float = VREF,
    gain: float = GAIN,
) -> list[float]:
    """Decode one 27-byte ADS1299 frame into eight microvolt channels."""
    if len(raw) < BYTES_PER_ADS1299:
        raise ValueError(f"Expected {BYTES_PER_ADS1299} bytes, got {len(raw)}")

    channels: list[float] = []
    scale = (vref / gain / (2**23 - 1)) * 1e6
    for ch in range(8):
        offset = 3 + ch * 3
        b1, b2, b3 = raw[offset], raw[offset + 1], raw[offset + 2]
        value = (b1 << 16) | (b2 << 8) | b3
        if value >= 0x800000:
            value -= 0x1000000
        channels.append(round(value * scale, 4))

    return channels


class PiEEGHardware:
    """Direct SPI reader for a PiEEG board attached to a Raspberry Pi."""

    def __init__(
        self,
        *,
        drdy_pin: int = DRDY_PIN,
        drdy_pin2: Optional[int] = DRDY_PIN_2,
        cs_pin2: Optional[int] = CS_PIN_2,
        spi_bus: int = SPI_BUS,
        spi_device: int = SPI_DEVICE,
        spi_device2: int = SPI_DEVICE_2,
        spi_max_speed_hz: int = SPI_MAX_SPEED_HZ,
        send_start: bool = True,
        separate_ads1299: bool = True,
        log: Optional[Callable[..., None]] = print,
    ) -> None:
        self.log = log or _noop
        self.drdy_pin = drdy_pin
        self.drdy_pin2 = drdy_pin2
        self.cs_pin2 = cs_pin2
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.spi_device2 = spi_device2
        self.spi_max_speed_hz = spi_max_speed_hz
        self.send_start = send_start
        self.separate_ads1299 = separate_ads1299
        self.drdy_timeouts = 0
        self.zero_frames = 0
        self._closed = False

        import spidev
        from gpiozero import DigitalInputDevice, DigitalOutputDevice

        self.log("[PiEEG] Initialising GPIO and SPI...")
        self.drdy = DigitalInputDevice(drdy_pin, pull_up=True)
        self.drdy2 = None
        self.cs2 = None
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = spi_max_speed_hz
        self.spi.mode = SPI_MODE
        self.spi2 = None

        if separate_ads1299:
            if drdy_pin2 is None or cs_pin2 is None:
                raise ValueError("PiEEG-16 separate ADS1299 mode needs drdy_pin2 and cs_pin2.")
            self.drdy2 = DigitalInputDevice(drdy_pin2, pull_up=True)
            self.cs2 = DigitalOutputDevice(cs_pin2, initial_value=True)
            self.spi2 = spidev.SpiDev()
            self.spi2.open(spi_bus, spi_device2)
            self.spi2.max_speed_hz = spi_max_speed_hz
            self.spi2.mode = SPI_MODE
            try:
                self.spi2.no_cs = True
            except Exception:
                pass

        self._initialise_ads1299()
        self.log("[PiEEG] ADS1299 initialised.")
        if self.separate_ads1299:
            self.log(
                "[PiEEG] PiEEG-16 pinout: "
                f"DRDY1=GPIO{self.drdy_pin}, DRDY2=GPIO{self.drdy_pin2}, CS2=GPIO{self.cs_pin2}."
            )

    def _xfer_chip2(self, data: Sequence[int]) -> list[int]:
        if self.spi2 is None or self.cs2 is None:
            raise RuntimeError("Second ADS1299 is not initialised.")
        self.cs2.value = 0
        try:
            return self.spi2.xfer2(list(data))
        finally:
            self.cs2.value = 1

    def _read_chip2(self, byte_count: int) -> list[int]:
        if self.spi2 is None or self.cs2 is None:
            raise RuntimeError("Second ADS1299 is not initialised.")
        self.cs2.value = 0
        try:
            return self.spi2.readbytes(byte_count)
        finally:
            self.cs2.value = 1

    def _for_each_chip(self, data: Sequence[int]) -> None:
        self.spi.xfer2(list(data))
        if self.separate_ads1299:
            self._xfer_chip2(data)

    def _initialise_ads1299(self) -> None:
        self._for_each_chip([0x06])  # RESET
        time.sleep(0.5)
        self._for_each_chip([0x11])  # SDATAC
        time.sleep(0.2)
        self._for_each_chip([0x43, 0x00, 0xE0])  # CONFIG3: enable internal reference
        time.sleep(0.01)
        self._for_each_chip([0x45, 0x07] + [0x60] * 8)  # CH1SET-CH8SET: gain=24
        time.sleep(0.01)
        if self.send_start:
            self._for_each_chip([0x08])  # START conversions.
            time.sleep(0.01)
        self._for_each_chip([0x10])  # RDATAC
        time.sleep(0.1)

    def reset_counters(self) -> None:
        self.drdy_timeouts = 0
        self.zero_frames = 0

    def read_channels(self, timeout: float = 0.1) -> Optional[list[float]]:
        if not self.drdy.wait_for_active(timeout=timeout):
            self.drdy_timeouts += 1
            return None

        if self.separate_ads1299:
            raw1 = self.spi.readbytes(BYTES_PER_ADS1299)
            assert self.drdy2 is not None
            if not self.drdy2.wait_for_active(timeout=timeout):
                self.drdy_timeouts += 1
                return None
            raw2 = self._read_chip2(BYTES_PER_ADS1299)
            raw = raw1 + raw2
            zero_frame = all(byte == 0 for byte in raw1) or all(byte == 0 for byte in raw2)
        else:
            raw = self.spi.readbytes(BYTES_PER_SAMPLE)
            zero_frame = all(byte == 0 for byte in raw)

        if zero_frame:
            self.zero_frames += 1
            if self.zero_frames <= 10 or self.zero_frames % SAMPLE_RATE == 0:
                self.log(
                    "[PiEEG] WARNING: all-zero SPI frame "
                    f"#{self.zero_frames}; check DRDY/START/SPI wiring."
                )
            return None

        if self.separate_ads1299:
            return decode_ads1299_frame(raw[:BYTES_PER_ADS1299]) + decode_ads1299_frame(raw[BYTES_PER_ADS1299:])

        return decode_ads1299_daisy_frame(raw)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._for_each_chip([0x11])  # SDATAC
            self.spi.close()
            if self.spi2 is not None:
                self.spi2.close()
        except Exception:
            pass
        try:
            self.drdy.close()
        except Exception:
            pass
        try:
            if self.drdy2 is not None:
                self.drdy2.close()
        except Exception:
            pass
        try:
            if self.cs2 is not None:
                self.cs2.close()
        except Exception:
            pass


class PiEEGRecorder:
    """Trial-scoped recorder used by DB-BMI.py.

    Modes:
        auto/direct: direct SPI if running on a Raspberry Pi with PiEEG attached
        auto/network: LSL receiver, intended for Windows and macOS
        demo: synthetic 16-channel signal for testing the experiment flow
    """

    def __init__(
        self,
        *,
        mode: Optional[str] = None,
        stream_name: str = STREAM_NAME,
        lsl_timeout: Optional[float] = None,
        sample_rate: int = SAMPLE_RATE,
        timestamp_fn: Optional[Callable[[], float]] = None,
        log: Optional[Callable[..., None]] = print,
    ) -> None:
        self.requested_mode = (mode or os.environ.get(PIEEG_MODE_ENV, "auto")).strip().lower()
        if self.requested_mode == "lsl":
            self.requested_mode = "network"
        self.stream_name = stream_name
        self.lsl_timeout = (
            float(os.environ.get(PIEEG_LSL_TIMEOUT_ENV, "5.0"))
            if lsl_timeout is None
            else lsl_timeout
        )
        self.sample_rate = sample_rate
        self.timestamp_fn = timestamp_fn or time.perf_counter
        self.log = log or _noop
        self.mode = "DEMO"
        self.status = "Not initialised"
        self._hardware: Optional[PiEEGHardware] = None
        self._lsl_inlet = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._rows: list[list[float]] = []
        self._missed_samples = 0
        self._zero_frames = 0
        self._setup()

    @property
    def missed_samples(self) -> int:
        if self.mode == "DIRECT" and self._hardware is not None:
            return self._hardware.drdy_timeouts
        return self._missed_samples

    @property
    def zero_frames(self) -> int:
        if self.mode == "DIRECT" and self._hardware is not None:
            return self._hardware.zero_frames
        return self._zero_frames

    def _setup(self) -> None:
        self._banner(f"Requested PiEEG mode: {self.requested_mode}")
        if self.requested_mode not in {"auto", "direct", "network", "demo"}:
            self._banner(
                f"Unknown PIEEG_MODE={self.requested_mode!r}; using auto instead."
            )
            self.requested_mode = "auto"

        if self.requested_mode in {"auto", "direct"} and self._try_direct():
            return
        if self.requested_mode in {"auto", "network"} and self._try_network():
            return

        self.mode = "DEMO"
        self.status = "Synthetic demo EEG"
        self._banner("Mode: DEMO - running with synthetic EEG data.")

    def _try_direct(self) -> bool:
        try:
            self._hardware = PiEEGHardware(
                send_start=env_flag(PIEEG_SEND_START_ENV, True),
                log=self.log,
            )
        except ImportError:
            if self.requested_mode == "direct":
                self._banner("Direct SPI unavailable. Install spidev and gpiozero on the Pi.")
            return False
        except Exception as exc:
            self._hardware = None
            self._banner(f"Direct SPI setup failed: {exc}")
            return False

        self.mode = "DIRECT"
        self.status = "Direct SPI PiEEG"
        self._banner("Mode: DIRECT - PiEEG hardware detected via SPI.")
        return True

    def _try_network(self) -> bool:
        try:
            from pylsl import StreamInlet, resolve_byprop
        except ImportError:
            self._banner("pylsl not found. Install it on Windows with: pip install pylsl")
            return False

        self._banner(
            f"Searching for LSL stream {self.stream_name!r} "
            f"(timeout {self.lsl_timeout:.1f}s)..."
        )
        try:
            streams = resolve_byprop("name", self.stream_name, timeout=self.lsl_timeout)
        except Exception as exc:
            self._banner(f"LSL stream search failed: {exc}")
            return False

        if not streams:
            self._banner(
                f"No LSL stream {self.stream_name!r} found. "
                "Start pieeg_lsl_streamer.py on the Raspberry Pi first."
            )
            return False

        self._lsl_inlet = StreamInlet(streams[0])
        info = self._lsl_inlet.info()
        self.mode = "NETWORK"
        self.status = f"LSL stream {info.name()} ({info.channel_count()} ch @ {info.nominal_srate()} Hz)"
        self._banner(f"Mode: NETWORK - connected to LSL stream {info.name()!r}.")
        return True

    def _banner(self, message: str) -> None:
        self.log("---------------------------------------------------")
        self.log(message)
        self.log("---------------------------------------------------")

    def start_trial(self) -> None:
        self.stop_trial(timeout=0.5, clear=True)
        self._stop_event.clear()
        self._missed_samples = 0
        self._zero_frames = 0
        if self._hardware is not None:
            self._hardware.reset_counters()
        with self._lock:
            self._rows.clear()
        self._thread = threading.Thread(
            target=self._record_loop,
            name=f"PiEEGRecorder-{self.mode}",
            daemon=True,
        )
        self._thread.start()

    def stop_trial(self, *, timeout: float = 2.0, clear: bool = True) -> list[list[float]]:
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        self._thread = None
        with self._lock:
            rows = list(self._rows)
            if clear:
                self._rows.clear()
        return rows

    def shutdown(self) -> None:
        self.stop_trial(timeout=1.0, clear=True)
        if self._lsl_inlet is not None:
            try:
                self._lsl_inlet.close_stream()
            except Exception:
                pass
        if self._hardware is not None:
            self._hardware.close()

    def _record_loop(self) -> None:
        sample_count = 0
        demo_start = time.perf_counter()

        while not self._stop_event.is_set():
            if self.mode == "DIRECT":
                assert self._hardware is not None
                channels = self._hardware.read_channels(timeout=0.1)
                if channels is None:
                    continue
                timestamp = self.timestamp_fn()
            elif self.mode == "NETWORK":
                sample, timestamp = self._lsl_inlet.pull_sample(timeout=0.1)
                if sample is None:
                    self._missed_samples += 1
                    continue
                channels = [round(float(value), 4) for value in sample[:N_CHANNELS]]
            else:
                elapsed = time.perf_counter() - demo_start
                timestamp = self.timestamp_fn()
                channels = [
                    round(50.0 * math.sin(2 * math.pi * freq * elapsed) + 3.0 * (random.random() - 0.5), 4)
                    for freq in _DEMO_FREQS
                ]
                time.sleep(1.0 / self.sample_rate)

            with self._lock:
                self._rows.append([timestamp] + channels)

            sample_count += 1
            if sample_count % self.sample_rate == 0:
                self.log(
                    f"[PiEEG {self.mode}] {sample_count:6d} samples | "
                    f"Ch1: {channels[0]:7.2f} uV | Missed: {self.missed_samples}"
                )


class PiEEGLSLStreamer:
    """Raspberry Pi process that publishes PiEEG SPI samples as an LSL stream."""

    def __init__(
        self,
        *,
        stream_name: str = STREAM_NAME,
        stream_type: str = STREAM_TYPE,
        sample_rate: int = SAMPLE_RATE,
        channel_format: str = CHANNEL_FORMAT,
        source_id: str = SOURCE_ID,
        drdy_pin: int = DRDY_PIN,
        drdy_pin2: Optional[int] = DRDY_PIN_2,
        cs_pin2: Optional[int] = CS_PIN_2,
        spi_max_speed_hz: int = SPI_MAX_SPEED_HZ,
        send_start: Optional[bool] = None,
        log: Optional[Callable[..., None]] = print,
    ) -> None:
        from pylsl import StreamInfo, StreamOutlet, local_clock

        self.log = log or _noop
        self.sample_rate = sample_rate
        self._local_clock = local_clock
        self._running = False
        self.hardware = PiEEGHardware(
            drdy_pin=drdy_pin,
            drdy_pin2=drdy_pin2,
            cs_pin2=cs_pin2,
            spi_max_speed_hz=spi_max_speed_hz,
            send_start=env_flag(PIEEG_SEND_START_ENV, True) if send_start is None else send_start,
            log=self.log,
        )

        info = StreamInfo(
            name=stream_name,
            type=stream_type,
            channel_count=N_CHANNELS,
            nominal_srate=sample_rate,
            channel_format=channel_format,
            source_id=source_id,
        )
        channels = info.desc().append_child("channels")
        for i in range(1, N_CHANNELS + 1):
            channel = channels.append_child("channel")
            channel.append_child_value("label", f"Ch{i}")
            channel.append_child_value("unit", "microvolts")
            channel.append_child_value("type", "EEG")

        self.outlet = StreamOutlet(info)
        self.log(f"[PiEEG-LSL] LSL stream {stream_name!r} is live.")
        self.log(f"[PiEEG-LSL] {N_CHANNELS} channels | {sample_rate} Hz | {channel_format}")

    def stop(self) -> None:
        self._running = False

    def close(self) -> None:
        self.stop()
        self.hardware.close()

    def run(self) -> int:
        sample_count = 0
        self._running = True
        self.log("[PiEEG-LSL] Waiting for DB-BMI.py to connect. Press Ctrl+C to stop.")
        try:
            while self._running:
                channels = self.hardware.read_channels(timeout=0.1)
                if channels is None:
                    continue
                self.outlet.push_sample(channels, self._local_clock())
                sample_count += 1
                if sample_count % self.sample_rate == 0:
                    self.log(
                        f"[PiEEG-LSL] {sample_count} samples pushed | "
                        f"Ch1: {channels[0]:7.2f} uV | "
                        f"Timeouts: {self.hardware.drdy_timeouts} | "
                        f"Zero frames skipped: {self.hardware.zero_frames}"
                    )
        finally:
            self.close()
            self.log(f"[PiEEG-LSL] Done. Total samples pushed: {sample_count}")
        return sample_count
