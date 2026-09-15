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
# tc_cordic_positive_radian_spin
#
# One full turn anticlockwise: 360 beats, one degree each.
#
# A full revolution is what exercises every quadrant and both fold boundaries,
# so a folding error that only shows up in one quadrant cannot hide. Each beat
# is checked against math.cos and math.sin of its own angle, so the pass
# condition is the value at every angle rather than the shape of the sweep.
#
################################################################################

from __future__ import annotations

from cordic_base_test import cordic_base_test, radian_spin
from seq_lib.vip_axi4s_seq import vip_axi4s_seq
from vip_axi4s_types_pkg import Axi4sTdataType, Axi4sTstrbType


class tc_cordic_positive_radian_spin(cordic_base_test):
  """One full turn anticlockwise, 360 beats of one degree each."""

  def build_phase(self):
    super().build_phase()
    self.mst_cfg.zero_delays_enable = True

  async def run_phase(self):
    self.raise_objection()
    await self.settle()

    seq = vip_axi4s_seq("cordic_seq0", self.cfg_t)
    theta_words = radian_spin(sign=1)
    self.arm_scoreboard(theta_words)

    seq.set_tdata_type(Axi4sTdataType.CUSTOM)
    seq.set_tdata(theta_words)
    seq.set_tstrb_type(Axi4sTstrbType.ALL)
    await seq.start(self.mst_sequencer)

    assert await self.wait_for_compared(360), (
      f"Only {self.env.scoreboard0.number_of_compared} of 360 beats compared")
    assert self.env.scoreboard0.number_of_failed == 0, (
      f"{self.env.scoreboard0.number_of_failed} beats outside tolerance")
    self.drop_objection()
