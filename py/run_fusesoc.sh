#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORDIC_ROOT="${CORDIC_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
VIP_ROOT="${CORDIC_ROOT}/submodules/vip_axi4s_agent"
COMMON_ROOT="${CORDIC_ROOT}/submodules/vip_common"
CORE="akerlund::cordic_example_py:0"

export CORDIC_ROOT
export PYTHONPATH="${SCRIPT_DIR}/tb:${SCRIPT_DIR}/tc:${VIP_ROOT}/py:${VIP_ROOT}/submodules/vip_gauss/py:${COMMON_ROOT}/vip_fixed_point/py${PYTHONPATH:+:${PYTHONPATH}}"

if [ "$#" -eq 0 ]; then
  fusesoc --cores-root "${CORDIC_ROOT}" run --target sim "${CORE}"
else
  fusesoc --cores-root "${CORDIC_ROOT}" run "$@" "${CORE}"
fi
