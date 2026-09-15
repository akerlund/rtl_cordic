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
# other_cordics
#
# Reference implementations in Python of CORDIC arrangements this repository
# does not synthesise -- division among them -- kept as working notes on what
# the same shift-and-add structure can compute.
#
# Not imported by the RTL, the testbench or the table generator.
#
################################################################################

# multiply(x,y){
#    for (i=1; i=<B; i++){
#       if (x > 0)
#          x = x - 2^(-i)
#          z = z + y*2^(-i)
#       else
#          x = x + 2^(-i)
#          z = z - y*2^(-i)
#    }
#    return(z)
# }
# log10(x){
#    z = 0;
#    for ( i=1;i=<B;i++ ){
#       if (x > 1)
#          x = x - x*2^(-i);
#          z = z - log10(1-2^(-i));
#        else
#          x = x + x*2^(-i);
#          z = z - log10(1+2^(-i));
#    }
#    return(z)
# }

# Listing Five
# 10_to_power(x){
#    z = 1;
#    for ( i=1;i=<B; i++ ){
#       if (x > 0)
#          x = x - log10(1+2^(-i));
#          z = z + z*2^(-i);
#       else
#          x = x - log10(1-2^(-i));
#          z = z - z*2^(-i);
#    }
#    return(z)
# }

def cordic_divide(x, y, stages):

  z = 0

  for i in range(1, stages):
    if x > 0:
      x = x - y*2**(-i)
      z = z + 2**(-i)
      print("x0 = %f, z0 = %f" % (x, z))
    else:
      x = x + y*2**(-i)
      z = z - 2**(-i)
      print("x1 = %f, z2 = %f" % (x, z))
  return z


def cordic_divide_4_quartant(x, y, stages):

  z = 0

  for i in range(1, stages):
    if x > 0:
      if y > 0:
        x = x - y*2**(-i)
        z = z + 2**(-i)
      else:
        x = x + y*2**(-i)
        z = z - 2**(-i)
    else:
      if y > 0:
        x = x + y*2**(-i)
        z = z - 2**(-i)
      else:
        x = x - y*2**(-i)
        z = z + 2**(-i)
  return z



if __name__ == '__main__':

  stages   = 16
  dividend_c0 = -0.1
  divisor_c0  = -0.5
  quotient = cordic_divide_4_quartant(dividend_c0, divisor_c0, stages)

  print("%f / %f = %f" % (divisor_c0, divisor_c0, quotient))
