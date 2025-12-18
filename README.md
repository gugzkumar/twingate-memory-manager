# Twingate Memory Manager

## Files
```
README.md               - This file
main.py                 - Example usage of the Memory Manager
twingate.py             - Twingate Module with implementations for MemoryUnit, MemoryManager, and MemoryBlock
tests/
    test_twingate.py    - Unit tests for the classes in the Twingate Module
```

## Quick Start

- You can run the example used in main with `python main.py`
- You can run the tests using `python -m unittest`

## Overview

The following project is a simple memory manager implemented in Python. It simulates memory allocation and deallocation using a list to represent a buffer.

## Classes
- `MemoryUnit`: This is just a simple class representing a unit of memory. The only attribute is a `char`
- `MemoryManager`: This class manages a memory buffer, represented by a list of MemoryUnits, and allows for the allocation and deallocation of memory blocks. Memory Manager also supports defragmentation of the memory buffer on demand.
- `MemoryBlock`: This class represents a block of memory allocated by the MemoryManager. It simply holds a list of MemoryUnits.

## Technical Overview of How The Memory Manager Works

The memory manager uses a list to represent the Buffer. In order to allocate the next block of memory during an allocation request, it maintains a pointer `next_alloc_index` to the next free unit in the buffer. When a block is allocated it is given an unique ID, and tracked in a dictionary `allocated_blocks` for easy lookup during deallocation.

When a block is freed, it is removed from the `allocated_blocks` dictionary, and its units are added to a stack called `freed_fragmented_units` to use for future allocations. This allows the memory manager to reuse freed units even if they are fragmented.

During the allocation process, the memory manager first checks if there are any units in the `freed_fragmented_units` stack. If there are, it uses those units first before allocating from the contiguous free space in the buffer.

If during any allocation request, there is not enough contiguous free space in the buffer, the memory manager raises a `MemoryError`.

In addition to allocation and deallocation, the memory manager also supports defragmentation on demand. The defragmentation process involves creating a new buffer and copying over all allocated units to the new buffer, consolidating free space towards the end of the buffer. After defragmentation, the `next_alloc_index` is updated to point to the next free unit in the new buffer, and the `freed_fragmented_units` stack is cleared. This process keeps intact the allocated blocks, their IDs, and their data.

## Limitations
- The memory manager is not thread-safe. Concurrent allocations, deallocations, and defragmentation are not supported.
- The memory manager only supports allocation of `char` type MemoryUnits.
- Defragmentation happens on demand only, and not automatically during allocations.

## Future Improvements

- Improvements can be made to support more than the `char` type in the memory units, and memory blocks.
- Implementation is not thread-safe. Future improvements can be made to support concurrent allocations, deallocations, and defragmentation.
- A very simple algorithm is used for defragmentation. More sophisticated algorithms can be implemented to optimize performance based reducing the amount of data movement.
- Another approach I considered was holding on to the indexes of the free units within the memory block itself. The defragmentation process currently involves creating a new buffer of the same size and copying over the allocated units. This can be optimized for memory by simply moving units within the existing buffer.
- Instead of using the fragmented units for allocation first, we could have used the contiguous free space first. This would reduce fragmentation over time during inserts.
- We could also have sorted the fragmented units stack based on their indexes in the buffer to improve the likelihood of contiguous allocations from the fragmented units.
