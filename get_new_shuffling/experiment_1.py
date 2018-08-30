"""
Can we produce a scenario where:
    validator_count >= min_committee_size * shard_count

    but

    get_new_shuffling does not allocate to each shard in a
    slot?
"""

from logic.get_new_shuffling import (
    ValidatorRecord,
    get_new_shuffling
)

# Specify the scenario
CYCLE_LENGTH = 64
MIN_COMMITTEE_SIZE = 128
SHARD_COUNT = 1024
VALIDATOR_COUNT = MIN_COMMITTEE_SIZE * SHARD_COUNT

assigned_shards = set()
for validator_count in range(VALIDATOR_COUNT, VALIDATOR_COUNT + 1):
    seed = b"\x00" * 32
    validators = [ValidatorRecord(0, 10) for _ in range(validator_count)]
    dynasty = 1
    crosslinking_start_shard = 0

    cycle = get_new_shuffling(
        CYCLE_LENGTH, MIN_COMMITTEE_SIZE, SHARD_COUNT,
        seed, validators, dynasty, crosslinking_start_shard)

    for (i, slot) in enumerate(cycle):
        for (i, sac) in enumerate(slot):
            assigned_shards.add(sac.shard_id)

    expected_shard_count = min(SHARD_COUNT, VALIDATOR_COUNT // MIN_COMMITTEE_SIZE)
    assigned_shard_count = len(assigned_shards)

    if expected_shard_count != assigned_shard_count:
        print("Scenario:")
        print("")
        print("CYCLE_LENGTH={}".format(CYCLE_LENGTH))
        print("MIN_COMMITTEE_SIZE={}".format(MIN_COMMITTEE_SIZE))
        print("SHARD_COUNT={}".format(SHARD_COUNT))
        print("VALIDATOR_COUNT={}".format(len(validators)))
        print("")

        if VALIDATOR_COUNT >= (MIN_COMMITTEE_SIZE * SHARD_COUNT):
            answer = "possible"
        else:
            answer = "impossible"

        print(("It's {} to make {} shard attestations, but "
               "get_new_shuffling produces {}.").format(
            answer, expected_shard_count, assigned_shard_count))
        print("")
        print(("With {} validators and a minimum committee "
               "size of {}, it should be possible to create a commitee "
               " for each of the {} shards. ").format(
                len(validators), MIN_COMMITTEE_SIZE, SHARD_COUNT))
