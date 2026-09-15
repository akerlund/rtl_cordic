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
# Egress monitor for the CORDIC pyUVM/cocotb testbench.
#
# cordic_axi4s_if has no egr_tready, so there is no handshake for the AXI4-S
# slave agent to model. This samples the egress signals on every rising edge
# and forwards one item per asserted egr_tvalid.
#
################################################################################

from __future__ import annotations

import cocotb
from cocotb.triggers import ReadOnly, RisingEdge
from pyuvm import ConfigDB, uvm_analysis_port, uvm_monitor


class cordic_egress_beat:

  def __init__(self, tdata, tid):
    self.tdata = int(tdata)
    self.tid = int(tid)


class cordic_egress_monitor(uvm_monitor):

  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.beat_port = None
    self.dut = None
    self.number_of_beats = 0

  def build_phase(self):
    self.beat_port = uvm_analysis_port("beat_port", self)
    self.dut = ConfigDB().get(self, "", "dut")

  async def run_phase(self):
    cocotb.start_soon(self._collect())

  async def _collect(self):
    while True:
      await RisingEdge(self.dut.clk)
      await ReadOnly()
      if not self.dut.rst_n.value:
        continue
      # An x/z on tvalid before the pipeline has filled is not a beat.
      if self.dut.egr_tvalid.value.is_resolvable is False:
        continue
      if int(self.dut.egr_tvalid.value) != 1:
        continue
      self.number_of_beats += 1
      self.beat_port.write(
        cordic_egress_beat(self.dut.egr_tdata.value, self.dut.egr_tid.value))
