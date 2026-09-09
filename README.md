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

## Running

```bash
uv run 01_telemetry.py
```

uv handles the Python version, the environment, and the dependencies.
There is no virtualenv to create or activate.

If you hit an error and Google it, every answer will tell you to run
`pip install` or activate a venv. Ignore that and ask. Mixing uv and pip
is the one way this setup gets confusing.

Adding a dependency:

```bash
uv add mavsdk            # runtime
uv add --dev pytest      # development only
```

Commit `pyproject.toml` and `uv.lock` when you do.

## Tests

```bash
uv run pytest
```

These do not need PX4, the simulator, or hardware. Pure logic like flight
path geometry lives in its own module specifically so it can be tested in
milliseconds instead of thirty seconds.

Keep it that way. Math goes in a plain function with a test. MAVSDK calls
stay thin.

## Simulator

Only needed if you are writing or testing flight code. Skip this if you
are doing the build, the video, or the slides.

TODO: document the working setup once it is verified end to end. Do not
paste a procedure from the internet into this section without running it
against this repo first.

## Documentation

| File | What it covers |
|---|---|
| `HOW-IT-WORKS.md` | Every part of the kit, what PX4 and MAVLink are |
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