# HVAC Physical Constraints for ML

Purpose: collect HVAC physical sanity check ideas that can guide ML feature review, model constraints, result interpretation, and data quality review.

Boundary: this document is for ML behavior only. It must not be used as calculator formula authority or as justification for changing calculator formulas, fixtures, region configs, or golden expected values.

Any equations here are approximate ML sanity-check heuristics, not calculator formulas or standards references.

## Guide

### Constraint severity

Use hard constraints only for physically impossible regions, not for ordinary operating tendencies.

Hard constraint or sanity fail candidates:
- Discharge gas temperature below condensing temperature.
- Absolute temperature below 0 K.
- Predicted COP above a plausible Carnot-bound region.

Treat trend-based rules as soft guidance. Monotonicity, capacity/power tendencies, airflow relationships, and compressor frequency tendencies can be useful for ML review, but real data may include sensor noise, control hunting, thermal inertia, transient behavior, or protection control.

Negative superheat or subcooling should usually be treated as an outlier review flag rather than an immediate hard fail. Small negative values may be retained or flagged for review instead of strictly dropped. A configurable tolerance margin should be applied during preprocessing to account for sensor thermal lag, pipe mounting variance, and temporary EEV hunting.

### Cooling mode physical tendencies

As ambient temperature rises, cooling capacity generally decreases, input power generally increases, and COP generally decreases. At extreme high ambient conditions, compressor discharge temperature protection, inverter protection, or derating may reduce both capacity and power.

As return air temperature or wet-bulb temperature rises, cooling capacity and input power may increase. COP can improve initially if capacity rises faster than power, but saturation or current limit control can stop further capacity gain.

As airflow increases, heat exchanger effectiveness can improve and capacity may increase. Compressor power may decrease slightly, but fan power can rise quickly, so total system COP depends on fan and system behavior. Excess airflow can reduce total COP if fan power growth dominates.

### Heating mode physical tendencies

As ambient temperature falls, heating capacity and COP generally decrease. Input power is not always monotonic with ambient temperature. Fixed-speed systems, inverter compensation, and extreme low-temperature protection can produce different power trends.

Frosting and defrost can create strong nonlinear behavior. During defrost, delivered heating capacity may fall to zero or become effectively negative while power is still consumed.

Heating airflow behavior may resemble cooling in heat exchanger terms, but comfort constraints and control logic can limit how airflow is used.

### Airflow and static pressure relationships

At the same fan command or target RPM, higher external static pressure generally reduces airflow.

If airflow and static pressure both increase while fan power or actual RPM stays flat or decreases, the row should be reviewed. Fan command, target RPM, and measured RPM should be kept separate because motor type and control logic can change the observed relationship.

Fan-law style relationships are rule-of-thumb sanity checks only. Fan power may rise sharply with RPM, while capacity often increases more gradually. Wet coil conditions can change pressure drop and airflow behavior.

### Compressor, power, and capacity relationships

Within normal operating ranges, compressor frequency usually has a global increasing tendency with power and capacity. This is a monotonicity candidate, not an automatic hard constraint.

At high-frequency saturation, capacity can flatten while power rises sharply. Protection controls such as discharge temperature protection, EEV intervention, phase current limit, or inverter derating can break the usual mapping between frequency, power, and capacity.

### COP and efficiency sanity checks

COP is approximately capacity divided by power for ML sanity review. This relationship is a rule-of-thumb feature check, not a calculator formula.

A lower COP at a high-load point can be physically normal if power rises faster than capacity. A higher COP at part load can also be normal if power falls faster than capacity.

If ambient condition, indoor condition, and compressor frequency are fixed in a steady-state region, sustained behavior where capacity increases while power decreases should be reviewed as a possible sanity fail or transient/chamber issue.

### ML Architecture Boundary: Point Prediction vs. Seasonal Efficiency

Single operating point performance and seasonal efficiency are not necessarily monotonic with each other.

Seasonal efficiency metrics such as CSPF, HSPF, SEER, and SCOP aggregate multiple operating points through bin-hour weighting, cycling loss, and related rule-based adjustments. In heating, avoiding backup resistance heater operation can improve seasonal efficiency even if a specific low-temperature heat pump COP point becomes worse.

ML point prediction should remain separate from deterministic seasonal calculation. ML models may predict point-level capacity and input power, while seasonal efficiency aggregation should be handled by the appropriate rule-based calculator path.

This section is an ML architecture boundary note only. It is not a basis for changing calculator formulas, golden expected values, or region configs.

### When monotonicity can break

Monotonicity can break due to:
- Transient test conditions before steady state.
- Control logic such as oil recovery, discharge temperature protection, low-pressure protection, or current limits.
- Sensor or chamber issues such as sensor placement, thermal lag, contact problems, or short-circuiting airflow.
- Wet coil, dry coil, frosting, and defrost state changes.
- Saturation at high compressor frequency or fan operating limits.

## Practical ML implications

Use hard constraints sparingly. Reserve them for physically impossible predictions or clear sanity fail regions.

Use soft warnings, custom loss penalties, smoothing, or feature review for trend-based rules. Do not force strict monotonic constraints where local noise, control logic, or operating state can create valid exceptions.

Use outlier review flags for rows that may represent sensor artifacts, transient behavior, abnormal system state, or test condition mismatch. Do not automatically delete such rows without review.

Separate feature engineering hints from calculator contracts. Derived features such as temperature differences, enthalpy-like context, airflow ratios, fan command/RPM separation, or capacity-power ratios can help ML models, but they do not redefine calculator input/output schema.

Avoid end-to-end monotonic assumptions between point-level COP and seasonal efficiency. Optimize or evaluate seasonal metrics through the appropriate deterministic aggregation layer, not by forcing one operating point metric to move monotonically with the final seasonal result.

## Source interview summary

This document summarizes domain knowledge gathered through a grill-me style interview with the user.

Key background:
- HVAC chamber data can contain valid local exceptions caused by control behavior, sensor lag, transient state, wet coil, frosting, and protection logic.
- Hard constraints are safest when limited to physically impossible regions.
- Monotonicity is useful as an ML review concept, but strict algorithmic constraints can underfit real inverter and chamber data.
- Seasonal efficiency is a rule-based aggregation problem and should remain separate from point-level ML prediction.

## Open questions

- Configurable tolerance numbers: the tolerance used for outlier review, sanity checks, and feature validation is not yet defined.
- Carnot-bound clipping criteria: Carnot COP is only a physical intuition and upper-bound sanity check at this stage; actual clipping or hard constraint criteria are not yet defined.
- Air/ref capacity balance tolerance: how to use differences between air-side capacity and refrigerant-side or reported capacity for data quality review is not yet defined.
- Product-specific monotonicity scope: which monotonicity assumptions apply across cooling/heating, fixed/inverter, fan step, compressor control, and wet/dry coil conditions is not yet defined.
- Test condition grouping criteria: whether data from different chamber conditions, fan-only/compressor-on states, wet/dry coil states, or control states can share the same learning distribution is not yet defined.
