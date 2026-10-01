/*
 * TinyEdgeAI fixed-length signed-INT8 dot-product engine.
 * Four activation/weight pairs are accumulated per result.
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
  wire signed [17:0] product_ext  = {{2{product[15]}}, product};

  // Four signed INT8 products are bounded by [-65024, +65536].
  // Signed 18-bit range is [-131072, +131071], so this width is sufficient
  // with substantial numerical margin and avoids unnecessary adder/FF area.
  reg signed [17:0] accumulator;
  reg        [1:0]  sample_count;
  reg signed [7:0]  result_reg;

  wire signed [17:0] next_sum = accumulator + product_ext;

  function [7:0] saturate_int8;
    input signed [17:0] value;
    begin
      // Explicit signed clamp. Physical A/B characterization showed this
      // implementation gives materially better slow-corner timing and fewer
      // max-slew violations than the sign-extension-fit micro-optimization.
      if (value > 18'sd127)
        saturate_int8 = 8'h7f;
      else if (value < -18'sd128)
        saturate_int8 = 8'h80;
      else
        saturate_int8 = value[7:0];
    end
  endfunction

  always @(posedge clk) begin
    if (!rst_n) begin
      accumulator <= 18'sd0;
      sample_count <= 2'd0;
      result_reg   <= 8'sd0;
    end else if (enable) begin
      if (sample_count == 2'd3) begin
        result_reg   <= saturate_int8(next_sum);
        accumulator  <= 18'sd0;
        sample_count <= 2'd0;
      end else begin
        accumulator  <= next_sum;
        sample_count <= sample_count + 2'd1;
      end
    end
  end

  assign result = result_reg;

endmodule

`default_nettype wire
