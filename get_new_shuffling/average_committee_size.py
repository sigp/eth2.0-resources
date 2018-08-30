"""
Run this with:

```
$ python average_committee_size.py
```

It will run get_new_shuffling with a range
of validator_counts and produce the average
committee size across all committees produced
in the range.
"""

from logic.get_new_shuffling import (
    ValidatorRecord,
    get_new_shuffling
)

CYCLE_LENGTH = 20
MIN_COMMITTEE_SIZE = 10
SHARD_COUNT = 10

committee_sizes = []

for validator_count in range(10000, 15000):
    seed = b"\x00" * 32
    validators = [ValidatorRecord(0, 10) for _ in range(validator_count)]
    dynasty = 1
    crosslinking_start_shard = 0

    cycle = get_new_shuffling(
        CYCLE_LENGTH, MIN_COMMITTEE_SIZE, SHARD_COUNT,
        seed, validators, dynasty, crosslinking_start_shard)

    assigned_validators = 0
    for (i, slot) in enumerate(cycle):
        for (i, sac) in enumerate(slot):
            assigned_validators += len(sac.committee)
            committee_sizes.append(len(sac.committee))

    if assigned_validators != validator_count:
        print("validator_count discrepency:")
        print("validator_count={}".format(validator_count))
        print("CYCLE_LENGTH={}".format(CYCLE_LENGTH))
        print("MIN_COMMITTEE_SIZE={}".format(MIN_COMMITTEE_SIZE))
        print("SHARD_COUNT={}".format(SHARD_COUNT))
        assert assigned_validators == validator_count

print("average committee size: {}".format(sum(committee_sizes) /
                                          len(committee_sizes)))
