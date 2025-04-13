import pathlib
import time

from scl_frd3walk import *

SCRIPT_PATH=pathlib.Path(__file__).parent.absolute()

# input
path = SCRIPT_PATH / "tr00.frd"

def main():
        print(f"Processing {path}")
        buf = path.read_bytes()
        frd = FRD3Walk(buf)
        ptn = time.perf_counter_ns()
        frd.walk()
        ptne = time.perf_counter_ns() - ptn
        frd.print()
        print(f"Walking '{path.name}' with frd3walk took {(float(ptne) / 1e6):.2f} ms")

if __name__ == "__main__":
    main()
