# HVAC/R Electrical Helper (Educational)

Python **stdlib-only** CLI for common field electrical checks:

- **Amps** — measured vs **FLA** / **RLA** with approximate high/low guidance
- **Capacitor** — rated vs measured µF (± practice bands), optional voltage note
- **Imbalance** — **1φ** (two legs) or **3φ** (NEMA-style % imbalance)
- **LRA notes** — locked-rotor vs running checklist with **LOTO** reminders

> **Educational only.** Not a substitute for OEM nameplate data, a calibrated meter, or lockout/tagout. Live electrical work is dangerous.

## Requirements

- Python 3.9+

## Quick start

```bash
cd hvac-electrical-helper
python3 electrical_helper.py --help
python3 electrical_helper.py -i
```

### Amps vs FLA/RLA

```bash
python3 electrical_helper.py amps --measured 14.2 --fla 16.0 --rla 12.8
```

### Capacitor check

```bash
python3 electrical_helper.py capacitor --rated-mfd 45 --measured-mfd 42.5 --voltage 370
```

### Voltage imbalance

```bash
# 3-phase
python3 electrical_helper.py imbalance --phases 3 --volts 240 238 242

# 1-phase (two readings)
python3 electrical_helper.py imbalance --phases 1 --volts 120 118
```

### Locked-rotor / running notes

```bash
python3 electrical_helper.py lra-notes --mode locked-rotor
python3 electrical_helper.py lra-notes --mode running
```
