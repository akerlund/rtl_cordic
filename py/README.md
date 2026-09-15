# CORDIC cocotb testbench

A cocotb/pyUVM port of the UVM testbench in [`../sv`](../sv), running on
Verilator. Unlike the SV testbench — whose `cor_scoreboard` is never
instantiated and whose DUT egress is left unconnected — this one checks every
beat.

## What it checks

`cordic_hdl_top.sv` presents the DUT's ingress as a full AXI4-Stream slave
with `tready` tied high, so the `vip_axi4s` master agent drives it unchanged.
`cordic_axi4s_if` has no `egr_tready`, so there is no handshake for a slave
agent to model and `cordic_egress_monitor` samples the egress signals
directly.

For each beat, `cordic_scoreboard` reads `{sine, cosine}` as two N4Q28 words
and compares them against `math.cos(|θ|)` and `math.sin(|θ|)`, with a
tolerance of 1e-3. The worst error across a full turn is about 5.4e-05.

The expected angles come from the testcase, not from the AXI4-S monitor. Both
agree: the driver sends 360 beats on cycles 33..392 and the DUT answers on
48..407 -- 360 beats, 15 cycles of latency. Checking against the stimulus the
testcase asked for is simply the stronger of the two, since it does not rely on
the monitor reconstructing the same list. A count mismatch on either side still
fails in `check_phase`.

## Running

```
./run_fusesoc.sh
```

It exports `PYTHONPATH` for `vip_axi4s_agent`, `vip_gauss` and `vip_common`
before calling FuseSoC, so run it rather than invoking the `sim` target
directly. Both testcases run in one pass:

- `tc_cordic_positive_radian_spin` — one turn anticlockwise, 360 beats
- `tc_cordic_negative_radian_spin` — one turn clockwise; the core takes |θ|,
  so the expected values are those of the positive angle
