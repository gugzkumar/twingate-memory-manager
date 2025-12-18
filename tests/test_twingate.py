import unittest
from twingate import MemoryUnit, MemoryBlock, MemoryManager
from uuid import uuid4


class TestMemoryUnit(unittest.TestCase):
    def test_memory_unit_initialization(self):
        mu = MemoryUnit()
        self.assertIsNone(mu.value)

    def test_memory_unit_with_value(self):
        mu = MemoryUnit(value='A')
        self.assertEqual(mu.value, 'A')

class TestMemoryBlock(unittest.TestCase):
    def test_memory_block_initialization(self):
        mu1 = MemoryUnit(value='A')
        mu2 = MemoryUnit(value='B')
        mb = MemoryBlock(units=[mu1, mu2], id=uuid4())
        self.assertEqual(len(mb), 2)
        self.assertEqual(mb.units[0].value, 'A')
        self.assertEqual(mb.units[1].value, 'B')

    def test_memory_block_write_and_read(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2], id=uuid4())
        
        mb.write('CD')
        self.assertEqual(mb.read(), 'CD')

    def test_memory_block_write_with_incorrect_length(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2], id=uuid4())
        
        with self.assertRaises(MemoryError):
            mb.write('CDE')
    
    def test_memory_block_can_write_twice(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2], id=uuid4())
        
        mb.write('EF')
        self.assertEqual(mb.read(), 'EF')
        
        mb.write('G')
        self.assertEqual(mb.read(), 'G')

class TestMemoryManager(unittest.TestCase):

    def test_memory_manager_initialization_and_alloc_use(self):
        mm = MemoryManager(10)
        self.assertEqual(len(mm.buffer), 10)
        self.assertEqual(mm.next_alloc_index, 0)
        self.assertEqual(len(mm.allocated_blocks), 0)
        self.assertEqual(len(mm.freed_fragmented_units), 0)

        # Write entire buffer
        b = mm.alloc(10)
        b.write('ABCDEFGHIJ')
        self.assertEqual(b.read(), 'ABCDEFGHIJ')
    
    def test_memory_manager_alloc_and_free(self):
        mm = MemoryManager(5)
        self.assertEqual(len(mm.buffer), 5)
        
        b1 = mm.alloc(2)
        b2 = mm.alloc(2)
        
        self.assertEqual(len(mm.allocated_blocks), 2)
        self.assertEqual(len(b1), 2)
        self.assertEqual(len(b2), 2)
        self.assertEqual(mm._free_buffer_size(), 1)
        self.assertEqual(len(mm.freed_fragmented_units), 0)
        self.assertEqual(mm.next_alloc_index, 4)
        
        mm.free(b1)
        self.assertRaises(MemoryError, lambda: b1.write('AB')) # b1 is freed so writing should raise error
        self.assertEqual(len(mm.allocated_blocks), 1)
        self.assertEqual(mm._free_buffer_size(), 3)
        self.assertEqual(len(mm.freed_fragmented_units), 2)
        self.assertEqual(mm.next_alloc_index, 4)
        
        mm.free(b2)
        self.assertRaises(MemoryError, lambda: b2.write('AB')) # b2 is freed so writing should raise error
        self.assertEqual(len(mm.allocated_blocks), 0)
        self.assertEqual(mm._free_buffer_size(), 5)
        self.assertEqual(len(mm.freed_fragmented_units), 4)
        self.assertEqual(mm.next_alloc_index, 4)
    
    def test_alloc_with_insufficient_memory(self):
        mm = MemoryManager(3)
        b1 = mm.alloc(2)
        
        # Not enough  memory
        with self.assertRaises(MemoryError):
            mm.alloc(2)
        
        # Use all freed fragmented units
        mm.free(b1)
        b2 = mm.alloc(3)
        b2.write('XYZ')
        self.assertEqual(b2.read(), 'XYZ')
        self.assertEqual(mm._free_buffer_size(), 0)

        # No memory left
        with self.assertRaises(MemoryError):
            mm.alloc(1)

    def test_memory_manager_defragment(self):
        mm = MemoryManager(6)
        b1 = mm.alloc(2)
        b2 = mm.alloc(2)
        b3 = mm.alloc(2)
        b1.write('AB')
        b2.write('CD')
        b3.write('EF')
        
        mm.free(b1)
        mm.free(b3)
        
        self.assertEqual(mm._free_buffer_size(), 4)
        self.assertEqual(len(mm.freed_fragmented_units), 4)
        self.assertEqual(mm.next_alloc_index, 6)
        
        mm.defragment()
        self.assertEqual(mm._free_buffer_size(), 4)
        self.assertEqual(len(mm.freed_fragmented_units), 0)
        self.assertEqual(mm.next_alloc_index, 2)

        # Check that b2's data is intact
        self.assertEqual(b2.read(), 'CD')
    
    def test_0_size_allocation(self):
        with self.assertRaises(ValueError):
            MemoryManager(0)
        
        mm = MemoryManager(5)
        with self.assertRaises(ValueError):
            mm.alloc(0)
        