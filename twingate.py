from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class MemoryUnit:
    """
    Represents a single unit of memory in the memory manager (1 byte).

    if unit is free, value is None
    """
    value: Optional[str] = None


@dataclass
class MemoryBlock:
    units: list[MemoryUnit]
    id: UUID = uuid4()

    def write(self, data: str):
        """
        Writes/Overwrites the value to the memory block.

        Args:
            data: The string value to write to the memory block.
        """
        if len(self.units) < 1:
            raise MemoryError("Cannot write to a freed memory block.")

        if len(data) > len(self.units):
            raise MemoryError("data length exceeds memory block size.")
        
        for i in range(len(data)):
            self.units[i].value = data[i]
        
        # Fill the rest with None if data is shorter
        for i in range(len(data), len(self.units)):
            self.units[i].value = None
    
    def read(self) -> str:
        """
        Returns the string representation of the memory block.
        """
        return ''.join(unit.value for unit in self.units if unit.value != None)
    
    def __len__(self):
        return len(self.units)


class MemoryManager:
    
    buffer: list[MemoryUnit]
    next_alloc_index: int = 0
    allocated_blocks: dict[UUID, MemoryBlock] = {}
    freed_fragmented_units: list[MemoryUnit] = [] # Stack of freed memory units
    
    def __init__(self, buffer_size: int):
        """Initialize the memory manager with a contiguous buffer.
        
        Args:
            buffer_size: The total size of the memory buffer in bytes.
        """
        if buffer_size <= 0:
            raise ValueError("Buffer size must be a positive integer.")

        self.buffer = [MemoryUnit() for _ in range(buffer_size)]
        self.next_alloc_index = 0
    
    def _free_buffer_size(self) -> int:
        """Returns the total free size in the buffer."""
        return len(self.buffer) - self.next_alloc_index + len(self.freed_fragmented_units)
    
    def alloc(self, size: int) -> MemoryBlock:
        """Allocates a block of memory of the given size.
        
        Args:
            size: The number of bytes to allocate from the buffer.
            
        Returns:
            The allocated memory block.
        """
        if size <= 0:
            raise ValueError("Allocation size must be a positive integer.")

        # Check if there is enough space to allocate
        if self._free_buffer_size() < size:
            raise MemoryError("Not enough memory to allocate the requested block.")
    
        # Allocate the memory block from the buffer
        allocated_units = []
        
        if self.freed_fragmented_units:
            while size > 0 and self.freed_fragmented_units:
                unit = self.freed_fragmented_units.pop()
                allocated_units.append(unit)
                size -= 1

        allocated_units.extend(
            self.buffer[self.next_alloc_index:self.next_alloc_index + size]
        )
        self.next_alloc_index += size

        new_block = MemoryBlock(units=allocated_units, id=uuid4())
        self.allocated_blocks[new_block.id] = new_block
        return new_block
    
    def free(self, block: MemoryBlock):
        """Frees the given memory block.
        
        Args:
            block: The memory block to free.
        """
        if block.id not in self.allocated_blocks:
            raise ValueError("The provided block is not allocated by this manager.")
        
        # Mark the memory units as free (None)
        for unit in block.units:
            unit.value = None
        
        # Add the freed units' indices to the freed fragmented units stack
        self.freed_fragmented_units.extend(block.units)

        # Delete references to the block's units
        block.units = []
        
        # Remove the block from allocated blocks
        del self.allocated_blocks[block.id]


    def defragment(self):
        """Defragments the memory buffer to consolidate free space.  
        """
        new_buffer = []

        i = 0
        for block in self.allocated_blocks.values():
            for unit in block.units:
                new_buffer.append(MemoryUnit(value=unit.value))
                i += 1
            # Update block units to point to new buffer units
            block.units = new_buffer[i - len(block.units):i]
        
        # Fill the rest of the buffer with free units
        while len(new_buffer) < len(self.buffer):
            new_buffer.append(MemoryUnit())
        
        del self.buffer
        self.buffer = new_buffer
        self.next_alloc_index = i
        self.freed_fragmented_units.clear()

    def __repr__(self):
        """
        Returns a string representation of the memory manager's state.
        
        Can be improved
        """
        return(
            f"MemoryManager(buffer_size={len(self.buffer)}, " +\
            f"next_alloc_index={self.next_alloc_index}, " +\
            f"allocated_blocks={len(self.allocated_blocks)}, " +\
            f"freed_fragmented_units={len(self.freed_fragmented_units)}, " +\
            f"free_buffer_size={self._free_buffer_size()}) \n" +\
            
            f"Buffer State: [{' '.join([unit.value if unit.value is not None else '-' for unit in self.buffer])}]"
        )