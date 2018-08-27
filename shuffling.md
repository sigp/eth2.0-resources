# Validator Shuffling

Paul Hauner | @paulhauner | [Sigma Prime](https://sigmaprime.io/)

This document is a walk-through of the shuffling algorithm used to "randomize"
the distribution of validators to blocks and shards in the
[Ethereum 2.0 spec](https://notes.ethereum.org/SCIg8AH5SA-O4C1G1LYZHQ?view)
(now referred to as "the spec").

This article does not fully describe how validators are assigned to block
production and shard attestation. Instead, it describes the shuffling primitive
used to ensure validators do not repeatedly get assigned to the same task.
First validators are shuffled, then they are assigned to tasks.

The intention of this document is to give enough background information for
someone with a programming background to understand, in-depth, the
`get_shuffling()` method published in the spec.

## Background

Necessary to understanding this function are two background items:

- A basic list shuffling algorithm.
- The concept of modulo-bias.

Lets cover them.

### Durstenfeld-Knuth-Fisher-Yates Shuffle

This is a method of shuffling a list "introduced" by Richard Durstenfeld in
1964 and "popularized" by Donald E. Knuth in _The Art of Computer Programming_.
Apparently it's similar to work done by Ronald Fisher and Frank Yates in 1938.
More @ [wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle).

History aside, it looks like this:

```
-- To shuffle an array a of n elements (indices 0..n-1):
for i from 0 to n−2 do
     j ← random integer such that i ≤ j < n
     exchange a[i] and a[j]
```

It seems that this is the primitive for the shuffling algorithm used in the
spec, so lets assume this is what we're going to use. Seems optimal.

Let's just call it the "Fisher-Yates" shuffle from here.

### Modulo-Bias

For background, modulo bias is introduced when using modulo to "fit" an random
integer of a large range into a smaller range when the smaller range is not a
clean multiple of the larger range. In other words, `large_range % small_range
> 0`.

As an example, consider a function `rng()` which generates an integer between
`0..3` (inclusive) and an application which requires a integer of `0..2`
(inclusive). A developer might simply call `rng() % 3`, however this introduces
a bias because both `0 % 3 = 0` and `3 % 3 = 0`. This skews the post-modulo
result in favor of `0`. This is a Bad Thing™.

A method to fix this is to simply filter out all "biased" results, that is any
results which are greater than `RAND_MAX - (RAND_MAX % n)`, where `RAND_MAX`
defines the upper bound of an rng (`0..RAND_MAX`) and `n` is the upper bound of
the desired range (`0..n`) and `RAND_MAX > n`. Lets apply this knowledge to the
previous example and define the following function:

```python
def filtered_rng(n):
    while True:
            x = rng()
            if x < rand_max - rand_max % n:
                break
    return x
```

The developer can now call `filtered_rng(3)`. This will give them results
without a modulo bias. The downside is that it's now possible for the function
to run indeterminately, because it's relying on `rng` not to generate certain
numbers. We can just assume that this won't actually run forever, instead it'll
just slow us down a every now and then.

## The code

Now we examine an implementation of a Fisher-Yates shuffle which uses a
psuedo-random RNG without modulo-bias.

Here I present an implementation which is is different to that which is in the
spec, however their output is the same.

I re-wrote the `shuffle()` function from the spec because I believe it is
easier to understand this way. I broke it into two components; a Fisher-Yates
shuffle and an RNG. The trade-off is that my code runs much slower in Python.
It should be trivial to understand one if you understand the other.


In this section, we will examine the entirety of my implementation; two functions and a class:
- `ShuffleRNG`: a class which serves as a stateful pseudo-random RNG (PRNG) based on blake2 hashes.
- `durstenfeld_shuffle()` a method which performs an in-place Fisher-Yates shuffle.
- `shuffle()`: a top-level method which instantiates a `ShuffleRNG` then performs a `durstenfeld_shuffle`.

We will show them in reverse-order, each with comments.

### Top-level method

```python
def shuffle(lst, seed):
    rng = ShuffleRng(seed)
    o = [x for x in lst]
    durstenfeld_shuffle(o, rng.rand_range)
    return o
```

Here we accept a list for shuffling (`lst`) and a byte-array (`seed`) as an
intial source of entropy to seed the PRNG.

This function is deterministic; it will always return the same result given the
same list and seed.

### Shuffling method

```python
def durstenfeld_shuffle(lst, rand_range):
    for i in range(len(lst) - 1):
        j = rand_range(i, len(lst))
        lst[i], lst[j] = lst[j], lst[i]
```

This is the Durstenfeld-Knuth-Fisher-Yates shuffle described earlier.



It takes a list for shuffling (`lst`) and a function (`rand_range`) which, when
called, generates a random integer in some given range.

For example, we expect `rand_range(4)` to return a random number `n` where `0
<= n <= 3`.

### PRNG class

```python
class ShuffleRng:
    def __init__(self, seed):
        self.seed = blake(seed)
        self.seed_idx = 0

    def rehash_seed(self):
        self.seed = blake(self.seed)
        self.seed_idx = 0

    def rand(self):
        num_bytes = int(NUM_RAND_BITS / 8)
        first = self.seed_idx
        last = self.seed_idx + num_bytes
        if last >= len(self.seed):
            self.rehash_seed()
            return self.rand()
        x = int.from_bytes(self.seed[first:last], 'big')
        self.seed_idx += num_bytes
        return x

    def rand_range(self, a, b):
        rand_max = 2**NUM_RAND_BITS
        n = b - a
        x = 0
        while True:
            x = self.rand()
            if x < rand_max - rand_max % n:
                break
        return (x % n) + a
```

The class is intitialised (see `__init__()`) with a byte-array (`seed`).
Entropy is harvested by hashing `seed` as many times as necessary. In the spirit
of PRNGs, this class will always generate the same sequence of numbers if given
the same `seed`.

The `rehash_seed()` replaces the present `seed` with the blake2s hash of
itself. Whenever all the bits have been read from the current `seed`, it is
hashed again to get "fresh" bits.

`rand()` reads 24 bits (3 bytes) of the `seed` and returns the result as an
integer. The stream of bits is read as a big-endian unsigned integer. It keeps
track of which bits it has read and rehashes the seed when required.

`rand_range()` calls `rand()` and then restricts the result to be within range
`a` and `b`. There is a `while` loop used to filter results which lead to
modulo-bias (as explained earlier).

Note: This example used `blake2s` as the hashing algorithm, but any crypto
hashing algorithm will do.

## Summary

Now we can see that it is possible to do a deterministic psuedo-random shuffle
given some arbitrary data as an input.

Deterministic is required because all Beacon Chain clients must be able to
perform the shuffle and get the same results.

Of course, this method is only as random as the bits you supply it (and the
underlying hash function). The design of the Beacon Chain RNG is not yet
finialized, but whatever it chooses can almost-certainly be supplied as an
input to this method.

Given this information, it should be easy to understand the `get_shuffling()`
method used in the spec.

## Extra Resources

This document is the result of my research on [issue #57](https://github.com/ethereum/beacon_chain/issues/57) on the github.com/ethereum/beacon_chain repo. 

During this process, I made a [shuffling_sandbox](https://github.com/sigp/shuffling_sandbox) repository which allows benchmarking and output comparisons of some shuffling implementations. 

There's also a fuzzer to try and find differences between my shuffling
implementation (disclosed here) and the implementation in the spec.
