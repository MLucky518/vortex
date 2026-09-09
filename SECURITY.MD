# Security

This aircraft can be commanded over a network. Security failures here are
safety failures.

The professor has said next semester's course involves attacking these
drones. This document is what we know is exposed today and what has to be
fixed before anything flies. It is deliberately short. It will grow when
there is something real to add.

**Safety beats security.** Do not harden your way out of a manual
override or a failsafe. A drone nobody can take control of is worse than
one somebody else can.

## Known exposure, today

**MAVLink is unauthenticated by default.** PX4's docs are blunt about
what that means: any device that can send MAVLink to the vehicle can
issue commands, including shell access, file operations, and flight
termination. This is the main attack.

**We bind to all interfaces.** `.env.default` uses
`udpin://0.0.0.0:14540`. That accepts connections on every network
interface. Harmless in simulation on one machine. On a Pi with wifi in a
classroom, it is an open port that accepts flight commands. Narrow it
once we know whether the Pi and the ground station are on the same box.

## Secrets

Never commit real passwords, private keys, MAVLink signing keys, wifi
credentials, or tokens. Not to source, not to docs, not to test
fixtures. Git history counts.

`.env.default` is a committed template with safe values and empty
placeholders. `.env` is local and gitignored. Verify with:

```bash
git check-ignore -v .env
```

Silence means it is tracked. Fix that immediately.

If a real secret is ever committed, pasted in chat, or screenshotted,
treat it as compromised and replace it. Deleting the line does not
remove it from history.

## MAVLink signing

MAVLink 2 supports message signing: a shared key lets the receiver verify
a packet came from a system holding that key. PX4 supports it via the
`MAV_SIGN_CFG` parameter, no special build required.

Signing is authentication, not encryption. Traffic remains readable to
anyone listening.

Two things to understand before enabling it on the aircraft:

- **Key loss is recovered physically only.** Pull the SD card and delete
  the key file, or reflash. There is no software path back in. On a
  five-person team someone will lose the key, so decide where it lives
  before provisioning it.
- **Some messages are always accepted unsigned**, including `HEARTBEAT`.
  That is deliberate, so you cannot lock yourself out of your own
  aircraft.

Decision deferred until the aircraft exists. Do not enable it in the
middle of the build.

## Before physical flight

**Raspberry Pi**

- [ ] OS updated
- [ ] No default credentials
- [ ] SSH keys only, password auth disabled
- [ ] Vortex runs as a dedicated user, not root
- [ ] Unneeded services off
- [ ] Firewall configured once we know what traffic is actually required

Do not disable the only working access method until another one is
verified. Locking yourself out of a Pi at the college, an hour away, is
its own kind of incident.

**Checklist**

- [ ] No secrets in Git
- [ ] `.env` ignored
- [ ] MAVLink network exposure understood and narrowed
- [ ] Signing decision documented either way
- [ ] Pi to Pixhawk path verified
- [ ] PX4 failsafes configured and tested
- [ ] RC link and safety pilot in place
- [ ] Simulator testing passed
- [ ] Test area approved
- [ ] Everyone knows how to stop the aircraft immediately

## Application safety

As flight code lands, validate before commanding. A requested altitude or
distance outside a configured limit should be rejected, not forwarded.

`TAKEOFF_ALTITUDE` and `SQUARE_SIDE` are not secrets. Security does not
come from hiding numbers. It comes from the aircraft refusing values it
should not accept.

PX4 owns its own failsafes. Do not reinvent them in Python.

## Physical access

Anyone holding the aircraft can read the SD card. Assume physical access
means full compromise and do not store anything on the card you cannot
afford to lose.

## References

- PX4 Guide, MAVLink Security Hardening for Production Deployments
- MAVLink Guide, Message Signing

Verify against current official docs before freezing the aircraft
configuration. Not forum posts.