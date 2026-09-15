////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2026 Fredrik Åkerlund
// https://github.com/akerlund/rtl_cordic
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// Description:
// HDL shell for the CORDIC pyUVM/cocotb testbench.
//
// cordic_axi4s_if is a fixed-latency pipeline with no egress backpressure: it
// has no ing_tready and no egr_tready. The ingress side is therefore presented
// as a full AXI4-Stream slave with tready tied high, so the vip_axi4s master
// agent can drive it unchanged, while the egress side is left as plain signals
// for cordic_egress_monitor to sample.
//
////////////////////////////////////////////////////////////////////////////////

`default_nettype none

module cordic_hdl_top #(
    parameter int DATA_WIDTH     = 32,
    parameter int ID_WIDTH       = 2,
    parameter int NR_OF_STAGES   = 16
  )(
    input  wire                        clk,
    input  wire                        rst_n,

    // Ingress AXI4-Stream (driven by the vip_axi4s master agent)
    input  wire                        ing_tvalid,
    output logic                       ing_tready,
    input  wire  [DATA_WIDTH-1 : 0]    ing_tdata,
    input  wire  [DATA_WIDTH/8-1 : 0]  ing_tstrb,
    input  wire  [DATA_WIDTH/8-1 : 0]  ing_tkeep,
    input  wire                        ing_tlast,
    input  wire  [ID_WIDTH-1 : 0]      ing_tid,
    input  wire                        ing_tdest,
    input  wire                        ing_tuser,

    // Egress, sampled directly by the testbench
    output logic                       egr_tvalid,
    output logic [2*DATA_WIDTH-1 : 0]  egr_tdata,
    output logic [ID_WIDTH-1 : 0]      egr_tid
  );

  // The pipeline consumes a beat every cycle; it can never stall.
  assign ing_tready = 1'b1;

  logic unused_ok;
  assign unused_ok = &{1'b0, ing_tstrb, ing_tkeep, ing_tlast, ing_tdest};

  cordic_axi4s_if #(
    .AXI_DATA_WIDTH_P ( DATA_WIDTH   ),
    .AXI_ID_WIDTH_P   ( ID_WIDTH     ),
    .NR_OF_STAGES_P   ( NR_OF_STAGES )
  ) cordic_axi4s_if_i0 (
    .clk              ( clk          ),
    .rst_n            ( rst_n        ),
    .ing_tvalid       ( ing_tvalid   ),
    .ing_tdata        ( ing_tdata    ),
    .ing_tid          ( ing_tid      ),
    .ing_tuser        ( ing_tuser    ),
    .egr_tvalid       ( egr_tvalid   ),
    .egr_tdata        ( egr_tdata    ),
    .egr_tid          ( egr_tid      )
  );

endmodule

`default_nettype wire
