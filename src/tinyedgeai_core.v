/*
 * Streaming signed-INT8 multiply-accumulate core.
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tinyedgeai_core (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,
    input  wire [7:0] activation,
    input  wire [7:0] weight,
    output wire [7:0] result
);

  wire signed [7:0]  activation_s = activation;
  wire signed [7:0]  weight_s     = weight;
  wire signed [15:0] product      = activation_s * weight_s;

  reg signed [23:0] accumulator;

  localparam signed [23:0] INT8_MAX = 24'sd127;
  localparam signed [23:0] INT8_MIN = -24'sd128;

  always @(posedge clk) begin
    if (!rst_n)
      accumulator <= 24'sd0;
    else if (enable)
      accumulator <= accumulator + {{8{product[15]}}, product};
  end

  assign result =
      (accumulator > INT8_MAX) ? 8'h7f :
      (accumulator < INT8_MIN) ? 8'h80 :
      accumulator[7:0];

endmodule

`default_nettype wire
