from typing import List, Optional

from loguru import logger
from smbus2 import SMBus

from typedefs import FlightController, PlatformType, Serial


class LinuxFlightController(FlightController):
    """Linux-based Flight-controller board."""

    @property
    def type(self) -> PlatformType:
        return PlatformType.Linux

    @staticmethod
    def detect():
        raise NotImplementedError

    def serial_ports_mapping(self):
        raise NotImplementedError

    def get_serial_cmdlines(self) -> str:
        cmdlines = [f"-{entry.port} {entry.endpoint}" for entry in self.get_serials()]
        return " ".join(cmdlines)

    def get_serials(self) -> List[Serial]:
        raise NotImplementedError

    @staticmethod
    def setup_board():
        # loads overlays and required modules in runtime
        raise NotImplementedError

    def check_for_i2c_device(self, bus, address) -> bool:
        try:
            bus = SMBus(bus)
            bus.read_byte_data(address, 0)
            return True
        except OSError:
            return False

    @staticmethod
    def detect_boards() -> Optional["LinuxFlightController"]:
        from flight_controller_detector.linux.navigator import (
            NavigatorPi4,
            NavigatorPi5,
        )

        for candidate in [NavigatorPi4, NavigatorPi5]:
            logger.info(f"Detecting Linux board: {candidate.__name__}")
            if candidate().detect():
                logger.info(f"Detected Linux board: {candidate.__name__}")
                return candidate()
        raise RuntimeError("No Linux board detected")
