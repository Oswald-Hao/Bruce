
import time

def fast_function():
    return 1 + 1

def slow_function():
    time.sleep(0.1)
    return sum(range(1000))

if __name__ == "__main__":
    fast_function()
    slow_function()
