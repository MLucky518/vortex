# Vortex Security

Vortex controls or communicates with a physical aircraft.

Security failures therefore have potential safety consequences.

This document defines the security expectations for the Vortex project, identifies the current threat model, separates implemented protections from planned hardening, and provides requirements that should be reviewed before physical flight.

This document is expected to evolve as the system architecture becomes more complete.

---

# Security Goals

Vortex should be designed so that:

* unauthorized users cannot easily issue aircraft commands
* credentials and cryptographic keys are not exposed through Git
* the Raspberry Pi exposes only the services required by the project
* untrusted network devices cannot directly reach aircraft-control interfaces without a deliberate reason
* application inputs are validated before becoming flight commands
* compromise of one component does not automatically provide unrestricted control of every component
* security failures fail safely whenever practical
* simulator development does not accidentally create unsafe production defaults
* sensitive information does not leak through logs
* the team can identify and rotate compromised credentials

Security is treated as part of the architecture rather than something added immediately before the final demonstration.

---

# Current Security Status

Vortex is currently in development.

Not every protection described in this document has been implemented.

Sections labeled **Required before physical flight** or **Planned** describe hardening work that must be evaluated later.

Do not claim a planned control is currently active unless it has been implemented and tested.

---

# Threat Model

The project should consider at least the following attacker positions.

## Network attacker

Someone who can communicate with the Raspberry Pi, telemetry network, Wi-Fi network, or MAVLink connection.

Potential goals include:

* connecting to exposed services
* sending unauthorized aircraft commands
* changing configuration
* observing telemetry
* disrupting communication

## Local Raspberry Pi user

Someone who has obtained an account or shell on the companion computer.

Potential goals include:

* modifying Vortex
* reading secrets
* changing configuration
* launching unauthorized applications
* accessing the Pixhawk communication device

Linux permissions and service isolation should limit what an unprivileged user can access.

## Repository attacker

Someone who attempts to introduce malicious or unsafe code through source control.

Potential vectors include:

* compromised credentials
* unsafe pull requests
* malicious dependency changes
* accidentally committed secrets
* unauthorized configuration changes

## Malformed or unexpected input

Not every security problem requires a malicious attacker.

Incorrect coordinates, invalid configuration, unexpected telemetry, or programming mistakes may result in unsafe behavior unless values are validated.

## Physical attacker

Someone with physical access to the Raspberry Pi, Pixhawk, storage media, debug interfaces, wiring, or radios.

Physical access is a significantly stronger attacker position than network access.

Some protections that are effective against remote attackers may not protect a device that an attacker can physically disassemble.

---

# Secrets

## Never commit secrets

The repository must never contain real:

* passwords
* private keys
* MAVLink signing keys
* Wi-Fi credentials
* API tokens
* GitHub tokens
* SSH private keys
* other authentication credentials

This includes source files, documentation examples, test fixtures, and Git history.

---

# Environment Files

The repository contains:

```text
.env.default
```

This file is safe to commit.

It documents supported environment variables and contains only safe development values or placeholders.

Developers create:

```text
.env
```

for machine-specific configuration.

The local `.env` file must be excluded from Git.

A typical pattern is:

```gitignore
.env
```

If more environment-file naming conventions are introduced later, the ignore rules must be reviewed so that local secret-containing variants cannot accidentally be committed.

---

# `.env.default`

`.env.default` may contain:

```dotenv
DRONE_ADDRESS=udpin://0.0.0.0:14540
```

or placeholders such as:

```dotenv
SOME_SECRET=
```

It must never contain the real secret.

The purpose of the template is to tell developers:

> This configuration variable exists.

It is not a place to distribute credentials.

---

# GitHub Secrets

Secrets required specifically by GitHub Actions or another GitHub-hosted automation process should be stored using GitHub's secret-management features rather than committed to repository files.

A GitHub Actions secret only makes the secret available to the GitHub workflow in which it is explicitly used.

It does not automatically make the value available to the physical Raspberry Pi.

Secrets for the aircraft therefore require their own deployment and storage strategy.

---

# Raspberry Pi Secrets

Production or aircraft-specific secrets should eventually be stored outside the source repository with restrictive Linux permissions.

For example, Vortex may eventually use a protected runtime configuration location such as:

```text
/etc/vortex/
```

The exact production secret-management design should be chosen after the Raspberry Pi deployment architecture is finalized.

Requirements include:

* files containing secrets should not be world-readable
* the Vortex service should receive only secrets it actually requires
* secrets should not be printed to the terminal
* secrets should not appear in normal logs
* backup copies should be protected
* exposed secrets should be replaced rather than trusted again

---

# Secret Rotation

If a real credential or signing key is:

* committed to Git
* pasted into public chat
* included in a screenshot
* placed in a public log
* shared with an unauthorized person
* otherwise potentially exposed

it must be considered compromised.

Deleting the visible line is not sufficient if the value may still exist in Git history, caches, screenshots, logs, or clones.

The credential should be revoked or replaced.

---

# MAVLink Security

Vortex communicates with PX4 using MAVLink.

MAVLink should be treated as a security boundary.

Development behavior and production behavior may differ.

## Development

Unsigned MAVLink communication may be used while developing against local PX4 SITL.

Development convenience must not automatically become the physical-aircraft security policy.

## Physical aircraft

Before physical deployment, the team must review the security configuration of every MAVLink communication path.

This includes communication between:

```text
Raspberry Pi <-> Pixhawk
Ground station <-> Pixhawk
Telemetry radio <-> vehicle
Other MAVLink-capable devices <-> vehicle
```

---

# MAVLink Message Signing

MAVLink 2 supports message signing.

Signing allows a receiver to verify that a MAVLink packet was produced by a system possessing the shared signing key and helps protect against forged and replayed commands.

Message signing provides authentication and integrity.

It does **not** encrypt MAVLink telemetry.

An observer who can capture the communication may still be able to read unencrypted information even when message signing is enabled.

## Planned

Before enabling signing on the physical aircraft, the team must verify compatibility between:

* PX4
* MAVSDK
* QGroundControl
* the Raspberry Pi companion software
* any telemetry hardware
* any other MAVLink participant

The signing key must not be committed to Git.

Initial key provisioning should occur through a trusted connection.

Key-loss and recovery procedures should be understood before enabling signing on an aircraft required for a graded demonstration.

---

# Network Exposure

MAVLink ports should not be exposed to untrusted networks or directly to the public internet.

The team should understand which interfaces a listening service is bound to.

For example:

```text
0.0.0.0
```

typically means listening on all available network interfaces.

That can be convenient during development but may expose a service more broadly than intended.

```text
127.0.0.1
```

limits IPv4 communication to the local computer.

## SITL TODO

The current SITL configuration uses:

```text
udpin://0.0.0.0:14540
```

Before changing this, verify how PX4 SITL, MAVSDK, and any ground-control software are being run.

If every relevant process is running on the same development computer, evaluate whether the connection can be bound more narrowly.

If communication intentionally crosses machines, network access should be restricted through the host firewall and trusted network configuration.

---

# Raspberry Pi Hardening

The Raspberry Pi should be treated as an aircraft-control computer rather than a general-purpose shared desktop.

## Required before physical flight

Review the following.

### Updates

Install supported operating-system security updates before the final deployment configuration is frozen.

### Default credentials

No default passwords should remain.

### SSH

Remote administration should preferably use SSH keys.

Before physical deployment, evaluate:

* disabling root SSH login
* disabling password-based SSH authentication
* limiting which users may connect
* removing unused authorized keys

Do not disable the team's only working access mechanism until another verified recovery path exists.

### Least privilege

Vortex should not run as `root` simply because doing so is convenient.

A dedicated service account should be considered.

That account should receive only the permissions required to:

* run Vortex
* read its configuration
* access the required Pixhawk serial device
* access specifically required hardware

### Sudo

The Vortex runtime account should not receive unrestricted passwordless sudo.

### Unnecessary services

Services that are not required by the aircraft should be disabled where practical.

Every listening service increases attack surface.

### Firewall

Once the required network traffic is known, configure the host firewall to permit only necessary inbound connections.

Do not write firewall rules until the team's real development and ground-station network requirements are understood.

### File permissions

Sensitive configuration should be readable only by the accounts that need it.

### Service management

The final application should eventually be considered for execution through a Linux service manager such as `systemd`.

This would allow the team to control:

* which user runs Vortex
* startup behavior
* restart behavior
* environment configuration
* filesystem access
* resource limits
* service isolation

Additional `systemd` hardening should be introduced incrementally and tested rather than enabled blindly.

---

# Application-Level Safety and Security

The Python application should not blindly trust every value simply because it came from configuration or another part of the program.

As flight functionality is introduced, Vortex should validate important values before issuing aircraft commands.

Examples may include:

```text
minimum altitude
maximum altitude
maximum mission distance
maximum velocity
allowed flight modes
valid coordinates
expected connection state
vehicle health requirements
```

Exact limits must be chosen based on the aircraft, testing environment, assignment, and instructor requirements.

---

# Mission Limits

Mission configuration such as:

```python
TAKEOFF_ALTITUDE = 3.0
SQUARE_SIDE = 5.0
```

does not need to be secret.

Security does not come from hiding these numbers.

Instead, Vortex should eventually distinguish between:

```text
requested behavior
```

and:

```text
absolute safety limits
```

For example:

```text
Requested takeoff altitude: 3 m
Maximum permitted altitude: determined safety limit
```

A requested value outside an allowed range should be rejected rather than silently forwarded to the aircraft.

---

# Fail Closed Where Practical

If Vortex cannot determine that a requested operation is valid, the preferred behavior should generally be to reject the command rather than guess.

Examples include:

* malformed coordinates
* missing required configuration
* impossible mission geometry
* connection ambiguity
* failed prerequisite checks

The exact response to an in-flight failure must account for PX4's own failsafe behavior and should not be invented solely at the Python layer.

PX4 remains responsible for its configured flight-controller failsafes.

---

# Input Validation

Any future external interface to Vortex must be considered untrusted by default.

This becomes especially important if the project later adds:

* HTTP APIs
* web interfaces
* network command sockets
* remote mission uploads
* user-entered coordinates
* autonomous planning systems
* camera or AI-generated decisions

Do not turn arbitrary network input directly into flight commands.

Inputs should be parsed, validated, bounded, and converted into an internal representation before they reach MAVSDK.

---

# Separation of Responsibilities

Prefer an architecture such as:

```text
untrusted input
      |
      v
validation
      |
      v
mission logic
      |
      v
safety checks
      |
      v
MAVSDK adapter
      |
      v
PX4
```

rather than:

```text
untrusted input
      |
      v
MAVSDK
      |
      v
PX4
```

This separation also makes security behavior easier to test.

---

# Logging

Logs are useful for debugging but can create their own security problem.

Do not log:

* passwords
* private keys
* signing keys
* authentication tokens
* complete secret-containing environment dumps

Be cautious about logging:

* precise location history
* network configuration
* personally identifying information
* sensitive mission information

Telemetry logs needed for the class project should be stored intentionally rather than left scattered across user directories.

---

# Dependency Security

Vortex uses `uv` for dependency management.

The project should commit the lockfile so team members and automated systems resolve a consistent dependency graph.

Dependency changes should be deliberate.

Before adding a package, consider:

* why the dependency is required
* whether it is maintained
* whether the project can reasonably avoid it
* whether it introduces native/system dependencies
* whether it will run on Raspberry Pi ARM64

Do not add packages only because a random troubleshooting answer says to install them.

---

# Source-Control Security

Repository access should follow least privilege.

As team collaboration grows, consider:

* protecting the primary branch
* requiring pull requests for important changes
* reviewing dependency updates
* reviewing aircraft configuration changes
* preventing force-pushes to important branches
* using GitHub secret scanning where available
* enabling appropriate account multi-factor authentication

Changes involving safety limits, security settings, deployment configuration, or flight behavior deserve particularly careful review.

---

# Code Review

Flight-control code should be understandable by more than one person.

Avoid important behavior that exists only in one team member's local files or memory.

Security-critical assumptions should be:

* represented in code
* documented
* tested where practical

For example, the NED coordinate convention should be represented by tests rather than relying on every developer to remember that positive `down` means downward.

---

# Physical Security

Physical possession of the aircraft is a powerful attacker position.

Potentially exposed components include:

* Raspberry Pi storage
* Pixhawk SD card
* USB ports
* serial interfaces
* debug interfaces
* telemetry hardware

Software protections alone cannot fully defend against an attacker with unrestricted physical access to the hardware.

Before final testing:

* keep the aircraft under team control
* do not leave secret-bearing removable storage unattended
* protect unnecessary physical interfaces where practical
* understand how a device can be recovered if configuration is damaged

---

# Development vs. Aircraft Configuration

Development defaults should not automatically be considered production defaults.

For example:

```text
SITL
    permissive local development configuration

Physical aircraft
    deliberately reviewed configuration
```

Before moving software from simulation to the Raspberry Pi, review:

* connection addresses
* network bindings
* secrets
* logging
* user permissions
* MAVLink security
* safety limits
* PX4 failsafes
* startup behavior

---

# Security Testing

Security testing should begin in simulation where practical.

Potential defensive tests include:

* invalid altitude rejected
* invalid coordinates rejected
* missing required configuration handled safely
* unexpected environment value rejected
* mission exceeding configured bounds rejected
* application does not print secrets
* non-required network services are unreachable
* Vortex service does not run with unnecessary privileges

Security tests should be reproducible rather than dependent only on manually attempting an attack.

---

# Preflight Security Review

Before the first physical autonomous flight, verify at minimum:

```text
[ ] No real secrets are committed to Git
[ ] .env is ignored
[ ] Aircraft-specific credentials are protected
[ ] Raspberry Pi default credentials are removed
[ ] Raspberry Pi remote-access configuration has been reviewed
[ ] Unnecessary network services are disabled
[ ] Firewall requirements have been reviewed
[ ] MAVLink network exposure is understood
[ ] MAVLink signing decision has been documented
[ ] Pixhawk-to-Pi communication path has been verified
[ ] Application safety limits have been reviewed
[ ] PX4 failsafes have been configured and tested
[ ] Manual recovery / safety-pilot requirements are understood
[ ] Simulator testing has passed
[ ] Physical test area has been approved
[ ] Team knows how to immediately stop or recover the aircraft
```

This checklist should become more specific as Vortex develops.

---

# Incident Response

If a security problem is discovered:

1. stop physical flight testing if the issue could affect aircraft control
2. preserve enough information to understand what happened
3. disconnect unnecessary network access
4. revoke or rotate potentially exposed credentials
5. reproduce the issue in SITL when practical
6. fix the root cause
7. add a regression test when the issue can be tested automatically
8. review whether the same weakness exists elsewhere
9. retest before returning to physical flight

Do not simply hide evidence of a security problem so the demonstration can continue.

---

# Hardening Roadmap

## Development phase

* keep secrets out of Git
* use `.env.default` for safe templates
* maintain dependency lockfile
* separate pure logic from MAVLink communication
* validate mission inputs
* add automated tests

## SITL integration phase

* understand all listening network ports
* minimize unnecessary network exposure
* test malformed mission input
* verify failure behavior
* identify assumptions that differ from real hardware

## Raspberry Pi phase

* create deliberate Linux user and permission model
* configure SSH
* configure firewall
* protect runtime configuration
* restrict serial-device access
* configure Vortex as a service
* remove unnecessary services

## Aircraft-integration phase

* review every MAVLink link
* evaluate and test MAVLink 2 signing
* secure signing keys
* verify QGroundControl compatibility
* verify companion-computer compatibility
* verify PX4 failsafes
* establish manual recovery procedure

## Final phase

* perform security checklist
* perform safety checklist
* freeze known-good configuration
* tag the demonstrated source revision
* document any remaining known limitations

---

# References

Security decisions involving PX4 and MAVLink should be verified against current official documentation before the final aircraft configuration is frozen.

Useful official documentation includes:

* PX4 Guide — **MAVLink Security Hardening for Production Deployments**
* PX4 Guide — **MAVLink Messaging**
* MAVLink Guide — **Message Signing (Authentication)**

The project should not rely on security advice copied from random forum posts when official protocol or firmware documentation exists.
