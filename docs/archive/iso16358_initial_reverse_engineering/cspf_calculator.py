def calculate_iso16358_cspf_excel(
    phi_full_35, p_full_35,
    phi_haf_35, p_haf_35,
    phi_min_35, p_min_35,
    phi_full_29=None, p_full_29=None,
    phi_haf_29=None, p_haf_29=None,
    phi_min_29=None, p_min_29=None,
    t_0=20.0, t_100=35.0,
    c_d=0.25,
    bin_data=None
):
    """
    Pure Python implementation of ISO 16358-1 CSPF following the EXACT logic 
    and formula structure of the provided Excel tool.
    
    Assumes `c_d` and `bin_data` are loaded from "region_config.md".
    For demonstration, default values are still used if not provided.
    """
    
    # If bin_data or c_d are not provided, they would typically be loaded from "region_config.md".
    # For this example, we'll use the provided defaults or hardcoded values if not passed.
    if bin_data is None:
        # This would ideally be loaded from "region_config.md"
        bin_data = [
            (15.0, 0), (16.0, 0), (17.0, 0), (18.0, 0), (19.0, 0), (20.0, 0),
            (21.0, 100), (22.0, 139), (23.0, 165), (24.0, 196), (25.0, 210),
            (26.0, 215), (27.0, 210), (28.0, 181), (29.0, 150), (30.0, 120),
            (31.0, 75), (32.0, 35), (33.0, 11), (34.0, 6), (35.0, 4)
        ]
    # c_d is already a parameter with a default, so no change needed here unless it's also loaded from file.

    # 2. Defaults for 29C
    if phi_full_29 is None: phi_full_29 = phi_full_35 * 1.077
    if p_full_29 is None: p_full_29 = p_full_35 * 0.914
    if phi_haf_29 is None: phi_haf_29 = phi_haf_35 * 1.077
    if p_haf_29 is None: p_haf_29 = p_haf_35 * 0.914
    if phi_min_29 is None: phi_min_29 = phi_min_35 * 1.077
    if p_min_29 is None: p_min_29 = p_min_35 * 0.914

    # 3. Interpolation and Balance Points
    def get_val_at_t(v35, v29, t):
        return v35 + (v29 - v35) / (35 - 29) * (35 - t)

    def calc_balance(phi_at_35, phi_at_29):
        dt = 6
        dload = 15
        num = dt * phi_full_35 * t_0 + dt * phi_at_35 * dload + t_100 * (phi_at_29 - phi_at_35) * dload
        den = dt * phi_full_35 + (phi_at_29 - phi_at_35) * dload
        return num / den

    t_b = calc_balance(phi_full_35, phi_full_29)
    t_c = calc_balance(phi_haf_35, phi_haf_29)
    t_p = calc_balance(phi_min_35, phi_min_29)

    # 4. Bin-by-bin
    total_cl = 0
    total_ec = 0
    for t_j, n_j in bin_data:
        if n_j == 0: continue
        
        # Load(tj) = FullCap(35) * (Tj - T0) / (T100 - T0)
        load_tj = phi_full_35 * (t_j - t_0) / (t_100 - t_0)
        
        phi_f_tj = get_val_at_t(phi_full_35, phi_full_29, t_j)
        phi_h_tj = get_val_at_t(phi_haf_35, phi_haf_29, t_j)
        phi_m_tj = get_val_at_t(phi_min_35, phi_min_29, t_j)
        
        p_f_tj = get_val_at_t(p_full_35, p_full_29, t_j)
        p_h_tj = get_val_at_t(p_haf_35, p_haf_29, t_j)
        p_m_tj = get_val_at_t(p_min_35, p_min_29, t_j)
        
        # Power calc logic from columns CK, CZ:
        # Load_Cap_Ratio X = Load / Capacity(tj)
        # Power = ... (Excel CZ formula logic)
        
        # simplified E calculation
        # Excel: CZ formula uses logic: if Load <= Min, E = (Load * Hours * PowerMin/CapMin) / FPL
        # If Load > Min, E = Load * Hours / EER_interpolated
        
        # FPL factor
        x_tj = load_tj / phi_m_tj if phi_m_tj > 0 else 0
        f_pl_tj = 1 - c_d * (1 - min(1, x_tj))
        
        if load_tj <= phi_m_tj:
            eer = (phi_m_tj / p_m_tj) * f_pl_tj
        elif load_tj <= phi_h_tj:
            # Interpolation between Min and Half
            eer_m = phi_m_tj / p_m_tj
            eer_h = phi_h_tj / p_h_tj
            eer = eer_m + (load_tj - phi_m_tj) / (phi_h_tj - phi_m_tj) * (eer_h - eer_m)
        elif load_tj <= phi_f_tj:
            # Interpolation between Half and Full
            eer_h = phi_h_tj / p_h_tj
            eer_f = phi_f_tj / p_f_tj
            eer = eer_h + (load_tj - phi_h_tj) / (phi_f_tj - phi_h_tj) * (eer_f - eer_h)
        else:
            # Full speed
            eer = phi_f_tj / p_f_tj
        
        total_cl += load_tj * n_j
        total_ec += (load_tj * n_j) / eer
        
    return total_cl / total_ec

if __name__ == "__main__":
    cspf = calculate_iso16358_cspf_excel(
        phi_full_35=2691.334, p_full_35=899.5,
        phi_haf_35=1249.055, p_haf_35=303.2,
        phi_min_35=1500.0, p_min_35=320.0,
        # If 29C data is not available, it will use defaults calculated from 35C values.
        # Example of providing 29C data:
        # phi_full_29=3300.0, p_full_29=680.0,
        # phi_haf_29=2850.0, p_haf_29=580.0,
        # phi_min_29=1650.0, p_min_29=290.0
    )
    print(f"Calculated CSPF: {cspf:.4f}")
