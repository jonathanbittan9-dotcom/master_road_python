"""
03_data_structures_algorithms.py

Section 3: Data Structures & Algorithms
    - Big-O complexity (time and space)
    - Arrays, linked lists, stacks, queues, hash maps, trees, graphs, heaps
    - Sorting/searching
    - Recursion and dynamic programming

Run: python 03_data_structures_algorithms.py
"""

import functools
import sys
import time
import heapq
# New words in this line:
#   heapq  -> standard library module providing heap / priority-queue
#             operations that work directly on a plain list
from collections import deque
# New words in this line:
#   deque ("deck")  -> like a list, but appending/popping from the FRONT is
#        O(1) instead of O(n) (a plain list has to shift every remaining
#        element over)


# ---------------------------------------------------------------------------
# Big-O — seeing complexity, not just reading about it
# ---------------------------------------------------------------------------
def demo_big_o():
    print("\n--- Big-O in practice ---")

    # O(n) lookup: list.__contains__ scans every element
    big_list = list(range(200_000))
    # New words in this line:
    #   200_000 (underscore inside a number literal)  -> purely a readability
    #        aid — Python ignores the underscores; 200_000 and 200000 are the
    #        identical integer
    start = time.perf_counter()
    199_999 in big_list
    # New words in this line:
    #   x in y (as a standalone expression)  -> membership test, returning
    #        True/False (already used as `not in` inside an `if` in
    #        core_language_mastery.py — this line just shows it works
    #        standalone too, and its RESULT is being timed)
    print(f"list lookup (O(n)):  {time.perf_counter() - start:.6f}s")

    # O(1) lookup: set/dict use hashing
    big_set = set(big_list)
    # New words in this line:
    #   set(iterable)  -> built-in function: builds a set out of any
    #        iterable, here converting the list into a set with the same items
    start = time.perf_counter()
    199_999 in big_set
    print(f"set lookup  (O(1)):  {time.perf_counter() - start:.6f}s")
    # Same question, wildly different cost, purely from choosing the right structure.


# ---------------------------------------------------------------------------
# Stack (LIFO) — using a plain list
# ---------------------------------------------------------------------------
def demo_stack():
    print("\n--- Stack (LIFO) ---")
    stack = []
    stack.append("a")   # push
    stack.append("b")
    stack.append("c")
    print("popped:", stack.pop())
    # New words in this line:
    #   .pop() (no argument)  -> list method: removes AND returns the LAST
    #        item — 'c' here, proving last-in-first-out behavior
    print("remaining:", stack)


# ---------------------------------------------------------------------------
# Queue (FIFO) — using collections.deque (O(1) at both ends, unlike a list)
# ---------------------------------------------------------------------------
def demo_queue():
    print("\n--- Queue (FIFO) ---")
    queue = deque()
    queue.append("a")     # enqueue
    queue.append("b")
    queue.append("c")
    print("dequeued:", queue.popleft())
    # New words in this line:
    #   .popleft()  -> deque method: removes AND returns from the FRONT in
    #        O(1); a plain list's .pop(0) does the same thing but is O(n)
    #        because every remaining element has to shift left
    print("remaining:", queue)


# ---------------------------------------------------------------------------
# Linked List (built by hand — Python doesn't have one built in)
# ---------------------------------------------------------------------------
class Node:
    def __init__(self, value, next=None):
        # New words in this line:
        #   next=None  -> a default parameter value: makes `next` optional
        #        for callers — Node(5) works exactly like Node(5, None) would
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None

    def push_front(self, value):
        self.head = Node(value, self.head)

    def to_list(self):
        result, node = [], self.head
        while node:
            result.append(node.value)
            node = node.next
        return result


def demo_linked_list():
    print("\n--- Linked List ---")
    ll = LinkedList()
    ll.push_front("c")
    ll.push_front("b")
    ll.push_front("a")
    print("as list:", ll.to_list())
    # Insert at the FRONT is O(1) here, vs O(n) for list.insert(0, x)


# ---------------------------------------------------------------------------
# Hash Map — Python's dict IS a hash map
# ---------------------------------------------------------------------------
def demo_hash_map():
    print("\n--- Hash Map (dict) ---")
    book_availability = {"1984": True, "Dune": False}
    book_availability["Foundation"] = True   # O(1) insert
    print(book_availability.get("Dune"))     # O(1) lookup


# ---------------------------------------------------------------------------
# Binary Tree
# ---------------------------------------------------------------------------
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert(self.root, value)

    def _insert(self, node, value):
        # (leading-underscore naming convention already introduced in
        # 02_oop_design_principles.py's AppConfig._instance — signals
        # "internal helper, don't call this from outside the class")
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert(node.right, value)

    def in_order(self):
        result = []

        def walk(node):
            if node:
                walk(node.left)
                result.append(node.value)
                walk(node.right)

        walk(self.root)
        return result


def demo_tree():
    print("\n--- Binary Search Tree ---")
    bst = BinarySearchTree()
    for value in [5, 3, 8, 1, 4, 7, 9]:
        bst.insert(value)
    print("in-order (sorted!):", bst.in_order())


# ---------------------------------------------------------------------------
# Graph — adjacency list + BFS/DFS
# ---------------------------------------------------------------------------
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": ["E"],
    "E": [],
}


def bfs(start):
    visited, queue, order = {start}, deque([start]), []
    # New words in this line:
    #   {start}  -> a SET literal containing one item. Curly braces with no
    #        colon make a set (dedupes automatically); curly braces WITH a
    #        colon, like {"a": 1}, make a dict instead — same braces, the
    #        colon is what distinguishes them
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs(start, visited=None, order=None):
    # `visited=None, order=None` — defaults to None rather than mutable
    # objects like [] or set() directly. This is a classic Python gotcha
    # being sidestepped: NEVER write `def dfs(start, visited=set()):`.
    # Default argument values are created ONCE, when the function is
    # DEFINED, not fresh on every call — so a mutable default would be
    # silently SHARED and accumulate stale data across unrelated calls
    # (e.g. every dfs() call reusing the same set across different graphs).
    # The fix, shown below: default to None, then create a real empty
    # set/list inside the function body if none was passed in.
    if visited is None:
        visited, order = set(), []
        # New words in this line:
        #   set()  -> built-in function creating an EMPTY set (can't write
        #        {} for this — that makes an empty DICT instead)
    visited.add(start)
    order.append(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(neighbor, visited, order)
    return order


def demo_graph():
    print("\n--- Graph: BFS vs DFS ---")
    print("BFS from A:", bfs("A"))
    print("DFS from A:", dfs("A"))


# ---------------------------------------------------------------------------
# Heap — always pop the smallest (or largest, with negation)
# ---------------------------------------------------------------------------
def demo_heap():
    print("\n--- Heap (priority queue) ---")
    tasks = []
    # heapq works on a plain list, but you must only modify it through
    # heapq's functions — it keeps the list secretly ordered as a "heap"
    # (a tree laid out in an array) so the SMALLEST item is always available
    # at tasks[0] in O(1).
    heapq.heappush(tasks, (2, "medium priority"))
    # New words in this line:
    #   heapq.heappush(list, item)  -> inserts `item` into the list while
    #        maintaining the heap ordering
    heapq.heappush(tasks, (1, "high priority"))
    heapq.heappush(tasks, (3, "low priority"))
    # Tuples compare element-by-element, so (1, "high priority") sorts before
    # (2, "medium priority") purely because 1 < 2 — that's why priority is
    # placed FIRST in each tuple.

    while tasks:
        priority, task = heapq.heappop(tasks)
        # New words in this line:
        #   heapq.heappop(list)  -> removes AND returns the SMALLEST item in
        #        O(log n), keeping the rest of the list correctly heap-ordered
        print(f"priority={priority}: {task}")


# ---------------------------------------------------------------------------
# Sorting & Searching
# ---------------------------------------------------------------------------
def bubble_sort(items):
    """O(n^2) — shown for learning, never use this in real code."""
    items = items.copy()
    n = len(items)
    # New words in this line:
    #   len(items)  -> built-in function: the number of elements in a
    #        list/string/dict/etc.
    for i in range(n):
        for j in range(n - i - 1):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                # New words in this line:
                #   a, b = b, a (tuple-swap idiom)  -> swaps two values
                #        without a temporary variable; the right side
                #        (items[j+1], items[j]) is built as a tuple FIRST,
                #        then unpacked into the left side's two targets
    return items


def binary_search(sorted_items, target):
    """O(log n) — requires the list to already be sorted."""
    low, high = 0, len(sorted_items) - 1
    while low <= high:
        mid = (low + high) // 2
        # New words in this line:
        #   //  -> floor division: divides and rounds DOWN to the nearest
        #        whole number (regular `/` would give a float, e.g. 3.5)
        if sorted_items[mid] == target:
            return mid
        elif sorted_items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def demo_sorting_searching():
    print("\n--- Sorting & Searching ---")
    unsorted = [5, 2, 8, 1, 9, 3]
    sorted_items = bubble_sort(unsorted)
    print("bubble sort:", sorted_items)
    print("built-in sorted() — always prefer this in real code:", sorted(unsorted))
    # New words in this line:
    #   sorted(iterable)  -> built-in function: returns a NEW sorted list,
    #        leaving the original unsorted list untouched (unlike bubble_sort
    #        above, which also happens to return a new list via .copy(), but
    #        many other in-place approaches, like list.sort(), modify and
    #        return None instead)
    print("binary_search for 8:", binary_search(sorted_items, 8))


# ---------------------------------------------------------------------------
# Sorting with a key function
# ---------------------------------------------------------------------------
def demo_sort_key():
    print("\n--- sorted(key=...) ---")

    books = [
        {"title": "1984", "pages": 328},
        {"title": "Dune", "pages": 412},
        {"title": "Foundation", "pages": 255},
    ]

    by_pages = sorted(books, key=lambda b: b["pages"])
    # New words in this line:
    #   key=lambda item: expr  -> tells sorted() what to compare INSTEAD of
    #        the items themselves — here, each dict gets compared by its
    #        "pages" value rather than Python trying (and failing) to compare
    #        two dicts directly. The lambda runs once per item, not once per
    #        COMPARISON, so this stays efficient even on long lists.
    print("by pages:", [b["title"] for b in by_pages])

    by_title_length = sorted(books, key=lambda b: len(b["title"]), reverse=True)
    # New words in this line:
    #   reverse=True  -> sorts descending instead of the default ascending
    print("longest title first:", [b["title"] for b in by_title_length])
    # Real-world use of this exact pattern: sorting a leaderboard by score,
    # or a list of Book domain objects (04_software_architecture.py) by
    # `key=lambda b: b.title` instead of a dict key.


# ---------------------------------------------------------------------------
# Two-Pointer Technique — O(n) instead of the naive O(n^2) nested loop
# ---------------------------------------------------------------------------
def has_pair_with_sum(sorted_items, target):
    """Do any two numbers in a SORTED list add up to target?"""
    left, right = 0, len(sorted_items) - 1
    # New words in this line:
    #   left, right  -> two indices, starting at OPPOSITE ends of the list —
    #        the "two pointers" the technique is named for
    while left < right:
        current_sum = sorted_items[left] + sorted_items[right]
        if current_sum == target:
            return sorted_items[left], sorted_items[right]
        elif current_sum < target:
            left += 1    # sum too small -> move the LEFT pointer up to grow it
        else:
            right -= 1   # sum too big -> move the RIGHT pointer down to shrink it
    return None
    # Why this beats a nested loop: a naive `for i: for j:` check is O(n^2) —
    # every pair gets compared. Because the list is SORTED, moving either
    # pointer in the right direction rules out a whole range of pairs at
    # once, so the whole scan is O(n) — each pointer moves at most n times
    # total, never backwards.


def demo_two_pointer():
    print("\n--- Two-Pointer Technique ---")
    numbers = [1, 3, 4, 6, 8, 11, 15]
    print("pair summing to 14:", has_pair_with_sum(numbers, 14))
    print("pair summing to 5:", has_pair_with_sum(numbers, 5))
    print("pair summing to 100 (none exists):", has_pair_with_sum(numbers, 100))


# ---------------------------------------------------------------------------
# Recursion & Dynamic Programming
# ---------------------------------------------------------------------------
def fib_naive(n):
    """O(2^n) — recomputes the same values over and over. Try fib_naive(30)+ and feel it."""
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n, cache=None):
    """O(n) — dynamic programming: remember answers you've already computed."""
    # (same None-sentinel pattern as dfs() above, sidestepping the mutable-
    # default-argument gotcha — here with an empty dict instead of a set)
    if cache is None:
        cache = {}
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


def demo_recursion_dp():
    print("\n--- Recursion & Dynamic Programming ---")

    start = time.perf_counter()
    result_naive = fib_naive(25)
    time_naive = time.perf_counter() - start

    start = time.perf_counter()
    result_memo = fib_memo(25)
    time_memo = time.perf_counter() - start

    print(f"naive fib(25)={result_naive} in {time_naive:.6f}s")
    print(f"memo  fib(25)={result_memo} in {time_memo:.6f}s")
    print("Same answer, memoized version is dramatically faster — that's DP.")


@functools.lru_cache(maxsize=None)
# New words in this line:
#   @functools.lru_cache(maxsize=None)  -> the standard-library version of
#        the same idea as fib_memo's hand-written `cache = {}` above — see
#        core_language_mastery.py's lru_cache section for the full
#        explanation. Shown here specifically to compare against fib_memo:
#        same O(n) result, zero manual cache-dict bookkeeping.
def fib_lru(n):
    if n <= 1:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)


def demo_recursion_limit():
    print("\n--- Recursion depth limit ---")

    print("fib_lru(25) via lru_cache:", fib_lru(25))
    print("default recursion limit:", sys.getrecursionlimit())
    # New words in this line:
    #   sys.getrecursionlimit()  -> Python (unlike some languages) does NOT
    #        optimize away deep recursion — every recursive call adds a real
    #        frame to the call stack, and Python caps how deep that's allowed
    #        to go (1000 by default) to avoid crashing the whole process with
    #        a C-level stack overflow.

    def count_down(n):
        if n <= 0:
            return 0
        return count_down(n - 1)

    try:
        count_down(10_000)
    except RecursionError as e:
        # New words in this line:
        #   RecursionError  -> the specific built-in exception Python raises
        #        once a call chain hits that limit — a signal to either
        #        rewrite the recursion as a loop, or (rarely) raise the limit
        #        with sys.setrecursionlimit(n), which just moves the ceiling,
        #        it doesn't remove it
        print("Expected error:", e)
    # fib_naive(25) above is already ~half a million calls DEEP in branching
    # (not stack DEPTH — it returns before recursing further each time), so
    # it doesn't hit this; count_down(10_000) hits it because each call
    # stays on the stack waiting for the one below it to return first.


if __name__ == "__main__":
    demo_big_o()
    demo_stack()
    demo_queue()
    demo_linked_list()
    demo_hash_map()
    demo_tree()
    demo_graph()
    demo_heap()
    demo_sorting_searching()
    demo_sort_key()
    demo_two_pointer()
    demo_recursion_dp()
    demo_recursion_limit()
