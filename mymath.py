import inspect


class Set:
    """
    **Allows the creating of set with collection of objects**

    Usage:
     - randSet = Set(1, "a", OrderedPair(1, "b"))
    """
    def __init__(self, *args):
        elements = args
        self.set: set | None = set(elements) if elements else set()
    def add(self, item):
        """Adds an element to the set. If it exists, nothing happens."""
        self.set.add(item)
    def __len__(self):
        """Allows the use of len(set_obj)"""
        return len(self.set)
    def __add__(self, other):
        """Union of two sets: set1 + set2"""
        if not isinstance(other, Set):
            raise TypeError("Can only add another Set.")
        new_set = Set()
        new_set.set = self.set.union(other.set)
        return new_set
    def __mul__(self, other):
        if not isinstance(other, Set):
            raise TypeError("Can only add another Set.")
        CartisianSet = Set()
        for e1 in self.set:
            for e2 in other:
                CartisianSet.add(OrderedPair(e1, e2))
        return CartisianSet
    def __sub__(self, other):
        if not isinstance(other, Set):
            raise TypeError("Can only add another Set.")
        new_set = Set()
        new_set.set = self.set.difference(other.set)
        return new_set
    # formating functions
    def __repr__(self):
        items = sorted(list(self.set), key=lambda x: str(x))
        return f"{{{', '.join(map(str, items))}}}"
    def __iter__(self):
        return iter(self.set)

class OrderedPair:
    def __init__(self, first, second):
        # Used pointers internally for maximum efficiency
        # However you can use sets
        self.first = first
        self.second = second
    def __hash__(self):
        # Necessary so OrderedPairs can be stored in a Set
        return hash((self.first, self.second))
    def __eq__(self, other):
        return isinstance(other, OrderedPair) and \
               self.first == other.first and self.second == other.second
    def __iter__(self):
        yield self.first
        yield self.second
    def __repr__(self):
        return f"({self.first}, {self.second})"

class SetConstruct:
    """
    **Handles making sets with an infinte domain using predicats**

    Usage:
     - even_set = SetConstruct(lambda x: x % 2 == 0)
    """
    def __init__(self, predicate: callable[[int], bool],expr=None):
        self.predicate = predicate
        if expr is None:
            try:
                source = inspect.getsourcelines(predicate)[0][0].strip()
                if "lambda" in source:
                    # Extracts everything after 'lambda x:'
                    self.expr = source.split("lambda")[-1].split(":")[-1].strip().rstrip(",)")
                else:
                    self.expr = f"{predicate.__name__}(x)"
            except Exception:
                self.expr = "f(x)"
        else:
            self.expr = expr
    def __and__(self, other):
        return SetConstruct(
            lambda x: self.predicate(x) and other.predicate(x),
            expr=f"({self.expr} ∧ {other.expr})"
        )

    def __or__(self, other):
        return SetConstruct(
            lambda x: self.predicate(x) or other.predicate(x),
            expr=f"({self.expr} ∨ {other.expr})"
        )

    def __invert__(self):
        return SetConstruct(
            lambda x: not self.predicate(x),
            expr=f"¬({self.expr})"
        )
    def __contains__(self, x):
        return bool(self.predicate(x))
    def __repr__(self):
        return f"{{ x | {self.expr} }}"
    def __sub__(self, other):
        """Difference: A - B (In A but NOT in B)"""
        return self & ~other
    def __call__(self, x):
        return self.predicate(x)
    
    def __repr__(self):
        return f"{{ x | {self.expr} }}"


D = Set(1, 2, 3)
C = Set(1, 'c')
print(D*C)

# Usage
g_2 = SetConstruct(lambda x: x > 2)
g_10 = SetConstruct(lambda x: x > 10)
odd_set = SetConstruct(lambda x: x % 2 == 1)
combined = g_2 & ~odd_set
print(40 in combined)


# print(1.1 in even_set)
# all_sets = even_set + odd_set
# print(1 in all_sets)
# Mapping 1->a, 2->b, 3->a (Valid function, not injective)
# m = Set(OrderedPair(1, 'a'), OrderedPair(2, 'b'), OrderedPair(3, 'a'))
# f = Function(D, C, m)

# print(m) # Output: 'b'