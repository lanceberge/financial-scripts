#!/usr/bin/env python3

from blackscholes import BlackScholesCall

spot = 55.0
strike = 50.0
T = 1.0   # Expiry time in years
r = 0.0025
vol = 0.15 
div_yield = 0.0

call = BlackScholesCall(spot, strike, T, r, vol, div_yield)
call_price = call.price()
print(f"Call Price: {call_price:.6f}")

