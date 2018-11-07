# Validator Architecture

## Document Structure

Firstly, the desired features for a validator are listed, then the minimum
required components are stated. Finally, an argument is made about which
separate binaries should exist and which components these binaries should
contain.

## Desired Features

1. The signing service should be kept completely separate from blockchain
   nodes. No validator private keys should ever be accessed by a component that
has direct access to the Internet (e.g., a P2P stack).
2. The signing service should always be protected by one or more "slash
   protectors". This is a stateful component which stores past attestations and
rejects any message that is slashable.
3. The validator service should have a watchdog that provides alerts to some
   notification service (console logs, email, etc.) if it is unable to
obtain up-to-date blockchain information. This condition might caused by either
node or network faults.
4. A beacon node should be able to outsource shard syncing and shard block production
   to a remote server. This avoids placing an `O(c)` bound upon the beacon
chain node with respect to obtaining canonical shard information.

## Components

- **Beacon Node (Bnode)**: Provides canonical information about the beacon
  chain.
- **Shard Node (Snode)**: Provides canonical information about one or more shard
  chains.
- **Shard Node Manager (SCmgr)**: Manages one or more shard nodes which
  each sync one or more shard chains.
- **Validator Scheduler (Vsched)**: Maintains a clock and triggers validator
  duties like proposing a block or attesting to a shard.
- **Validator Watchdog (Vwatch)**: Provides alerts to some external component
  if the BeaconChain or ShardChain nodes do not provide satisfactory data.
- **Validator Slash Protector (Vslash)**: A stateful component which stores the history of
  a validators votes. Accepts attestations and forwards them to the Validator
Signer if they are not slashable, otherwise discards and reports error.
- **Validator Signer (Vsig)**: Cryptographically signs message that have passed the
  slash protector.

## Binaries

Here components are placed inside binaries (listed as `exe` files, for fun).
Three different layouts are provide to demonstrate how the component layout
might differ between different phases of Serenity deployment. The `v0.0.1` phase is the
focus of this document, future states are listed as considerations.

### v0.0.1: Testnet

The public testnet without sharding (e.g., Q1 2019)

- **BeaconChain.exe**:
	- BC
	- SCMgr
	- SC (junk data generator)

- **Validator.exe**:
	- Vsched
	- Vwatch
	- Vslash
	- Vsig

### v0.1.0: Testnet with Shards

A public testnet with working shards.

- **BeaconChain.exe**:
	- BC
	- SCMgr

- **ShardChain.exe**:
	- SC

- **Validator.exe**:
	- Vsched
	- Vwatch
	- Vslash
	- Vsig

### v1.0.0: Future

Some future solution where staking hardware wallets provide portable state and
additional slash protection.

- **BeaconChain.exe**:
	- BC
	- SCMgr

- **ShardChain.exe**:
	- SC

- **Validator.exe**:
	- Vsched
	- Vwatch
	- Vslash (a)

- **Staking Hardware Wallet**:
	- Vslash (b)
	- Vsig

## Reasoning

It is accepted that a validator operates on some time-based schedule -- it is
required to perform tasks at points in wall-clock time that are not necessarily
triggered by some network event. Therefore, some component needs to exist that
infers the validators duties from some shuffling in the beacon chain
crystallized state and executes upon a timeline of events. Such events might
include:

- Producing a beacon block at some slot
- Producing a shard block at some slot
- Signing or creating an AttestationRecord.
- Requesting that some shard chain be synced and made available.
- Requesting that a beacon node performs AttestationRecord aggregation duties.

The question at hand is whether or not that service should exist in the beacon
chain node or not. Here it is argued that this service should not exist in the
beacon chain node.

It was established that a watchdog service should exist to provide alerts if a
node (or the network) are not operating as expected. Some cases where a user
might want to be notified include:

- A validator is unable to obtain a new crystallized state `n` slots after
  it expected a state transition to occur.
- A validator is unable to obtain new shard block hashes.
- Some RPC call to the beacon chain node fails.
- Many more...

The first part of the argument says that the scheduling service and watchdog
service should exist together; the watchdog service can be less verbose and
more effective if it has knowledge of validator requirements.

The second part of the argument says that a watchdog should not live inside the
beacon node -- the watchdog cannot alarm if the entire node goes down.

Because the watchdog and schedule are more efficient when placed together and
the watchdog cannot exist inside the beacon node, the validator schedule should
not live in the beacon chain node.

### Further Reasoning

#### Separation of Concerns

In the scenario where the Vsched is not in the Bnode, more concerns are shifted out
of the Bnode. In this case the Bnode is not required to know exactly which
validators are connected to it, it simply knows that it has clients that
require arbitrary services like shard syncing and (unsigned) block and
attestation production.

(Note: it will likely be able to deduce which validators are connected to it,
but it will not be _required_ to know it).

#### Minimising Work When Using Redundant Beacon Nodes

Consider a scenario where there are two (2) validators and four (4) beacon
chain nodes for a redundancy factor of 2.

In the scenario where the scheduler is stored inside the beacon node, this
means that `2 * 4 = 8` schedulers exist. In the scenario where the scheduler is
in the validator there exists `1 * 2 = 2` schedulers.
