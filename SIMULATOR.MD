# Running the Simulator

PX4 SITL on macOS. Everything here was verified on an M1 Pro, Gazebo
Harmonic 8.15.0, PX4 v1.18.0-beta.

You only need this if you are writing or testing flight code. If you are
doing the physical build, the video, or the slides, skip it.

## What SITL actually is

**Software In The Loop** is the real PX4 firmware compiled to run on a
normal computer instead of on a Pixhawk, connected to a physics simulator
instead of to real sensors and motors.

What is real: the firmware itself, every module, the EKF, the arming
logic, the failsafes, and the MAVLink interface byte for byte.

What is simulated: physics, sensor readings, motors, ESCs.

Our code cannot tell the difference. That is the entire point, and it is
why we can build the software before the aircraft exists.

PX4 includes an **x500** airframe model, which is the same Holybro X500
on our equipment sheet. We are not simulating a generic quadcopter.

---

## One-time setup

### 1. Prerequisites

```bash
xcode-select --install        # if not already present
df -h /                       # want 15 GB free
```

Homebrew must be installed.

### 2. Raise the open-file limit

The PX4 build opens many files at once and the macOS default of 256 is
too low. Without this you get "LD: too many open files" partway through
a 40 minute build.

```bash
echo 'ulimit -S -n 2048' >> ~/.zshrc
```

Open a new terminal afterward.

### 3. Clone PX4

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
```

Large, with many submodules. 10 to 20 minutes.

### 4. Run the setup script WITH `--sim-tools`

```bash
cd ~/PX4-Autopilot
bash ./Tools/setup/macos.sh --sim-tools
```

**The flag is not optional and it is easy to miss.** Without it you get
the compiler toolchain and no Gazebo. The script still prints "All set!",
the build still configures, and then it fails with:

```
Could NOT find gz-transport
ERROR: Gazebo simulation dependencies not found!
```

`--sim-tools` installs the `px4-sim` Homebrew formula, which pulls in
Gazebo Harmonic.

When it finishes, **quit and reopen your terminal.** The script modifies
your shell environment and the running session will not see it.

### 5. If you already built without `--sim-tools`

CMake caches the result of its dependency search. Rerunning the setup
script does not invalidate that cache, so the build will keep failing
with the identical error even after Gazebo is installed.

Delete the build directory:

```bash
rm -rf build/px4_sitl_default
```

### 6. Verify Gazebo before building

```bash
gz sim --versions
```

Should print `8.15.0`. If it prints nothing, `--sim-tools` did not take
and there is no point rebuilding.

### 7. Build

```bash
cd ~/PX4-Autopilot
source .venv/bin/activate
HEADLESS=1 make px4_sitl gz_x500
```

First build compiles roughly 1200 targets. 20 to 45 minutes on an M1
Pro. Later builds take seconds because ccache is enabled.

### 8. QGroundControl

Download the macOS build and install it. On first run:

- Preferred Firmware: **PX4 Pro**
- Preferred Vehicle: **Multi-Rotor**
- System of units: **Metric**

Metric matters. PX4, MAVLink, and every number in our code are metric.
`TAKEOFF_ALTITUDE = 3.0` is three meters. If QGC shows feet you will be
converting in your head every time you cross-check it against telemetry,
which is how scale errors survive.

---

## Why headless

We run without the Gazebo 3D window. This is deliberate.

Gazebo's GUI does not work reliably on Apple Silicon:

- With the default `ogre2` engine, the viewport detaches into a separate
  black `OgreWindow` and renders nothing.
- With `--render-engine ogre`, it segfaults. The GUI talks to Metal,
  `ogre` speaks OpenGL, and it dies handing a Metal texture ID to an
  OpenGL render target.
- On macOS `gz sim` cannot run server and GUI in one process at all. It
  says so explicitly and points at gz-sim issue #44.

None of this affects the simulation. Physics, sensors, EKF, and MAVLink
all run identically headless. The only thing missing is a 3D picture of
a quadcopter.

**QGroundControl is the better view anyway.** Map, altitude, attitude,
battery, GPS count, and flight mode, all over the same MAVLink link you
will use with the real aircraft.

If you genuinely want the 3D view, the reliable path is a Linux machine.
PX4 documents WSL2 as supported, and Gazebo works properly there with a
real GPU.

---

## Running it

One terminal:

```bash
cd ~/PX4-Autopilot
source .venv/bin/activate
HEADLESS=1 make px4_sitl gz_x500
```

Wait for the `pxh>` prompt. Then open QGroundControl and leave it
running.

Startup output worth recognizing:

```
INFO [mavlink] mode: Normal,   udp port 18570 remote port 14550
INFO [mavlink] mode: Onboard,  udp port 14580 remote port 14540
```

- **14550** is QGroundControl.
- **14540** is companion software. That is us. It is the port in
  `config.py`.

Do not point two things at the same port. They will fight and neither
works.

---

## Verifying it works

Run these at the `pxh>` prompt, in order, **before** involving any of our
own code. Each isolates a different layer.

```
commander status
```

Expect disarmed, with a navigation mode.

```
mavlink status
```

Expect several instances with nonzero `tx` rates. This proves MAVLink is
being published.

```
commander check
```

Expect `Preflight check: OK`. If it fails, see below.

```
commander takeoff
```

Watch QGroundControl. It arms, climbs to about 2.5 m, and reports
"Takeoff detected".

```
commander land
```

Lands and disarms itself. You will see "Disarmed by landing" without
asking for it, which is why our scripts can attempt a disarm and ignore
the refusal.

**When those pass, you have flown a simulated aircraft with none of our
code involved.** Everything after this is additive, and if something
breaks you know where it is not.

---

## Two preflight failures you will see

### "No connection to the GCS"

PX4 refuses to arm with no ground station attached. Start
QGroundControl, wait for `INFO [mavlink] partner IP: 127.0.0.1`, and
rerun `commander check`.

### "no heading reference"

The EKF has not converged. It fuses gyro, accelerometer, GPS, barometer
and magnetometer into a state estimate it trusts, and that takes a few
seconds of data.

This clears on its own. It is not a bug and it is not our code. It is the
autopilot declining to fly without knowing which way it is pointing, and
you will meet the same message on the real aircraft.

---

## Running our code against it

Leave SITL running. In a second terminal:

```bash
cd ~/vortex
uv run 01_telemetry.py
```

Then go back to the `pxh>` window and type `commander takeoff`. Watch
the altitude in your own script climb.

That is the real milestone: something we wrote observing something we
did not, over the protocol we will use on the actual aircraft.

---

## Shutting down

Ctrl-C at the `pxh>` prompt. If ports seem stuck on the next run, check
for orphaned processes:

```bash
ps aux | grep -E "px4|gz sim"
```

---

## Quick reference

| Step | Command |
|---|---|
| Build | `HEADLESS=1 make px4_sitl gz_x500` |
| Verify sim | `commander status`, `mavlink status`, `commander check` |
| Fly it | `commander takeoff`, `commander land` |
| Our code | `uv run 01_telemetry.py` |

| Problem | Cause |
|---|---|
| `Could NOT find gz-transport` | Missing `--sim-tools`, or stale build dir |
| Same error after installing Gazebo | Stale CMake cache, `rm -rf build/px4_sitl_default` |
| `Timed out waiting for Gazebo world` | GUI mode on macOS. Use `HEADLESS=1` |
| Black `OgreWindow` | Gazebo GUI on Apple Silicon. Use `HEADLESS=1` |
| `Arming denied` | Run `commander check` and read the reason |
| `LD: too many open files` | Missing `ulimit -S -n 2048` in `~/.zshrc` |