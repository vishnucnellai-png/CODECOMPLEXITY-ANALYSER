import time
import sys

# add backend to path
sys.path.append(r"c:\Users\vishnu priyan\OneDrive\Desktop\codecomplexity22\backend")

from analyzer.engine import analyze_python_code

code = """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""

start = time.time()
res = analyze_python_code(code)
dt = time.time() - start
print(f"Time taken to analyze: {dt:.6f} seconds")
