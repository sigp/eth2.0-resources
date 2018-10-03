"""
Can we produce a scenario where:
    validator_count >= min_committee_size * shard_count

    but

    get_new_shuffling does not allocate to each shard in a
    slot?
"""
import sys
sys.path.insert(0, './beacon_chain')

from beacon_chain.state.helpers import (
    get_new_shuffling
)

from beacon_chain.state.validator_record import ValidatorRecord

# Specify the scenario
CYCLE_LENGTH = 64
MIN_COMMITTEE_SIZE = 128
SHARD_COUNT = 1024
VALIDATOR_COUNT = MIN_COMMITTEE_SIZE * SHARD_COUNT

assigned_shards = set()
committee_sizes = []
config = {'cycle_length': CYCLE_LENGTH,
          'min_committee_size': MIN_COMMITTEE_SIZE,
          'shard_count': SHARD_COUNT}
for validator_count in range(VALIDATOR_COUNT, VALIDATOR_COUNT + 1):
    # Setup for the cycle
    seed = b"\x00" * 32
    validators = [ValidatorRecord(start_dynasty=0, end_dynasty=10) for _ in range(validator_count)]
    dynasty = 1
    crosslinking_start_shard = 0

    # Generate the cycle
    cycle = get_new_shuffling(seed, validators, dynasty, crosslinking_start_shard, config)

    # Recurse into the cycle and add each shard id to the
    # accumlative set.
    for slot in cycle:
        for sac in slot:
            assigned_shards.add(sac.shard_id)
            committee_sizes.append(len(sac.committee))

    # Calculate how many shards we think should be possible.
    expected_shard_count = min(
        SHARD_COUNT,
        VALIDATOR_COUNT // MIN_COMMITTEE_SIZE
    )
    # Find how many shards were attested to in total
    assigned_shard_count = len(assigned_shards)
    # Find the average committee size
    average_committee_size = sum(committee_sizes) / len(committee_sizes)

    # If the amount of shards assigned wasn't what we expected,
    # print the little speil.
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
               "get_new_shuffling() produces {} with an average "
               "committee size of {:.2f}.").format(
                   answer, expected_shard_count, assigned_shard_count,
                   average_committee_size))
        print("")
        print(("With {} validators and a minimum committee "
               "size of {}, it should be possible to create a commitee "
               " for each of the {} shards. ").format(
                len(validators), MIN_COMMITTEE_SIZE, SHARD_COUNT))
