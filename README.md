# vortex
CIS 116 team drone build. Raspberry Pi 5 companion computer for a Holybro X500 V2 running PX4
# Vortex

Vortex is the CIS 116 team drone project.

The aircraft is a Holybro X500 V2 using a Pixhawk 6C flight controller running PX4. A Raspberry Pi 5 acts as the companion computer and runs the software developed by our team.

## Architecture

The Pixhawk and Raspberry Pi have different responsibilities.

### Pixhawk 6C

The Pixhawk runs PX4 and handles the real-time flight-control work required to keep the aircraft stable.

This includes things such as:

* reading flight sensors
* estimating aircraft state
* stabilization
* motor control
* flight modes
* low-level failsafes

We are not writing the PX4 flight-control firmware.

### Raspberry Pi 5

The Raspberry Pi is a Linux companion computer.

Our software runs on the Pi and communicates with PX4 over MAVLink.

The Pi can perform higher-level tasks such as:

* monitoring telemetry
* issuing flight commands
* generating flight paths
* running missions
* processing sensor or camera data
* performing higher-level decision making

The basic architecture is:

```text
Vortex Python software
        |
      MAVSDK
        |
      MAVLink
        |
     Pixhawk 6C
        |
       PX4
        |
Motors / sensors / aircraft
```

During development, PX4 SITL replaces the physical Pixhawk and aircraft:

```text
Vortex Python software
        |
      MAVSDK
        |
      MAVLink
        |
     PX4 SITL
        |
Simulated aircraft
```

This allows most of our flight software to be developed before the physical aircraft is ready.

---

# Getting Started

## 1. Install uv

Vortex uses `uv` to manage Python, the project environment, dependencies, and development tools.

### macOS

```bash
brew install uv
```

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows development machines

```powershell
winget install --id=astral-sh.uv -e
```

The Raspberry Pi itself will run Linux.

---

## 2. Clone the repository

```bash
git clone <repository-url>
cd vortex
```

---

## 3. Create your local environment configuration

The repository contains:

```text
.env.default
```

This is the safe configuration template committed to Git.

Copy it to:

```text
.env
```

with:

```bash
cp .env.default .env
```

The `.env` file is local to your machine and must not be committed.

For normal SITL development, the default configuration should be sufficient.

Example:

```dotenv
DRONE_ADDRESS=udpin://0.0.0.0:14540
```

For a physical Raspberry Pi connected to a Pixhawk, `DRONE_ADDRESS` will normally use an appropriate serial connection instead.

For example:

```dotenv
DRONE_ADDRESS=serial:///dev/serial0:921600
```

That is only an example.

The actual Linux serial device, Pixhawk telemetry port, and baud rate depend on the final aircraft configuration.

See `SECURITY.md` before placing secrets or sensitive configuration in environment files.

---

# Running the Code

From the repository root:

```bash
uv run 01_telemetry.py
```

`uv` will prepare the project's managed Python environment and install the dependencies described by `pyproject.toml` and the lockfile.

There is no virtual environment that team members need to create or activate manually.

There should also be no need to manage Vortex dependencies with normal `pip install` commands.

## Dependency Management

If Vortex needs a new runtime dependency:

```bash
uv add <package>
```

For example:

```bash
uv add mavsdk
```

If a dependency is only needed while developing or testing Vortex:

```bash
uv add --dev <package>
```

For example:

```bash
uv add --dev pytest
```

Run tools and scripts through the project environment with:

```bash
uv run <command>
```

Do not create a second manual virtual environment or mix arbitrary `pip install` commands into the project setup.

The goal is for every team member to receive the same dependency set from the repository instead of maintaining their own undocumented Python environment.

---

# Running Tests

Run the complete test suite with:

```bash
uv run pytest
```

Many Vortex tests intentionally do **not** require PX4, SITL, MAVLink, or physical hardware.

For example, flight-path geometry should be testable as ordinary Python:

```text
tests
   |
   v
geometry.py
```

rather than requiring:

```text
tests
   |
   v
MAVSDK
   |
   v
PX4
   |
   v
simulator
```

Keeping pure application logic separate from hardware communication allows us to:

* run tests in milliseconds
* catch mathematical mistakes quickly
* reproduce bugs consistently
* test without an aircraft
* distinguish application bugs from MAVLink or PX4 problems

Integration tests involving the simulator will be added separately where appropriate.

---

# Running PX4 SITL

PX4 SITL is only required when testing behavior that actually communicates with PX4.

Examples include:

* connecting with MAVSDK
* receiving vehicle telemetry
* arming
* takeoff
* landing
* sending position setpoints
* mission execution

It is not required for pure Python tests such as geometry calculations.

## Simulator setup

TODO: Document the final PX4 SITL startup procedure after the team's development setup has been verified.

This section should eventually document:

1. starting PX4 SITL
2. confirming MAVLink output
3. connecting QGroundControl if needed
4. starting Vortex
5. confirming telemetry
6. safely stopping the simulation

Do not copy a random simulator setup from the internet into this section without testing it against this repository first.

---

# Configuration

Application configuration currently lives in `config.py`.

Environment-specific configuration can be supplied through `.env`.

The intended separation is:

```text
.env
    Machine / environment configuration

config.py
    Application defaults and mission configuration
```

For example:

```text
DRONE_ADDRESS
```

depends on the environment and therefore belongs in environment configuration.

Values such as:

```text
TAKEOFF_ALTITUDE
SQUARE_SIDE
```

describe mission behavior and can remain normal application constants unless there is a reason to make them configurable later.

The application should provide safe development defaults whenever practical.

---

# Project Structure

The project will evolve as Vortex grows, but the general separation should remain:

```text
vortex/
|
├── .env.default
├── .gitignore
├── README.md
├── SECURITY.md
├── pyproject.toml
├── uv.lock
|
├── config.py
├── geometry.py
├── 01_telemetry.py
|
├── tests/
|   └── test_geometry.py
|
├── HOW-IT-WORKS.md
├── PLAN.md
└── PI-SETUP.md
```

Not every future module needs to be decided in advance.

The important architectural rule is to avoid mixing everything into one flight script.

Whenever possible:

```text
pure logic
    |
    v
flight / application logic
    |
    v
MAVSDK
    |
    v
PX4
```

Pure logic should remain independently testable.

---

# Documentation

## `README.md`

How to understand, install, configure, run, and test Vortex.

Start here if you just cloned the repository.

## `HOW-IT-WORKS.md`

Explains the aircraft components and how they work together.

This should explain concepts such as:

* Pixhawk
* Raspberry Pi
* PX4
* MAVLink
* MAVSDK
* ESCs
* motors
* telemetry
* companion computers

Start here if you want to understand the system rather than simply run it.

## `PLAN.md`

The phased Vortex development plan.

Each phase should have a measurable completion condition so the team knows when it is actually finished.

## `PI-SETUP.md`

Instructions for preparing the Raspberry Pi 5 that will run Vortex on the physical aircraft.

## `SECURITY.md`

Security assumptions, threat model, secrets policy, network protections, MAVLink security, Raspberry Pi hardening, and preflight security requirements.

---

# Development Principles

## Separate logic from hardware

Mathematics, geometry, validation, mission generation, and other deterministic logic should not depend directly on MAVSDK when that dependency can reasonably be avoided.

## Test the smallest thing possible

If a calculation can be tested without PX4, test it without PX4.

Use SITL when PX4 behavior actually matters.

Use physical hardware only when the behavior cannot be adequately demonstrated in software.

## Keep configuration explicit

Avoid unexplained hard-coded connection information scattered throughout the application.

Environment-specific values belong in configuration.

## Never commit secrets

Credentials, signing keys, passwords, and other secrets must not be committed to the repository.

See `SECURITY.md`.

## Prefer safe failure

Unexpected inputs or invalid states should cause Vortex to refuse an operation rather than blindly send an unsafe flight command.

Safety validation will become increasingly important as flight functionality is added.

---

# Team Responsibilities

The project requires more than programming.

The team needs clear ownership for at least the following areas:

### Companion software

Vortex development running on the Raspberry Pi.

### PX4 configuration

Someone must own PX4 configuration through QGroundControl, including tasks such as:

* airframe setup
* sensor calibration
* ESC configuration
* RC configuration
* flight-mode configuration
* failsafe configuration
* verification before flight

This is an aircraft configuration responsibility, not simply a Python coding task.

### Physical aircraft build

Someone must own assembly and ensure the aircraft matches the required documentation and project deliverables.

### Build documentation / video

Someone must ensure required physical-build documentation is captured while the aircraft is assembled.

This cannot easily be recreated after assembly is complete.

### Presentation

Someone must own the final PowerPoint and presentation requirements.

`HOW-IT-WORKS.md` should provide much of the technical material.

---

# Open Questions for the Team

## RC control

The current equipment information does not identify an RC transmitter and receiver.

A telemetry radio and an RC control link perform different jobs.

Before purchasing closes, the team should determine:

* whether manual RC control is required
* whether a safety pilot will be required during testing
* which RC transmitter and receiver are compatible with the final setup
* who is responsible for obtaining and configuring them

## Pixhawk-to-Pi connection

The final physical connection between the Raspberry Pi and Pixhawk must be confirmed.

We should verify:

* which Pixhawk telemetry/UART port will be used
* which Raspberry Pi serial device it appears as
* the configured baud rate
* required wiring
* power and grounding requirements

Do not assume the example connection string in `.env.default` is the final aircraft configuration.

## Simulator workflow

The exact SITL startup process should be documented after it has been tested successfully by the team.

---

# Safety

A successful software command is not automatically a safe flight command.

Before physical flight testing, the team must verify the aircraft, PX4 configuration, failsafes, communications, flight area, manual recovery options, and any school-specific safety requirements.

Simulator success should be treated as a prerequisite to physical testing where practical—not as proof that the real aircraft is safe to fly.

See `SECURITY.md` for the security side of the system.
