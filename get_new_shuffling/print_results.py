from logic.get_new_shuffling import (
    ValidatorRecord,
    set_constants,
    get_new_shuffling
)

VALIDATOR_COUNT = 100
CYCLE_LENGTH = 20
MIN_COMMITTEE_SIZE = 10
SHARD_COUNT = 10

set_constants(CYCLE_LENGTH, MIN_COMMITTEE_SIZE, SHARD_COUNT)

seed = b"\x00" * 32
validators = [ValidatorRecord(0, 10) for _ in range(VALIDATOR_COUNT)]
dynasty = 1
crosslinking_start_shard = 0


cycle = get_new_shuffling(
    seed,
    validators,
    dynasty,
    crosslinking_start_shard)

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
