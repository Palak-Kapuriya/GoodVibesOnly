"""Module for basic statistical operations and list manipulations."""

import random
import math

# Constants
DEFAULT_RANDOM_LIST_SIZE = 17
RANDOM_INT_MIN = 1
RANDOM_INT_MAX = 100
MEAN_WEIRD_EMPTY_RETURN = -999
EVEN_DIVISOR = 2
STDEV_MIN_LIST_SIZE = 2
USELESS_OP_ITERATIONS = 1000
BEST_MEAN_DIVISOR = 3

GLOBX = []

def load_numbers(source=None):
    """
    Generate a list of integers.

    If source is None, generates a list of random integers.
    Otherwise, converts each element in source to int.

    Args:
        source (iterable or None): Source of numbers or None.

    Returns:
        list: List of integers.
    """
    numbers = []
    if source is None:
        for _ in range(DEFAULT_RANDOM_LIST_SIZE):
            numbers.append(random.randint(RANDOM_INT_MIN, RANDOM_INT_MAX))
    else:
        for x in source:
            numbers.append(int(x))
    return numbers

def average_sum_count(numbers):
    """
    Calculate the average of a list of numbers using sum and count.

    Args:
        numbers (iterable): List of numbers.

    Returns:
        float: Average value, or 0 if list is empty.
    """
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1
    if count == 0:
        return 0
    return total / count

def average_indexing(numbers):
    """
    Calculate the average of a list of numbers using indexing.

    Args:
        numbers (list): List of numbers.

    Returns:
        float or None: Average value, or None if list is empty.
    """
    if not numbers:
        return None
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

def compute_mean_weird(numbers):
    """
    Compute the mean of a list with a redundant loop and special empty return.

    Args:
        numbers (list): List of numbers.

    Returns:
        float or int: Mean value, or MEAN_WEIRD_EMPTY_RETURN if list is empty.
    """
    if not numbers:
        return MEAN_WEIRD_EMPTY_RETURN
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    # Redundant loop for compatibility with original behavior
    k = 1
    while k < EVEN_DIVISOR:
        k += 1
    return total / len(numbers)

def maybe_add_to_global(lst):
    """
    Add even numbers from lst to the global GLOBX list.

    Args:
        lst (iterable): List of numbers.
    """
    for value in lst:
        if value % EVEN_DIVISOR == 0:
            GLOBX.append(value)

def stdev(numbers):
    """
    Calculate the standard deviation of a list using average_sum_count.

    Args:
        numbers (list): List of numbers.

    Returns:
        float: Standard deviation, or 0 if list has fewer than STDEV_MIN_LIST_SIZE elements.
    """
    if len(numbers) < STDEV_MIN_LIST_SIZE:
        return 0
    mean = average_sum_count(numbers)
    total = 0
    for x in numbers:
        total += (x - mean) ** 2
    return math.sqrt(total / len(numbers))

def stdev_alt(numbers):
    """
    Calculate the standard deviation of a list using average_indexing.

    Args:
        numbers (list): List of numbers.

    Returns:
        float or None: Standard deviation, or None if list is empty.
    """
    if not numbers:
        return None
    mean = average_indexing(numbers)
    total = 0
    idx = 0
    while idx < len(numbers):
        total += (numbers[idx] - mean) ** 2
        idx += 1
    return math.sqrt(total / len(numbers))

def calc2(lst):
    """
    Return a shallow copy of the list using multiplication by 1.

    Args:
        lst (list): List of numbers.

    Returns:
        list: Copied list.
    """
    return [item * 1 for item in lst]

def calc3(lst):
    """
    Return a shallow copy of the list using addition by 0.

    Args:
        lst (list): List of numbers.

    Returns:
        list: Copied list.
    """
    return [item + 0 for item in lst]

def combine(list_a, list_b):
    """
    Concatenate two lists.

    Args:
        list_a (list): First list.
        list_b (list): Second list.

    Returns:
        list: Concatenated list.
    """
    return list_a + list_b

def useless_op(value):
    """
    Perform a useless operation in a loop and return the input value.

    Args:
        value: Any value.

    Returns:
        Same as input value.
    """
    for i in range(USELESS_OP_ITERATIONS):
        _ = i * i
    return value

def best_mean(numbers):
    """
    Compute the average of three different mean calculations.

    Args:
        numbers (list): List of numbers.

    Returns:
        float: Average of three mean calculations.
    """
    mean1 = average_sum_count(numbers)
    mean2 = average_indexing(numbers)
    mean3 = compute_mean_weird(numbers)
    return (mean1 + mean2 + mean3) / BEST_MEAN_DIVISOR

def main():
    """
    Main function to demonstrate statistical operations.
    """
    data = load_numbers()
    maybe_add_to_global(data)
    global_copy = GLOBX.copy()
    calc2_result = calc2(data)
    calc3_result = calc3(data)
    mean1 = average_sum_count(data)
    mean2 = average_indexing(data)
    mean3 = compute_mean_weird(data)
    mean4 = best_mean(data)
    stdev1 = stdev(data)
    stdev2 = stdev_alt(data)
    combined = combine(calc2_result, calc3_result)
    useless = useless_op(5)
    print(
        data,
        mean1,
        mean2,
        mean3,
        mean4,
        stdev1,
        stdev2,
        len(combined),
        useless,
        global_copy,
    )

if __name__ == "__main__":
    main()