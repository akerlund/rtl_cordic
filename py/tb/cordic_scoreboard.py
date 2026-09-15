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
# pyUVM scoreboard for the CORDIC testbench.
#
# Each egress beat carries {sine, cosine}, both N4Q28, for the theta that
# entered the pipeline 15 cycles earlier. cordic_radian_core takes the absolute
# value of theta before folding it into a quadrant, so a negative input yields
# cos(|theta|) and sin(|theta|) -- not cos/sin of the signed angle. The
# reference model mirrors that.
#
# The expected angles come from the testcase rather than from the AXI4-S
# monitor. Both agree -- the driver sends 360 beats on cycles 33..392, the DUT
# consumes exactly those and answers on 48..407, 15 cycles of latency, matching
# the register count in cordic_axi4s_if -- but checking against the stimulus
# the testcase asked for is the stronger of the two: it does not depend on the
# monitor reconstructing the same thing.
#
# This used to differ. An observer sampling at posedge + ReadOnly also saw
# tvalid at cycle 32, because vip_axi4s_driver drove its first beat in the same
# timestep as the edge that woke the sequence, landing after the RTL evaluated
# that edge but before ReadOnly. The driver now steps past the edge first, so
# the monitor's count and the DUT's agree.
#
################################################################################

from __future__ import annotations

import math

from pyuvm import uvm_component, uvm_subscriber

from float_to_fixed_point import fixed_point_to_float

# The DUT's word format: 4 integer bits (one of them the sign) and 28
# fractional, matching cordic_atan_radian_table_pkg's tables truncated to
# DATA_WIDTH_P bits.
N_BITS = 4
Q_BITS = 28
DATA_WIDTH = N_BITS + Q_BITS


class _SbSub(uvm_subscriber):

  def __init__(self, name, parent, callback):
    super().__init__(name, parent)
    self._callback = callback

  def write(self, item):
    self._callback(item)


class cordic_scoreboard(uvm_component):

  def __init__(self, name, parent):
    super().__init__(name, parent)
    self.expected = []
    self.number_of_compared = 0
    self.number_of_passed = 0
    self.number_of_failed = 0
    self.number_of_unexpected = 0
    self.worst_error = 0.0
    self.worst_error_theta = 0.0
    # 16 stages of N4Q28 CORDIC: the gain constant, the atan table and every
    # intermediate are truncated to 28 fractional bits, so the residual is
    # some tens of LSBs rather than one.
    self.tolerance = 1.0e-3
    self.egr_port = None

  def build_phase(self):
    self._egr_sub = _SbSub("egr_sub", self, self.write_egr_port)
    self.egr_port = self._egr_sub.analysis_export

  def set_expected(self, theta_words):
    """The N4Q28 angle words the testcase drives, in order."""
    self.expected = list(theta_words)

  def handle_reset(self):
    self.expected.clear()

  def write_egr_port(self, beat):
    if not self.expected:
      self.number_of_unexpected += 1
      self.logger.error(
        f"Egress beat {self.number_of_compared + self.number_of_unexpected} "
        "arrived with no angle left to compare it against")
      return
    self._compare(self.expected.pop(0), beat)

  def _compare(self, theta_word, egr_beat):
    self.number_of_compared += 1

    theta = fixed_point_to_float(theta_word, N_BITS, Q_BITS)
    cosine = fixed_point_to_float(egr_beat.tdata & ((1 << DATA_WIDTH) - 1),
                                  N_BITS, Q_BITS)
    sine = fixed_point_to_float(egr_beat.tdata >> DATA_WIDTH, N_BITS, Q_BITS)

    expected_cos = math.cos(abs(theta))
    expected_sin = math.sin(abs(theta))
    cos_error = abs(cosine - expected_cos)
    sin_error = abs(sine - expected_sin)
    error = max(cos_error, sin_error)

    if error > self.worst_error:
      self.worst_error = error
      self.worst_error_theta = theta

    if error <= self.tolerance:
      self.number_of_passed += 1
    else:
      self.number_of_failed += 1
      self.logger.error(
        f"Beat {self.number_of_compared} theta={theta:+.9f} rad "
        f"({math.degrees(theta):+.3f} deg): "
        f"cos got {cosine:+.9f} want {expected_cos:+.9f} (err {cos_error:.3e}), "
        f"sin got {sine:+.9f} want {expected_sin:+.9f} (err {sin_error:.3e})")

  def check_phase(self):
    if self.expected:
      self.number_of_failed += len(self.expected)
      self.logger.error(
        f"{len(self.expected)} angles never produced an egress beat")
    if self.number_of_unexpected:
      self.number_of_failed += self.number_of_unexpected
    if self.number_of_failed:
      self.logger.error(f"Test failed! ({self.number_of_failed} mismatches)")
    else:
      self.logger.info(
        f"Test passed ({self.number_of_passed}/{self.number_of_compared}) "
        f"beats, worst error {self.worst_error:.3e} at "
        f"theta={self.worst_error_theta:+.9f} rad")
