# this is where the magic happens
import macroator

from factorial import factorial

# let's lower the recursion limit a bit.
import sys
sys.setrecursionlimit(10)

# now, our tail recursive function should go to a stack depth equal to `n`.
# But thanks to our _magic_, this works.
print(factorial(50))

# The answer is right, too.
import math
assert factorial(50) == math.factorial(50)
