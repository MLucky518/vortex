"""Demo 1: connect to the flight controller and listen.

Read only. This script cannot arm, cannot move, and cannot embarrass
anyone. Run it first on every new environment to prove the link works
before anything with propellers is involved.

    uv run 01_telemetry.py

It talks to whatever ADDRESS points at. By default that is the
simulator. On the real aircraft it is the Pixhawk over serial, and not
one line of this file changes.
"""

import asyncio

from mavsdk import System

from config import ADDRESS


async def main():
    drone = System()

    print(f"Connecting to {ADDRESS} ...")
    await drone.connect(system_address=ADDRESS)

    # MAVLink is a stream of messages rather than a request/response API,
    # so almost everything here is "subscribe and react" instead of
    # "call and wait". connection_state() yields every time the link
    # changes; we stop at the first one that reports connected.
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected.\n")
            break

    # position() yields continuously for as long as the vehicle is
    # publishing. Ctrl-C to stop.
    async for position in drone.telemetry.position():
        print(
            f"lat {position.latitude_deg:11.6f}   "
            f"lon {position.longitude_deg:11.6f}   "
            f"alt {position.relative_altitude_m:6.2f} m"
        )
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")