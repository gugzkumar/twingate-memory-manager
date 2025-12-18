"""
Example usage of the MemoryManager.

From: https://gist.github.com/ebichman/0a1154de4e9ae4150da2109151e09d71
"""
from twingate import MemoryManager


def main():
    # Test
    mm = MemoryManager(5)

    # Allocate 5 blocks of 1 byte each
    b1 = mm.alloc(1)              # Buffer: [X----]
    b2 = mm.alloc(1)              # Buffer: [XX---]
    b3 = mm.alloc(1)              # Buffer: [XXX--]
    b4 = mm.alloc(1)              # Buffer: [XXXX-]
    b5 = mm.alloc(1)              # Buffer: [XXXXX]
    print(mm)
    print()

    b1.write('a')                  # Write "a" to the byte in `b1`
    print(b1.read())               # Read "a" from `b1`
    print(mm)
    print()

    # Write the char "z" to the byte in `b2`
    b2.write('z')                  # Write "z" to the byte in `b2`
    print(b2.read())               # Read "z" from `b2`
    print(mm)
    print()

    # Free the 2nd and 4th allocations
    mm.free(b2)                   # Buffer: [X-XXX]
    mm.free(b4)                   # Buffer: [X-X-X] (2 gaps)
    print(mm)
    print()

    # Now we can't read/write the data in `b2` and `b4`
    try:
        b2.write('y')                  # Error: MemoryError
    except MemoryError as e:
        print(f"Caught expected error for writing to b2: {e}")
    
    try:
        b4.write('y')                  # Error: MemoryError
    except MemoryError as e:
        print(f"Caught expected error for writing to b4: {e}")
    print()

    # Allocate a 2-byte block
    b6 = mm.alloc(2)              # Buffer: [XXXXX] (uses freed space)
    b6.write('xy')                 # Write "xy" to `b6`
    print(b6.read())               # Read "xy" from `b6`
    print(mm)
    print()

    # Free some blocks and defragment
    mm.free(b3)                   # Buffer: [X-XXX]
    mm.free(b5)                   # Buffer: [X-X-X] (2 gaps)
    mm.defragment()
    print(mm)

if __name__ == '__main__':
    main()
