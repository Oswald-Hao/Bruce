
import time

def inefficient_loop():
    total = 0
    for i in range(10000):
        for j in range(10000):
            total += 1
    return total

if __name__ == "__main__":
    inefficient_loop()
