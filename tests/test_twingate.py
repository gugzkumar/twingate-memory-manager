import unittest
from twingate import MemoryUnit, MemoryBlock


class TestMemoryUnit(unittest.TestCase):
    def test_memory_unit_initialization(self):
        mu = MemoryUnit()
        self.assertIsNone(mu.value)

    def test_memory_unit_with_value(self):
        mu = MemoryUnit(value='A')
        self.assertEqual(mu.value, 'A')

    def test_memory_unit_with_null_char_value(self):
        mu = MemoryUnit(value='\0')
        self.assertEqual(mu.value, '\0')

class TestMemoryBlock(unittest.TestCase):
    def test_memory_block_initialization(self):
        mu1 = MemoryUnit(value='A')
        mu2 = MemoryUnit(value='B')
        mb = MemoryBlock(units=[mu1, mu2])
        self.assertEqual(len(mb), 2)
        self.assertEqual(mb.units[0].value, 'A')
        self.assertEqual(mb.units[1].value, 'B')

    def test_memory_block_write_and_read(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2])
        
        mb.write('CD')
        self.assertEqual(mb.read(), 'CD')

    def test_memory_block_write_with_incorrect_length(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2])
        
        with self.assertRaises(MemoryError):
            mb.write('CDE')
    
    def test_memory_block_can_write_twice(self):
        mu1 = MemoryUnit()
        mu2 = MemoryUnit()
        mb = MemoryBlock(units=[mu1, mu2])
        
        mb.write('EF')
        self.assertEqual(mb.read(), 'EF')
        
        mb.write('G')
        self.assertEqual(mb.read(), 'G')