#!/usr/bin/env python3
"""Educational HVAC/R electrical helper CLI (stdlib).

FLA/RLA amp compare, single-phase capacitor check, 1φ/3φ voltage imbalance,
locked-rotor vs running notes. NOT a substitute for OEM data or a meter.
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional, Sequence, Tuple

DISCLAIMER = (
    "EDUCATIONAL ONLY — not a substitute for OEM nameplate data, a calibrated "
    "meter, or lockout/tagout procedures.\n"
    "Live electrical work kills. Verify LOTO before opening panels. "
    "Follow local codes and manufacturer instructions."
)

LOTO = (
    "SAFETY / LOTO: De-energize, lock/tag disconnect, verify zero energy with "
    "a meter, and treat capacitors as charged until discharged per OEM procedure."
)


def pct_diff(measured: float, rated: float) -> float:
    if rated == 0:
        raise ValueError("Rated value cannot be 0.")
    return (measured - rated) / abs(rated) * 100.0


def amp_compare(fla: Optional[float], rla: Optional[float], measured: float) -> None:
    print("\n--- FLA / RLA vs measured amps ---")
    print(DISCLAIMER)
    print(f"Measured amps: {measured:.2f} A")
    if fla is not None:
        d = pct_diff(measured, fla)
        print(f"FLA (nameplate): {fla:.2f} A  |  delta {d:+.1f}%")
        if measured > fla * 1.10:
            note = "High vs FLA — check load, airflow, charge, voltage, and shorted windings (approx)."
        elif measured < fla * 0.70:
            note = "Low vs FLA — light load, wrong scale, or open path; verify meter/clamp (approx)."
        else:
            note = "Often near a common band vs FLA for many running compressors (approx)."
        print(f"[APPROXIMATE] {note}")
    if rla is not None:
        d = pct_diff(measured, rla)
        print(f"RLA (nameplate): {rla:.2f} A  |  delta {d:+.1f}%")
        if measured > rla * 1.15:
            note = "High vs RLA — suspect load/airflow/charge/voltage/mechanical bind (approx)."
        elif measured < rla * 0.75:
            note = "Low vs RLA — may be unloaded or metering issue (approx)."
        else:
            note = "Often near a common band vs RLA while running (approx)."
        print(f"[APPROXIMATE] {note}")
    if fla is None and rla is None:
        print("Provide --fla and/or --rla from the nameplate.")
    print()


def capacitor_check(rated_mfd: float, measured_mfd: float, voltage: Optional[float]) -> None:
    print("\n--- Single-phase capacitor check ---")
    print(DISCLAIMER)
    print(LOTO)
    d = pct_diff(measured_mfd, rated_mfd)
    print(f"Rated: {rated_mfd:.1f} µF  |  Measured: {measured_mfd:.1f} µF  |  delta {d:+.1f}%")
    if voltage is not None:
        print(f"Test/supply voltage noted: {voltage:.0f} V (informational)")
    if abs(d) <= 6:
        note = "Within a common ±6% practice band of rated (approx) — still confirm OEM tolerance."
    elif abs(d) <= 10:
        note = "Near edge of a common ±10% band (approx) — check OEM limit; consider replacement."
    else:
        note = "Outside a common ±10% practice band (approx) — suspect weak/failed capacitor."
    print(f"[APPROXIMATE] {note}")
    print("Tip: Discharge safely, remove from circuit for accurate µF reading when possible.")
    print()


def voltage_imbalance(legs: Sequence[float], phases: int) -> None:
    print(f"\n--- {phases}φ voltage imbalance ---")
    print(DISCLAIMER)
    if phases == 1:
        if len(legs) != 2:
            raise ValueError("1φ imbalance needs two readings (e.g. L1-N and L2-N, or two line readings).")
        a, b = legs
        avg = (a + b) / 2.0
        imb = abs(a - b) / avg * 100.0 if avg else 0.0
        print(f"Leg A: {a:.1f} V  |  Leg B: {b:.1f} V  |  avg {avg:.1f} V")
        print(f"Imbalance: {imb:.2f}%  ( |A−B| / avg × 100 )")
        if imb <= 2:
            note = "Low imbalance (approx) — often acceptable for many 1φ supplies."
        elif imb <= 5:
            note = "Moderate imbalance (approx) — investigate loose neutrals/connections/load."
        else:
            note = "High imbalance (approx) — check utility, open neutral, and connections."
    else:
        if len(legs) != 3:
            raise ValueError("3φ imbalance needs three line-to-line (or three phase) voltages.")
        avg = sum(legs) / 3.0
        max_dev = max(abs(v - avg) for v in legs)
        imb = (max_dev / avg * 100.0) if avg else 0.0
        print(
            f"Vab={legs[0]:.1f}  Vbc={legs[1]:.1f}  Vca={legs[2]:.1f}  |  avg {avg:.1f} V"
        )
        print(f"Imbalance: {imb:.2f}%  ( max|V−avg| / avg × 100 )")
        if imb <= 1:
            note = "Very low imbalance (approx) — often preferred for 3φ motors."
        elif imb <= 2:
            note = "Within a common ≤2% practice target for many 3φ motors (approx)."
        elif imb <= 3:
            note = "Elevated (approx) — heating risk rises; investigate soon."
        else:
            note = "High imbalance (approx) — can overheat motors; find cause before long run."
    print(f"[APPROXIMATE] {note}")
    print()


def locked_rotor_notes(mode: str) -> None:
    print("\n--- Locked-rotor vs running notes ---")
    print(DISCLAIMER)
    print(LOTO)
    print(f"Mode: {mode}")
    if mode == "locked-rotor":
        print(
            "Locked-rotor / start attempt (educational checklist):\n"
            "  - Confirm LOTO before any wiring work; use rated PPE for live checks.\n"
            "  - LRA on nameplate is a start-current reference — brief spikes are expected.\n"
            "  - If stuck high / won't start: check start/run capacitor, contactor, "
            "voltage under load, hard-start kit (if OEM-approved), and mechanical seize.\n"
            "  - Do not repeatedly bang a locked compressor — windings overheat fast.\n"
            "  - Next: measure winding ohms (power off), capacitor µF, and supply voltage."
        )
    else:
        print(
            "Running amp / voltage checks (educational checklist):\n"
            "  - Compare measured amps to RLA/FLA; note indoor/outdoor conditions.\n"
            "  - Check voltage at unit under load (not only at panel).\n"
            "  - 3φ: check imbalance and contactor pitting; 1φ: capacitor and start circuit.\n"
            "  - High amps + normal voltage → load/airflow/charge/mech; low voltage → feeders.\n"
            "  - Next: temp split, pressures (if certified), and OEM troubleshooting tree."
        )
    print()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Educational HVAC/R electrical helper (amps, capacitor, voltage imbalance, "
            "LRA notes). NOT a substitute for OEM data or a meter."
        )
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("amps", help="Compare measured amps to FLA and/or RLA")
    a.add_argument("--measured", type=float, required=True, help="Measured running amps")
    a.add_argument("--fla", type=float, help="Full-load amps from nameplate")
    a.add_argument("--rla", type=float, help="Rated-load amps from nameplate")

    c = sub.add_parser("capacitor", help="Single-phase capacitor µF check")
    c.add_argument("--rated-mfd", type=float, required=True)
    c.add_argument("--measured-mfd", type=float, required=True)
    c.add_argument("--voltage", type=float, help="Optional test/supply voltage note")

    v = sub.add_parser("imbalance", help="1φ or 3φ voltage imbalance")
    v.add_argument("--phases", type=int, choices=[1, 3], required=True)
    v.add_argument(
        "--volts",
        type=float,
        nargs="+",
        required=True,
        help="1φ: two voltages; 3φ: three line voltages",
    )

    l = sub.add_parser("lra-notes", help="Locked-rotor vs running checklist")
    l.add_argument(
        "--mode",
        choices=["locked-rotor", "running"],
        default="locked-rotor",
    )

    p.add_argument("-i", "--interactive", action="store_true", help="Prompt for a tool")
    return p


def interactive() -> int:
    print("HVAC/R electrical helper (educational)\n" + DISCLAIMER + "\n")
    print(LOTO + "\n")
    choice = input("Tool (amps|capacitor|imbalance|lra-notes) [amps]: ").strip().lower() or "amps"
    try:
        if choice == "amps":
            m = float(input("Measured amps: "))
            fla_s = input("FLA (blank to skip): ").strip()
            rla_s = input("RLA (blank to skip): ").strip()
            amp_compare(
                float(fla_s) if fla_s else None,
                float(rla_s) if rla_s else None,
                m,
            )
        elif choice == "capacitor":
            rated = float(input("Rated µF: "))
            measured = float(input("Measured µF: "))
            vnote = input("Voltage note (blank skip): ").strip()
            capacitor_check(rated, measured, float(vnote) if vnote else None)
        elif choice == "imbalance":
            ph = int(input("Phases 1 or 3 [3]: ").strip() or "3")
            if ph == 1:
                legs = [float(input("Voltage A: ")), float(input("Voltage B: "))]
            else:
                legs = [
                    float(input("Vab: ")),
                    float(input("Vbc: ")),
                    float(input("Vca: ")),
                ]
            voltage_imbalance(legs, ph)
        elif choice == "lra-notes":
            mode = input("Mode locked-rotor|running [locked-rotor]: ").strip() or "locked-rotor"
            locked_rotor_notes(mode)
        else:
            print("Unknown tool.", file=sys.stderr)
            return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    if argv is None and len(sys.argv) == 1:
        return interactive()
    args = parser.parse_args(argv)
    if getattr(args, "interactive", False) and args.cmd is None:
        return interactive()
    try:
        if args.cmd == "amps":
            if args.fla is None and args.rla is None:
                print("Error: provide --fla and/or --rla", file=sys.stderr)
                return 1
            amp_compare(args.fla, args.rla, args.measured)
        elif args.cmd == "capacitor":
            capacitor_check(args.rated_mfd, args.measured_mfd, args.voltage)
        elif args.cmd == "imbalance":
            voltage_imbalance(args.volts, args.phases)
        elif args.cmd == "lra-notes":
            locked_rotor_notes(args.mode)
        else:
            parser.print_help()
            return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raw = sys.argv[1:]
    if not raw or raw == ["-i"] or raw == ["--interactive"]:
        sys.exit(interactive())
    sys.exit(main())
