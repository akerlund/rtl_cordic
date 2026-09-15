#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

VIVADO_SETTINGS="/opt/amd/2025.2/Vivado/settings64.sh"
if [ ! -f "${VIVADO_SETTINGS}" ]; then
  echo "error: Vivado settings file not found: ${VIVADO_SETTINGS}" >&2
  echo "       Install Vivado 2025.2, then rerun this script." >&2
  exit 1
fi

source "${VIVADO_SETTINGS}"

TARGET=synth_vivado
CORE=akerlund::cordic:1.0.0

# The Vivado target uses the edalize flow API, whose default make target builds
# a full bitstream (synth -> impl -> bitstream). cordic_axi4s_if is an IP block
# synthesized out-of-context (see constraints/vivado_ooc.tcl), so a bitstream is
# neither wanted nor possible: implementation fails at write_bitstream with no
# pins to place. Run FuseSoC in setup-only mode to generate the build files,
# then invoke the Makefile's synthesis-only target.
fusesoc run --target "${TARGET}" --setup "${CORE}"

work="$(find "${REPO_ROOT}/build" -type d -name "${TARGET}" | head -1)"
if [ -z "${work}" ] || [ ! -f "${work}/Makefile" ]; then
  echo "error: could not locate the build directory for ${TARGET}" >&2
  exit 1
fi

make -C "${work}" synth

echo
echo "Utilization and timing reports:"
find "${work}" -name "*utilization*.rpt" -o -name "*timing_summary*.rpt" | sed 's/^/  /'
