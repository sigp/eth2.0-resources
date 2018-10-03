"""
Run this with:

```
$ python print_results.py
```

It will "pretty" print a cycle produced by
`get_new_shuffling()`
"""

import sys
sys.path.insert(0, './beacon_chain')

from beacon_chain.state.helpers import (
    get_new_shuffling
)

from beacon_chain.state.validator_record import ValidatorRecord

VALIDATOR_COUNT = 100
CYCLE_LENGTH = 20
MIN_COMMITTEE_SIZE = 10
SHARD_COUNT = 10

config = {'cycle_length': CYCLE_LENGTH,
          'min_committee_size': MIN_COMMITTEE_SIZE,
          'shard_count': SHARD_COUNT}
seed = b"\x00" * 32

validators = [ValidatorRecord(start_dynasty=0, end_dynasty=10) \
              for _ in range(VALIDATOR_COUNT)]
dynasty = 1
crosslinking_start_shard = 0


cycle = get_new_shuffling(seed, validators, dynasty, crosslinking_start_shard, config)

print("Configuration:")
print("VALIDATOR_COUNT={}".format(VALIDATOR_COUNT))
print("CYCLE_LENGTH={}".format(CYCLE_LENGTH))
print("MIN_COMMITTEE_SIZE={}".format(MIN_COMMITTEE_SIZE))
print("SHARD_COUNT={}".format(SHARD_COUNT))

print("---------")
for (i, slot) in enumerate(cycle):
    print("Slot {}".format(i))
    for (i, sac) in enumerate(slot):
        print(("    Index {}:"
               "ShardAndCommittee(shard_id={}, committee_len={})")
              .format(i, sac.shard_id, len(sac.committee)))
