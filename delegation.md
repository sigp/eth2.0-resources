# [WIP] Validator Delegation

The purpose of this documentation is to define the requirements for a function that forms committees from a list of validators and assigns those committees to shards and slots.

*Note: this document is produced by Paul Hauner (@paulhauner) and is not endorsed at all by the Ethereum Foundation. This is my attempt to define the issue at hand.*

## Terms

### Constants

-  `CYCLE_LENGTH`: the amount of slots in a cycle.
-  `SHARD_COUNT` the number of shards in a system.
-  `MIN_COMMITTEE_SIZE`: a constant representing the minimum amount of validators required to form a committee.

### Objects/Variables

- `active_validators`: an unique, ordered list of `ValidatorRecords` representing all validators capable to participate in validation. 
- `ValidatorRecord`: an object representing a single validator. This term is used interchangably with "validator".
- `committee`: A set of indexes pointing to validators in the `active_validators` list.
- `shard`: some chain requiring attestation by one or more `committees`.
- `ShardAndCommittee`: an object linking a `committee` to a `shard`.
-  `slot`: a set of `ShardAndCommittee` objects representing the requirement for some `committee` to attest to some `shard`.
-  `cycle`: a set of `slots` with length `CYCLE_LENGTH`.

## Context

The Beacon Chain operates in a time scale defined by `cycles` and `slots`. Presently the specification defines the duration of a `slot` to be 8 seconds and `CYCLE_LENTH = 64`, making the length of a `cycle` equal to 512 seconds. The eventual assignment of these values should not be relevant to this document, however we may assume these values for demonstration purposes.

## Problem Description


Given some `active_validator` list, the function should achieve the following:

1. Split `active_validators` into the maximum possible number of `committees`, where each validator is assigned to exactly one `committee` and no `committee` contains less than `MIN_COMMITTEE_SIZE` validators.
2. 

It should return a nested list, where the first level consists of `CYCLE_LENGTH` lists, where each contains no more than `SHARD_COUNT` `ShardAndCommittee` objects. Example:

```
CYCLE_LENGTH = 2
SHARD_COUNT = 3

[
    [
        {shard_id: 0, committee: [0, 1]},
        {shard_id: 1, committee: [2, 3]},
    ],
    [
        {shard_id: 2, committee: [4, 5]},
    ],
]
```

The object returned by this function must observe the following constraints: 

1. Each validator should be assigned to exactly one (1) `committee`.
2. Each `committee` should consist of no less than `MIN_COMMITTEE_SIZE` validators.
3. There should not exist more than `SHARD_COUNT` committees.
4. Allocation of validators to `committees` should be performed to maximize the number of `committees` (whithout exceeeding `SHARD_COUNT`).
3. In each `slot`;
    i. A `committee` should appear no more than once.
    ii. A `shard` should appear no more than once.
    iii. As many `ShardAndCommittees` should be included as possible (without defying any other requirements).




