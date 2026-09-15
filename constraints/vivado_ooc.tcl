# Synthesize the CORDIC out-of-context.
#
# cordic_axi4s_if is an IP block with wide AXI4-Stream ports, not a full
# device design. Out-of-context synthesis skips I/O buffer insertion and pin
# mapping, so the ports are treated as internal block boundaries rather than
# device pins: utilization and register-to-register timing then describe the
# core logic instead of an artificial pinout.
#
# Sourced by the edalize Vivado flow after create_project (synth_1 already
# exists) and before the run is launched.
#
# Vivado 2025.2 exposes no STEPS.SYNTH_DESIGN.ARGS.MODE run property, so the
# out-of-context flag goes through the run's "MORE OPTIONS" field -- note the
# space in the property name, and the -name/-value form because the value
# begins with a dash.
set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} \
             -value {-mode out_of_context} \
             -objects [get_runs synth_1]
