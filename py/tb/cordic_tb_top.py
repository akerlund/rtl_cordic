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
# cocotb testbench top for the CORDIC pyUVM port.
#
################################################################################

from __future__ import annotations

import os
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from pyuvm import ConfigDB, uvm_root

_HERE = os.path.dirname(os.path.abspath(__file__))
_PY_ROOT = os.path.dirname(_HERE)


def _find_repo_root(start):
  env = os.environ.get("CORDIC_ROOT")
  if env:
    return os.path.abspath(env)
  path = os.path.abspath(start)
  while True:
    if os.path.exists(os.path.join(path, ".git")):
      return path
    parent = os.path.dirname(path)
    if parent == path:
      raise RuntimeError("cordic_tb_top: CORDIC_ROOT was not found")
    path = parent


_REPO_ROOT = _find_repo_root(_HERE)
_VIP_ROOT = os.path.join(_REPO_ROOT, "submodules", "vip_axi4s_agent")
_COMMON_ROOT = os.path.join(_REPO_ROOT, "submodules", "vip_common")
_LOCAL_PYS = [_HERE, os.path.join(_PY_ROOT, "tc")]
_COMPONENT_PYS = [
  os.path.join(_VIP_ROOT, "py"),
  os.path.join(_VIP_ROOT, "submodules", "vip_gauss", "py"),
  os.path.join(_COMMON_ROOT, "vip_fixed_point", "py"),
]
for path in _COMPONENT_PYS + _LOCAL_PYS:
  if not os.path.isdir(path):
    raise RuntimeError(f"cordic_tb_top: expected Python source directory not found: {path}")
  if path not in sys.path:
    sys.path.insert(0, path)

from vip_axi4s_if import Axi4sBus                                            # noqa: E402
from vip_axi4s_types_pkg import Axi4sCfgT                                    # noqa: E402
from tc_cordic_positive_radian_spin import tc_cordic_positive_radian_spin    # noqa: E402,F401
from tc_cordic_negative_radian_spin import tc_cordic_negative_radian_spin    # noqa: E402,F401


CFG_T = Axi4sCfgT(TDATA_BYTES_P=4, TID_WIDTH_P=2,
                  TDEST_WIDTH_P=0, TUSER_WIDTH_P=0)

CLOCK_PERIOD_NS = 10.0


async def _run(dut, test_name):
  cocotb.start_soon(Clock(dut.clk, CLOCK_PERIOD_NS, unit="ns").start())

  ing_bus = Axi4sBus(dut, clock_name="clk", reset_name="rst_n", prefix="ing_")
  ing_bus.reset_master()
  dut.rst_n.value = 0

  for _ in range(5):
    await RisingEdge(dut.clk)

  dut.rst_n.value = 1
  await Timer(CLOCK_PERIOD_NS, unit="ns")

  ConfigDB().set(None, "*", "ing_vif", ing_bus)
  ConfigDB().set(None, "*", "cfg_t", CFG_T)
  ConfigDB().set(None, "*", "dut", dut)
  await uvm_root().run_test(test_name, keep_set={ConfigDB})


@cocotb.test(name="tc_cordic_positive_radian_spin", timeout_time=20, timeout_unit="ms")
async def tc_cordic_positive_radian_spin_test(dut):
  await _run(dut, "tc_cordic_positive_radian_spin")


@cocotb.test(name="tc_cordic_negative_radian_spin", timeout_time=20, timeout_unit="ms")
async def tc_cordic_negative_radian_spin_test(dut):
  await _run(dut, "tc_cordic_negative_radian_spin")
