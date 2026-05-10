import json
from pathlib import Path
import pytest
from core.calculator_iso16358 import ISO16358Calculator

# Import helpers from existing test file
from tests.test_iso16358_hspf_golden import (
    load_iso_hspf_golden_fixture,
    make_iso_common_golden_calculator,
    iso_common_golden_measured_inputs,
    iso_common_golden_actuals
)

def get_formula_family(case_name):
    """Categorize the P_j formula family based on the branch case name."""
    if case_name == "cycling":
        return "cycling"
    if "min_half" in case_name:
        return "min-half"
    if case_name == "interpolation":
        return "half-full (capacity-linear)"
    if "formula50" in case_name:
        return "full-extended (F50 COP-linear)"
    if "formula47" in case_name:
        return "full-extended (F47 COP-linear)"
    if case_name == "saturated":
        return "saturated/auxiliary"
    return "unknown"

def trace_case(calculator, case):
    """Execute a single case and return detailed trace data."""
    measured = iso_common_golden_measured_inputs(case)
    result = calculator.calculate_hspf(measured)
    
    # Capture inputs and common actuals
    actuals = iso_common_golden_actuals(result)
    
    # Task 1: Point Trace summary
    point_trace = {
        "case_id": case["case_id"],
        "label": case["label"],
        "measured_keys": list(measured.keys()),
        "actual_results": actuals,
    }
    
    # Task 2: Bin-level Branch Trace
    bin_traces = []
    for detail in result.get("bin_details", []):
        if detail["nj"] <= 0:
            continue
        
        # Capture more details from calculator internal trace if possible
        # Some fields like 'tg', 'tf', 'pi_ext_f' are in the trace dict merged into bin_details
        
        bin_traces.append({
            "tj": detail["tj"],
            "nj": detail["nj"],
            "bl_h": detail["bl_h"],
            "case": detail["case"],
            "pi_j": detail["pi_j"],
            "P_j": detail["P_j"],
            "E_j": detail["E_j"],
            "auxiliary_energy": detail["auxiliary_energy"],
            "frost": -7.0 < detail["tj"] < 5.5,
            "family": get_formula_family(detail["case"]),
            "cap_full": detail.get("cap_rated") or detail.get("phi_full"),
            "pwr_full": detail.get("power_rated"),
            "cap_half": detail.get("cap_intermediate") or detail.get("phi_half"),
            "pwr_half": detail.get("power_intermediate"),
            "pi_ext_f": detail.get("pi_ext_f"),
            # Capture Formula 50 internals from trace dict
            "tg": detail.get("tg"),
            "tf": detail.get("tf"),
            "cop_fe_f": detail.get("cop_fe_f")
        })
        
    return point_trace, bin_traces

@pytest.mark.parametrize("case", load_iso_hspf_golden_fixture()["cases"])
def test_iso16358_hspf_h8_trace_audit(tmp_path, case):
    """
    Current behavior audit trace for ISO 16358-2 HSPF Golden Cases 1-8.
    This test is non-invasive and does not change results.
    """
    calculator = make_iso_common_golden_calculator(tmp_path)
    point_trace, bin_traces = trace_case(calculator, case)
    
    print(f"\n[TRACE] Case {point_trace['case_id']}: {point_trace['label']}")
    print(f"[TRACE] Actual Results: HSPF={point_trace['actual_results']['hspf']:.3f}, "
          f"HSEC={point_trace['actual_results']['hsec_kwh']:.2f}")
    
    # Display interesting bins
    print("| tj | nj | load | pi_full | Branch | P_j | Family | TF | COP_FE |")
    for bt in bin_traces:
        if bt["tj"] in [-1.0, 0.0, 1.0, 2.0, 6.0, 7.0]:
             tj = bt["tj"]
             nj = bt["nj"]
             load = bt["bl_h"]
             cap_full = bt.get("cap_full")
             cap_str = f"{cap_full:.1f}" if cap_full is not None else "N/A"
             case_name = bt["case"]
             pj = bt["P_j"]
             family = bt["family"]
             tf = bt.get("tf")
             tf_str = f"{tf:.2f}" if tf is not None else "N/A"
             cop = bt.get("cop_fe_f")
             cop_str = f"{cop:.2f}" if cop is not None else "N/A"
             print(f"| {tj} | {nj} | {load:.1f} | {cap_str} | {case_name} | {pj:.2f} | {family} | {tf_str} | {cop_str} |")

def test_iso16358_hspf_h8_case3_4_5_flip_audit(tmp_path):
    """
    Detailed audit of branch flips between Case 3, 4, and 5.
    """
    calculator = make_iso_common_golden_calculator(tmp_path)
    fixture = load_iso_hspf_golden_fixture()
    cases = {c["case_id"]: c for c in fixture["cases"]}
    
    results = {}
    traces = {}
    for cid in [3, 4, 5]:
        point_trace, bin_traces = trace_case(calculator, cases[cid])
        results[cid] = point_trace["actual_results"]
        traces[cid] = {bt["tj"]: bt for bt in bin_traces}

    print("\n[FLIP AUDIT] Comparing tj=2.0 (Frost Boundary)")
    for cid in [3, 4, 5]:
        bt = traces[cid][2.0]
        print(f"Case {cid}: Load={bt['bl_h']:.1f}, Full={bt['cap_full'] if bt['cap_full'] else 'N/A'}, "
              f"Branch={bt['case']}, P_j={bt['P_j']:.2f}, Family={bt['family']}")

    print("\n[FLIP AUDIT] Comparing tj=1.0")
    for cid in [3, 4, 5]:
        bt = traces[cid][1.0]
        print(f"Case {cid}: Load={bt['bl_h']:.1f}, Full={bt['cap_full'] if bt['cap_full'] else 'N/A'}, "
              f"Branch={bt['case']}, P_j={bt['P_j']:.2f}, Family={bt['family']}")

def test_iso16358_hspf_h8_invariants_audit(tmp_path):
    """
    Verify current behavior invariants as a baseline for H-8 implementation.
    """
    calculator = make_iso_common_golden_calculator(tmp_path)
    fixture = load_iso_hspf_golden_fixture()
    cases = {c["case_id"]: c for c in fixture["cases"]}
    
    results = {}
    for cid in [3, 4, 5, 6, 7, 8]:
        measured = iso_common_golden_measured_inputs(cases[cid])
        results[cid] = calculator.calculate_hspf(measured)
    
    # Invariant 1: Case 4/5 actual vs Case 3 (Current behavior: Frost points used if available)
    c3_hsec = results[3]["hsec_wh"]
    c4_hsec = results[4]["hsec_wh"]
    c5_hsec = results[5]["hsec_wh"]
    
    print(f"\n[INVARIANT] Case 3 HSEC: {c3_hsec:.2f}")
    print(f"[INVARIANT] Case 4 HSEC: {c4_hsec:.2f} (Diff vs C3: {c4_hsec - c3_hsec:.2f})")
    print(f"[INVARIANT] Case 5 HSEC: {c5_hsec:.2f} (Diff vs C4: {c5_hsec - c4_hsec:.2f})")
    
    if abs(c4_hsec - c3_hsec) > 1e-6:
        print("[INVARIANT] Case 4 is now DIFFERENT from Case 3 (2_full reflected).")
        
    if abs(c5_hsec - c4_hsec) > 1e-6:
        print("[INVARIANT] Case 5 is now DIFFERENT from Case 4 (2_half reflected).")

    # Invariant 2: Case 6/7/8 changes with -7 points
    c6_hsec = results[6]["hsec_wh"]
    c7_hsec = results[7]["hsec_wh"]
    c8_hsec = results[8]["hsec_wh"]
    
    print(f"[INVARIANT] Case 6 HSEC: {c6_hsec:.2f} (Diff vs C5: {c6_hsec - c5_hsec:.2f})")
    print(f"[INVARIANT] Case 7 HSEC: {c7_hsec:.2f} (Diff vs C6: {c7_hsec - c6_hsec:.2f})")
    print(f"[INVARIANT] Case 8 HSEC: {c8_hsec:.2f} (Diff vs C7: {c8_hsec - c7_hsec:.2f})")
    
    # Basic check for bin details existence
    for cid, res in results.items():
        assert "bin_details" in res
        assert len(res["bin_details"]) > 0
        first_bin = res["bin_details"][0]
        assert "case" in first_bin
        assert "P_j" in first_bin
