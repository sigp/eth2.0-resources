# [WIP] Validator Delegation

The purpose of this documentation is to define the requirements for a function
that forms committees from a list of validators and assigns those committees to
shards and slots.

*Note: this document is produced by Paul Hauner (@paulhauner) and is not
endorsed at all by the Ethereum Foundation. This is my attempt to define the
issue at hand.*

## Terms

The following terms are used in this document:

### Constants

-  `CYCLE_LENGTH`: the amount of slots in a cycle.
-  `SHARD_COUNT` the number of shards in a system.
-  `MIN_COMMITTEE_SIZE`: a constant representing the minimum amount of
   validators required to form a committee.

### Objects/Variables

- `active_validators`: an unique, ordered list of `ValidatorRecords`
  representing all validators capable to participate in validation.
- `ValidatorRecord`: an object representing a single validator. This term is
  used interchangeably with "validator".
- `committee`: A set of indexes pointing to validators in the
  `active_validators` list.
- `shard_id`: the unique identifier of some chain requiring attestation by a
  `committees` in a `slot`.
- `ShardAndCommittee`: an object linking a `committee` to a `shard`.
-  `slot`: a set of `ShardAndCommittee` objects representing the requirement
   for some `committee` to attest to some `shard`.
-  `cycle`: a set of `slots` with length `CYCLE_LENGTH`.

## Function Description

## Inputs

The function should accept the following inputs:

- `validator_indices`: a unique list of integers.
- `shard_indices`: a unique list of `shard_ids`.
- `cycle_length`: the number of `slots` in a `cycle`.
- `min_committee_size`: corresponds to the `CYCLE_LENGTH` value.

_Note: the `validator_indices` and `shard_indices` parameters should be
shuffled prior to this function._

## Outputs

The function should be pure and should return either:

- An error.
- A list.

### Return Type: Error

The program should return an error if:

- The length of `validator_indices` is less than `min_committee_size *
  cycle_length`.
- There is any integer overflow/underflow during computation.

### Return Type: List

Unless an error is encountered, a nested list should be returned where the first
level consists of `CYCLE_LENGTH` lists, where each of those lists contains no
more than `SHARD_COUNT` number of `ShardAndCommittee` objects.

Example:

```
# inputs
validator_indices = [0, 1, 2, 3]
shard_indices = [0, 1, 2]
cycle_length = 2
min_committee_size = 2

# output (list)
[
    [
        {shard_id: 0, committee: [0, 1]},
        {shard_id: 1, committee: [2, 3]},
    ],
    [
        {shard_id: 2, committee: [0, 1]},
        {shard_id: 0, committee: [2, 3]},
    ],
]
```

The object returned by this function must observe the following constraints:

1. Each validator should be assigned to exactly one `committee`.
2. Each `committee` should consist of no less than `min_committee_size` validators.
3. There should not exist more than `len(shard_indices)` committees.
4. Allocation of validators to `committees` should be performed to maximize the
   number of `committees` (without exceeding `len(shard_indices)`).
5. Each `slot` should not feature the same `committee` more than once.
6. Each `slot` should not feature the same `shard_id` more than once.
7. Each `slot` should include as many `committees` as possible, without defying
   any other constraint.
