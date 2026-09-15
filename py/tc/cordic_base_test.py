################################################################################
#
# Copyright (C) 2026 Fredrik Åkerlund
# https://github.com/akerlund/rtl_cordic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Description:
# Base pyUVM test for the CORDIC.
#
################################################################################

from __future__ import annotations

import math

from cocotb.triggers import Timer
from pyuvm import ConfigDB, uvm_test

from cordic_env import cordic_env
from float_to_fixed_point import float_to_fixed_point_int
from vip_axi4s_config import vip_axi4s_config

# The angle sweep the SV testcases drive, generated here rather than read from
# a table: cordic_test_angles_pkg.sv holds the same 360 values, and keeping a
# second copy of them in Python would be one more thing to keep in step.
N_BITS = 4
Q_BITS = 28
STEPS = 360


def radian_spin(steps=STEPS, sign=1):
  """The N4Q28 words for a full turn in `steps` equal increments."""
  increment = sign * 2 * math.pi / steps
  width = N_BITS + Q_BITS
  return [float_to_fixed_point_int(k * increment, Q_BITS) & ((1 << width) - 1)
          for k in range(steps)]


class cordic_base_test(uvm_test):

  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.cfg_t = None
    self.env = None
    self.mst_cfg = None
    self.ing_vif = None

  def build_phase(self):
    self.cfg_t = ConfigDB().get(self, "", "cfg_t")
    self.ing_vif = ConfigDB().get(self, "", "ing_vif")
    self.env = cordic_env("tb_env", self)

    self.mst_cfg = vip_axi4s_config("axi4s_mst_cfg0")
    # The SV base test disables both delay generators; the pipeline has no
    # backpressure, so every beat is accepted on the cycle it is offered.
    self.mst_cfg.tvalid_delay_enabled = False
    self.mst_cfg.tready_delay_enabled = False
    # One packet carries the whole 360-beat turn, above the agent's 256-beat
    # default ceiling for a single stream.
    self.mst_cfg.max_stream_burst_length = STEPS

    ConfigDB().set(self, "tb_env.mst_agent0", "cfg", self.mst_cfg)

  @property
  def mst_sequencer(self):
    return self.env.mst_agent0.sequencer

  def arm_scoreboard(self, theta_words):
    """Tell the scoreboard which angles to expect, in order."""
    self.env.scoreboard0.set_expected(theta_words)

  async def wait_for_compared(self, expected, timeout=20000):
    for _ in range(timeout):
      if self.env.scoreboard0.number_of_compared >= expected:
        return True
      await self.ing_vif.rising()
      await Timer(1, unit="step")
    return self.env.scoreboard0.number_of_compared >= expected

  async def settle(self, cycles=32):
    for _ in range(cycles):
      await self.ing_vif.rising()

  def report_phase(self):
    sb = self.env.scoreboard0
    self.logger.info(
      f"[{self.get_name()}] DONE -- compared={sb.number_of_compared} "
      f"passed={sb.number_of_passed} failed={sb.number_of_failed} "
      f"worst_error={sb.worst_error:.3e}")
