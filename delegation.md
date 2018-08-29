# [WIP] Validator Delegation

---------

**NOTE: THIS DOCUMENT IS OUTDATED AND INVALID.**

It will be updated soon.

---------

The purpose of this documentation is to define a function that delegates
validators to shards in the Beacon Chain.

*Note: this document is produced by Paul Hauner (@paulhauner) and is not
endorsed at all by the Ethereum Foundation. This does not represent the
canonical method for validator delegation.*

## Terms

The following terms are used in this document:

- `attest`: the process of stating that some shard block is valid.
- `committee`: A list of indices referencing some list of `ValidatorRecords`.
- `committee_count`: The number of committees formed from a single set of
  validators.
- `cycle_length`: the number of slots in a `cycle`.
- `cycle`: a list of `CYCLE_LENGTH` number of `slots`.
- `min_committee_size`: the minimum amount of validators required to form a
   `committee`.
- `shard_id`: the unique identifier of some chain requiring attestation by a
  `committees` in a `slot`.
- `ShardAndCommittee`: an object linking a `committee` to a `shard`.
-  `slot`: a set of `ShardAndCommittee` objects representing the requirement
   for some `committee` to attest to some `shard`.
- `ValidatorRecord`: an object representing a single validator. This term is
  used interchangeably with "validator".

## Required Qualities

The function should have the following qualities:

- Each validator should be given one or more chances to attest each `cycle`.
- Wherever possible, a validator is given only one attestation each
  `cycle`.
- A single `committee` should not be featured in a `cycle` more than once more
  than any other `committee` in that same `cycle`.
- A single `committee` should not appear twice in the same `slot`.

## Function Description

## Inputs

The function should accept the following inputs:

- `validator_indices`: a unique list of integers (assumed to be indices
  of an external list of `ValidatorRecords`).
- `shard_indices`: a unique list of `shard_ids`.
- `next_shard`: an integer representing the first index of the `shard_indices`
  list which will be allocated to a committee.
- `cycle_length`: the number of `slots` in a `cycle`.
- `min_committee_size`: minimum validators per `committee` (see "Terms").

_Note: the `validator_indices` parameters should be
shuffled prior to this function to avoid biases in delegation generated for
some input parameters (e.g., `len(validator_indices) % min_committee_size >
0`)._

_Note: all `validator_indices` are assumed to be "active validators" which
should be assigned to attestation duties._

## Outputs

The function should be pure and should return either:

- An error.
- A (list, integer) tuple.

### Return Type: Error

The program should return an error if:

- The length of `validator_indices` is less than `min_committee_size`.
- `next_shard` is greater than the length of `shard_indices`.
- There is any integer overflow/underflow during computation.

### Return Type: (list, integer) tuple

The the two components of the `(list, integer)` are described individually.

#### List

A two-dimensional list should be returned where the first dimenson represents a
`slot` and the second dimension contains the `ShardAndCommittee` objects
assigned to each `slot`.

Example:

```python
# inputs
validator_indices = [0, 1, 2, 3]
shard_indices = [0, 1, 2]
cycle_length = 2
min_committee_size = 2

# output (list)
[
    [
        ShardAndCommitte(shard_id=0, committee=[0, 1]),
        ShardAndCommitte(shard_id=1, committee=[2, 3]),
    ],
    [
        ShardAndCommitte(shard_id=2, committee=[0, 1]),
        ShardAndCommitte(shard_id=0, committee=[2, 3]),
    ],
]
```

The object returned by this function must observe the following constraints:

1. Each `slot` should be represented in the list (e.g., `len(output) ==
   cycle_length`).
2. Each validator should be assigned to exactly one `committee`.
2. Each `committee` should consist of no less than `min_committee_size` validators.
3. There should not exist more than `len(shard_indices)` number of committees.
4. Allocation of validators to `committees` should be performed to maximize the
   number of `committees` (without exceeding `len(shard_indices)`).
5. A `committee` should be included `n` times in a `cycle`, where
   `k = cycle_length / committee_count` and `k <= n <= k+1`.
6. 



5. Each `slot` should not feature the same `committee` more than once.
6. Each `slot` should not feature the same `shard_id` more than once.
7. Each `slot` should include as many `committees` as possible, without defying
   any other constraint.

#### Integer

An integer should be returned which is set to the `next_shard` which was
incremented each time.

This will allow another run of this function to continue from the same shard as
this run of the function did. TODO: make words better.
