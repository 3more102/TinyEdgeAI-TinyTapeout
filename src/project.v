/*
 * TinyEdgeAI Tiny Tapeout top-level wrapper
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_3more102_tinyedgeai (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  tinyedgeai_core core (
      .clk        (clk),
      .rst_n      (rst_n),
      .enable     (ena),
      .activation (ui_in),
      .weight     (uio_in),
      .result     (uo_out)
  );

  // The bidirectional bank is used as the signed INT8 weight input.
  assign uio_out = 8'h00;
  assign uio_oe  = 8'h00;

endmodule

`default_nettype wire
