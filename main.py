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

    b1.write('a')                  # Write "a" to the byte in `b1`
    print(b1.read())               # Read "a" from `b1`

    # Write the char "z" to the byte in `b2`
    b2.write('z')                  # Write "z" to the byte in `b2`
    print(b2.read())               # Read "z" from `b2`

    print(mm)
    # Free the 2nd and 4th allocations
    mm.free(b2)                   # Buffer: [X-XXX]
    mm.free(b4)                   # Buffer: [X-X-X] (2 gaps)

    # Now we can't read/write the data in `b2` and `b4`
    print(mm)

    # Allocate a 2-byte block
    b6 = mm.alloc(2)              # Buffer: [XXXXX] (uses freed space)
    print(b6.units)
    
    b6.write('xy')                 # Write "xy" to `b6`
    print(b6.read())               # Read "xy" from `b6`
    print(mm)

    mm.free(b3)                   # Buffer: [X-XXX]
    mm.free(b5)                   # Buffer: [X-X-X] (2 gaps)
    mm.defragment()
    print(mm)

if __name__ == '__main__':
    main()
