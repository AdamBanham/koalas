import unittest

from pmkoalas._struct import OutOfMemoryQueue, OutOfMemorySet
from pmkoalas.dtlog import convertTrace

class NoMemoryTest(unittest.TestCase):

    def test_set(self):
        true_set = set()
        no_mem_set = OutOfMemorySet()
        trace = convertTrace("a b c d")
        true_set.add(trace)
        no_mem_set.add(trace)
        self.assertEqual(len(true_set), len(no_mem_set), "Sets are not the same size.")
        self.assertIn(trace, no_mem_set, "Trace not in set")
        trace_b = convertTrace("a b c d e")
        trace_c = convertTrace("a b c d e f")
        true_set.add(trace_b)
        true_set.add(trace_c)
        no_mem_set.add(trace_b)
        no_mem_set.add(trace_c)
        self.assertEqual(len(true_set), len(no_mem_set), "Sets are not the same size.")
        self.assertIn(trace_b, no_mem_set, "Trace not in set")
        self.assertIn(trace_c, no_mem_set, "Trace not in set")
        count = 0 
        for item in no_mem_set:
            count += 1
            self.assertIn(item, true_set, "Item not in true set")
            self.assertIn(item, no_mem_set, "Item not in no mem set")
        self.assertEqual(count, len(true_set), "Not all items in set")

    def test_queue(self):
        true_queue = list()
        no_mem_queue = OutOfMemoryQueue() 
        trace = convertTrace("a b c d")
        true_queue.append(trace)
        no_mem_queue.append(trace)
        self.assertEqual(len(true_queue), len(no_mem_queue), "Queues are not the same size.")
        self.assertIn(trace, no_mem_queue, "Trace not in set")
        trace_b = convertTrace("a b c d e")
        trace_c = convertTrace("a b c d e f")
        true_queue.append(trace_b)
        true_queue.append(trace_c)
        no_mem_queue.append(trace_b)
        no_mem_queue.append(trace_c)
        self.assertEqual(len(true_queue), len(no_mem_queue), "Queues are not the same size.")
        count = 0
        for item in no_mem_queue:
            count += 1
            self.assertIn(item, true_queue, "Item not in true queue")
        self.assertEqual(count, len(true_queue), "Not all items in queue")
        self.assertEqual(count, len(no_mem_queue), "Queues are not the same size.")
        
        for _ in range(1000):
            no_mem_queue.append(convertTrace("a b c d e f g h i j k l m n o p q r s t u v w x y z"))
        self.assertEqual(len(no_mem_queue), 1003, "Queue is not the right size")
        count = 0
        for item in no_mem_queue:
            count += 1
        self.assertEqual(count, 1003, "Not all items in queue")