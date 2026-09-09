# Vortex

CIS 116 team drone build. A Holybro X500 V2 with a Pixhawk 6C running
PX4, and a Raspberry Pi 5 as companion computer.

The Pixhawk runs PX4 and keeps the aircraft in the air. We are not
writing that. The Pi is a Linux computer that tells the aircraft what to
do, over MAVLink. That part is ours.

Read `HOW-IT-WORKS.md` if you want to understand the system. Read on if
you just want to run it.

## Setup

Install uv once:

```bash
brew install uv                                     # macOS
winget install --id=astral-sh.uv -e                 # Windows
curl -LsSf https://astral.sh/uv/install.sh | sh     # Linux
```

Then:

```bash
git clone <repository-url>
cd vortex
cp .env.default .env
```

The defaults work for simulator development. You only edit `.env` when
running on the real aircraft.

## Running the tests

```bash
uv run pytest
```

No PX4, no simulator, no hardware required. Pure logic like flight path
geometry lives in its own module specifically so it can be tested in
milliseconds instead of thirty seconds.

Keep it that way: math goes in a plain function with a test, MAVSDK calls
stay thin.

## Running the flight code

Needs the simulator running. See `SIMULATOR.md`.

```bash
uv run 01_telemetry.py
```

`01_telemetry.py` is read only. It connects, prints position, and cannot
arm or move the aircraft. Run it first in any new environment to prove
the link works.

## Adding dependencies

```bash
uv add mavsdk            # runtime
uv add --dev pytest      # development only
```

Commit `pyproject.toml` and `uv.lock` when you do. The lockfile is what
makes everyone's environment identical, including the Pi later.

If you hit an error and Google it, every answer will tell you to run
`pip install` or activate a venv. Ignore that and ask. Mixing uv and pip
is the one way this setup gets confusing.

## What is in here

```text
config.py                  connection address and mission constants
geometry.py                flight path math, no hardware dependencies
01_telemetry.py            connects to PX4 and prints position
tests/test_geometry.py     runs without a simulator
.env.default               committed template, copy to .env
```

## The one architectural idea

`config.py` reads one environment variable:

```text
simulator        udpin://0.0.0.0:14540        (default)
real aircraft    serial:///dev/serial0:921600
```

Nothing else in the codebase knows which one it is talking to. MAVLink
does not care whether it travels over UDP, a serial cable, or a radio.
That is why we can build the entire software side now and change one
string when the hardware arrives.

## Documentation

| File | What it covers |
|---|---|
| `HOW-IT-WORKS.md` | Every part of the kit, what PX4 and MAVLink are |
| `SIMULATOR.md` | Running PX4 SITL on macOS, including the traps |
| `PLAN.md` | Phased build plan, each phase with a completion test |
| `PI-SETUP.md` | Flashing and configuring the Raspberry Pi |
| `SECURITY.md` | What we know is exposed, and what to fix before flight |

## Who owns what

Needs names next to it, not just descriptions.

- **Companion software** — the Python in this repo
- **PX4 configuration** — airframe, sensor and ESC calibration, RC
  binding, failsafes, all through QGroundControl. Not a coding job.
- **Physical build** — assembly
- **Build documentation** — filming each part during assembly. Cannot be
  recreated afterward.
- **Presentation** — the PowerPoint. `HOW-IT-WORKS.md` covers most of the
  technical content.

## Open questions

**No RC transmitter or receiver is on the equipment sheet.** A telemetry
radio and an RC control link are different things. Without RC we cannot
fly manually, cannot have a safety pilot, and cannot recover from a
software fault. Someone needs to raise this before purchasing closes.

**The Pi to Pixhawk connection is unconfirmed.** Which telemetry port,
which serial device, what baud rate, how it gets power. The example in
`.env.default` is an example, not the final answer.