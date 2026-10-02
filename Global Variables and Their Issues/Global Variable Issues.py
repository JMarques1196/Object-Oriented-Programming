# ==============================================================================
# POINT 1: DEMONSTRATING GLOBAL STATE ISSUES (REALISTIC SCENARIO)
# ==============================================================================

# 1. INITIAL GLOBAL STATE
# ------------------------------------------------------------------------------
water_level: int = 50  # Current water level in liters
maintenance_mode: bool = False  # Global control flag for system state


# 2. DEMONSTRATION OF BUG 1 (GLOBAL STATE MUTATION)
# ------------------------------------------------------------------------------
def calibrate_sensors() -> None:
    """Routine function that temporarily activates maintenance mode for calibration."""
    global maintenance_mode
    # BUG: Enables the global maintenance flag but forgets to reset it afterwards!
    maintenance_mode = True


def execute_pumping() -> None:
    """Executes pumping only if the system is not in maintenance mode."""
    global water_level, maintenance_mode

    if not maintenance_mode:
        print(f"[OK] Pumping completed. Current level: {water_level}L")
    else:
        print("[CRITICAL ERROR] Pumping blocked: System stuck in Maintenance Mode!")


# ------------------------------------------------------------------------------
# Execution of Bug 1:
# ------------------------------------------------------------------------------
print("--- Simulating Bug 1 (Hidden Side Effect) ---")
calibrate_sensors()  # Sensors calibrated
execute_pumping()  # Fails because calibrate_sensors() modified global maintenance_mode


# 3. FIX FOR BUG 1
# ------------------------------------------------------------------------------
def calibrate_sensors_fixed() -> None:
    """Ensures the global state is restored after the calibration process."""
    global maintenance_mode
    original_state = maintenance_mode

    maintenance_mode = True  # Temporarily activate
    # ... perform calibration routine ...

    maintenance_mode = original_state  # Restore original state


# ------------------------------------------------------------------------------
# Execution of Bug Fix:
# ------------------------------------------------------------------------------
print("\n--- Simulating Fix for Bug 1 ---")
maintenance_mode = False  # Reset global state
calibrate_sensors_fixed()
execute_pumping()  # Works as expected


# 4. CREATING A NEW FUNCTION THAT INTRODUCES ANOTHER GLOBAL STATE BUG
# ------------------------------------------------------------------------------
def empty_reservoir() -> None:
    """Prepares the system for cleaning by zeroing the global level directly."""
    global water_level
    # NEW BUG: Sets global water_level to 0 without validating active operations.
    water_level = 0


def drain_liters(liters: int) -> None:
    """Drains a specific amount calculated from the current global water level."""
    global water_level
    water_level -= liters
    if water_level < 0:
        print(f"[MEMORY ERROR] Inconsistent global water level state: {water_level}L")


# ------------------------------------------------------------------------------
# Execution of New Bug:
# ------------------------------------------------------------------------------
print("\n--- Simulating New Bug (New Function) ---")
empty_reservoir()
drain_liters(15)  # Results in an invalid -15L state in global memory

# ==============================================================================
# POINT 2: CODE REUSE ISSUES - FUNCTION VARIANTS & STATE CONFLICT
# ==============================================================================

# 1. SHARED GLOBAL STATE
# ------------------------------------------------------------------------------
# Multiple similar functions modify these variables independently.
water_level_a: int = 100  # Reservoir A level in liters (max 100L)
water_level_b: int = 20  # Reservoir B level in liters (max 100L)
maintenance_mode: bool = False  # Global control flag


# 2. FUNCTION VARIANTS & BUG DEMONSTRATION
# ------------------------------------------------------------------------------
def execute_pumping(liters: int) -> None:
    """Increases water level and temporarily disables maintenance mode to operate."""
    global water_level_a, maintenance_mode

    # Assumption: To pump, the system must be in operational mode
    maintenance_mode = False
    water_level_a += liters
    print(f"[OK] Pumping executed. Reservoir A: {water_level_a}L")


def execute_draining_with_bug(liters: int) -> None:
    """Drains water from Reservoir A but modifies level without validating global minimums."""
    global water_level_a, maintenance_mode

    # BUG: Drains requested liters, but sets maintenance_mode = True as a side effect,
    # blocking remaining system functions unexpectedly.
    if not maintenance_mode:
        water_level_a -= liters
        maintenance_mode = True  # Hidden side effect!
        print(f"[OK] Draining executed. Reservoir A: {water_level_a}L")
    else:
        print("[ERROR] Draining blocked by maintenance mode!")


def execute_transfer_with_bug(liters: int) -> None:
    """Transfers water from A to B. Fails if level is too low or system is in maintenance."""
    global water_level_a, water_level_b, maintenance_mode

    # Depends on maintenance_mode being False and A having at least 30L buffer
    if maintenance_mode:
        print("[CRITICAL ERROR] Transfer failed: System locked in maintenance mode by another function!")
        return

    if water_level_a - liters < 30:
        print("[ERROR] Transfer failed: Must keep at least 30L in Reservoir A!")
    else:
        water_level_a -= liters
        water_level_b += liters
        print(f"[OK] Transferred {liters}L. A: {water_level_a}L, B: {water_level_b}L")


# ------------------------------------------------------------------------------
# Execution of Bug 2:
# ------------------------------------------------------------------------------
print("--- Simulating Bug 2 (Function Variant Conflict) ---")
execute_draining_with_bug(20)  # Runs successfully, but leaves maintenance_mode = True
execute_transfer_with_bug(10)  # FAILS: Previous function mutated shared control state!


# 3. FIX FOR BUG 2
# ------------------------------------------------------------------------------
def execute_draining_fixed(liters: int) -> None:
    """Drains water while maintaining global control flag integrity."""
    global water_level_a, maintenance_mode

    if not maintenance_mode:
        water_level_a -= liters
        # Removed unexpected side effect on the global maintenance flag
        print(f"[OK] Draining fixed executed. Reservoir A: {water_level_a}L")


# ------------------------------------------------------------------------------
# Execution of Bug Fix:
# ------------------------------------------------------------------------------
print("\n--- Simulating Fix for Bug 2 ---")
maintenance_mode = False  # Reset global state
execute_draining_fixed(20)
execute_transfer_with_bug(10)  # Transfer now succeeds as expected!


# 4. CREATING A NEW FUNCTION THAT INTRODUCES ANOTHER VARIANT BUG
# ------------------------------------------------------------------------------
def execute_emergency_flush(liters: int) -> None:
    """New emergency draining variant function that breaks safety buffer assumptions."""
    global water_level_a
    # NEW BUG: Drains water without checking the 30L minimum safety limit
    water_level_a -= liters
    print(f"[OK] Emergency flush executed. Reservoir A level down to: {water_level_a}L")


# ------------------------------------------------------------------------------
# Execution of New Bug:
# ------------------------------------------------------------------------------
print("\n--- Simulating New Bug (New Variant Function) ---")
# Reservoir A level was 50L. Flush removes 30L, leaving A at 20L.
execute_emergency_flush(30)
# Transfer fails because it relies on the assumption that a 30L buffer is maintained
execute_transfer_with_bug(10)