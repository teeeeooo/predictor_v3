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
    
    # Task 1: Point Resolution Trace (Simulated as we can't easily reach internal 'resolved' dict 
    # without modifying core, so we look at the inputs provided to calculate_hspf)
    point_trace = {
        "case_id": case["case_id"],
        "label": case["label"],
        "measured_keys": list(measured.keys()),
        "actual_results": actuals
    }
    
    # Task 2: Bin-level Branch Trace
    bin_traces = []
    for detail in result.get("bin_details", []):
        if detail["nj"] <= 0:
            continue
        
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
            "family": get_formula_family(detail["case"])
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
    print(f"[TRACE] Measured Inputs: {point_trace['measured_keys']}")
    print(f"[TRACE] Actual Results: HSPF={point_trace['actual_results']['hspf']:.3f}, "
          f"HSTL={point_trace['actual_results']['hstl_kwh']:.2f}, "
          f"HSEC={point_trace['actual_results']['hsec_kwh']:.2f}")
    
    # Display top 3 bins by energy or specific interesting temps
    print("| tj | nj | load | Branch | P_j | Family |")
    # Focus on tj=2 (frost) and tj=7 (non-frost)
    for bt in bin_traces:
        if bt["tj"] in [2.0, 7.0, -1.0]:
             print(f"| {bt['tj']} | {bt['nj']} | {bt['bl_h']:.1f} | {bt['case']} | {bt['P_j']:.2f} | {bt['family']} |")

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
    
    # Invariant 1: Case 4/5 actual matches Case 3 (Current behavior: Frost points ignored)
    c3_hsec = results[3]["hsec_wh"]
    c4_hsec = results[4]["hsec_wh"]
    c5_hsec = results[5]["hsec_wh"]
    
    print(f"\n[INVARIANT] Case 3 HSEC: {c3_hsec:.2f}")
    print(f"[INVARIANT] Case 4 HSEC: {c4_hsec:.2f} (Diff: {c4_hsec - c3_hsec:.2f})")
    print(f"[INVARIANT] Case 5 HSEC: {c5_hsec:.2f} (Diff: {c5_hsec - c3_hsec:.2f})")
    
    if abs(c4_hsec - c3_hsec) < 1e-6 and abs(c5_hsec - c3_hsec) < 1e-6:
        print("[INVARIANT] Current behavior confirmed: Frost points (2_full, 2_half) are effectively IGNORED.")
        
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
