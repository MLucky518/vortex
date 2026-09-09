"""Connection and mission configuration.

Every script in this project imports configuration values from here.
The rest of the codebase does not need to know whether it is talking
to PX4 SITL or to a real Pixhawk.

Environment-specific configuration can be provided through a .env file.

Simulator:
    The default address connects to PX4 SITL over UDP.

Real aircraft:
    Set DRONE_ADDRESS in .env to the appropriate connection string for
    the Raspberry Pi and Pixhawk configuration.

    Example:
        DRONE_ADDRESS=serial:///dev/serial0:921600

    The actual serial device and baud rate may differ depending on the
    Raspberry Pi and Pixhawk configuration.
"""

import os

from dotenv import load_dotenv

# Load local environment configuration from .env if it exists.
# Existing shell environment variables take precedence.
load_dotenv()

# PX4 SITL publishes MAVLink for companion software on UDP port 14540.
# QGroundControl typically uses port 14550.
SITL_ADDRESS = "udpin://0.0.0.0:14540"

# Use DRONE_ADDRESS when configured; otherwise fall back to PX4 SITL.
ADDRESS = os.getenv("DRONE_ADDRESS", SITL_ADDRESS)

# Mission configuration.
TAKEOFF_ALTITUDE = 3.0  # metres
SQUARE_SIDE = 5.0       # metres