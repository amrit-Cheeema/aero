import unittest
from mymath import *

class testSet(unittest.TestCase):
    def test_creation(self):
        """Tests initial state and duplicate handling during instantiation."""
        self.assertEqual(Set(1).set, {1})
        self.assertEqual(Set(1, "a").set, {1, "a"})
        self.assertEqual(Set(1, "a", 2, 2).set, {1, 2, "a"})
        self.assertEqual(Set(1, "a", 2, 2).set, {1, 2, "a"})
    def test_cartesian_product(self):
        """Tests the multiplication (*) of two sets."""
        s1 = Set(1, 2)
        s2 = Set("a", "b")
        
        # Expected: {(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')}
        result = s1 * s2
        
        self.assertEqual(len(result.set), 4)
        self.assertIn(OrderedPair(1, "a"), result.set)
        self.assertIn(OrderedPair(1, "b"), result.set)
        self.assertIn(OrderedPair(2, "a"), result.set)
        self.assertIn(OrderedPair(2, "b"), result.set)
    
    def test_cartesian_product_empty(self):
        """The product of any set and an empty set is an empty set."""
        s1 = Set(1, 2)
        s2 = Set()
        
        result = s1 * s2
        self.assertEqual(len(result.set), 0)

    def test_cartesian_product_identity(self):
        """Multiplying a set by itself (S^2)."""
        s = Set(1)
        result = s * s
        self.assertEqual(result.set, {OrderedPair(1, 1)})
    
    def test_empty_set(self):
        """Ensures the class handles no arguments gracefully."""
        self.assertEqual(Set().set, set())
    
    def test_contains(self):
        """Tests the 'in' keyword functionality (requires __contains__)."""
        s = Set("apple", "orange")
        self.assertTrue("apple" in s)
        self.assertFalse("banana" in s)
    
    def test_add(self):
        """Tests adding new elements and ensuring duplicates aren't added."""
        s = Set(1, 2)
        s.add(3)
        self.assertIn(3, s.set)
        s.add(2)  # Duplicate
        self.assertEqual(len(s.set), 3)


class TestPredicateSet(unittest.TestCase):

    def setUp(self):
        # Define reusable base sets
        self.even_set = SetConstruct(lambda x: x % 2 == 0)
        self.positive_set = SetConstruct(lambda x: x > 0)
        self.multiple_of_5 = SetConstruct(lambda x: x % 5 == 0)

    def test_creation(self):
        """Verify basic predicate evaluation."""
        self.assertTrue(self.even_set(2))
        self.assertFalse(self.even_set(3))
        self.assertTrue(self.positive_set(100))
        self.assertFalse(self.positive_set(-5))

    def test_and_operation(self):
        """Intersection: x must satisfy both predicates."""
        even_and_positive = self.even_set & self.positive_set
        
        self.assertTrue(even_and_positive(2))    # Even and Positive
        self.assertFalse(even_and_positive(-2))  # Even but NOT Positive
        self.assertFalse(even_and_positive(3))   # Positive but NOT Even

    def test_or_operation(self):
        """Union: x must satisfy at least one predicate."""
        even_or_positive = self.even_set | self.positive_set
        
        self.assertTrue(even_or_positive(2))     # Satisfies both
        self.assertTrue(even_or_positive(-2))    # Satisfies Even
        self.assertTrue(even_or_positive(3))     # Satisfies Positive
        self.assertFalse(even_or_positive(-3))   # Satisfies neither

    def test_not_operation(self):
        """Complement: x must NOT satisfy the predicate."""
        odd_set = ~self.even_set
        
        self.assertTrue(odd_set(3))
        self.assertFalse(odd_set(4))

    def test_nested_logic(self):
        """Verify complex chaining: (A AND B) OR C."""
        # Positive evens OR any multiple of 5
        complex_set = (self.even_set & self.positive_set) | self.multiple_of_5
        
        self.assertTrue(complex_set(2))    # Positive Even
        self.assertTrue(complex_set(-5))   # Multiple of 5 (even though negative/odd)
        self.assertFalse(complex_set(-2))  # Even, but not positive and not mult of 5
        self.assertFalse(complex_set(3))   # Satisfies nothing

    def test_infinite_domain_limits(self):
        """Ensure it handles large/edge cases correctly."""
        large_even = 10**12
        self.assertTrue(self.even_set(large_even))
        self.assertFalse(self.positive_set(-10**12))

if __name__ == '__main__':
    unittest.main()