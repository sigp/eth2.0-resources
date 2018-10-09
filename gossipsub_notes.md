# GossipSub Generic Notes

Generic notes for GossipSub, cross point between the go implementation and the
specification notes.

General:

|   Item   |                                   Structure                                   | Description                                                    |
|:--------:|:-----------------------------------------------------------------------------:|:---------------------------------------------------------------|
|  `peers` |                                  ``[]peers``                                  | Set/Array of peers                                             |
|  `mesh`  |                            ``Map<topic, []peers>``                            | topic to peer list.                                            |
| `fanout` |                            ``Map<topic, []peers>``.                           | Peers to publish to without topic membership.                  |
|  `seen`  |                              ``Map<message_id>``                              | Tracks last seen messages.                                     |
| `mcache` | ``{ messages: Map<string, message>, history: [][]({ message_id, topics }) }`` | Cache that contains messages for the last few heartbeat ticks. |



## Functions

### Receive

#### AddPeer

Add the peer to the list of peers. Using their protocol ID.

Example Protocol Repo: https://github.com/libp2p/go-libp2p-protocol

```
peers[peer] = protocol
```

#### RemovePeer

Remove the peer from peer list, mesh and fanout.

```
peers.remove(peer)

for each topic in fanout
    fanout[topic].remove(peer)

for each topic in mesh
    mesh[topic].remove(peer)
```

#### IHAVE

Receive an `IHAVE` message from a peer. Check if you've seen the messages, if
not then send an `IWANT` in return to catch up.

```
for each topic in IHAVE
    check if mesh[topic] exists
        false => continue
        true =>
            check through all message_id in seen
                if not seen => construct IWANT(message) and append to list

if list of IWANT > 0
    send IWANT
```


#### IWANT

Receive an `IWANT` message from a peer. Check memcache for the message IDs and
send the response of messages back.

```
messages_to_send = []

for each message_id in IWANT
    if message_id in memcache
        messages_to_send[message_id] = memcache.Get(message_id)

if len(messages_to_send) == 0
    return nothing


send messages_to_send
```

#### GRAFT

Receive a `GRAFT`, add the peer to the mesh of the topic as they have added you
to their mesh. If that topic is not in your mesh, send prune.

```
if mesh[graft.topic] exists
    peers[sender] = blank
else
    prune[graft.topic]
```

#### PRUNE

Handle a prune, removes the mesh link from a peer.

```
if mesh[prune.topic] exists
    mesh[prune.topic].remove(peer)
```

### Sending

#### JOIN

Join a topic by adding to mesh and sending a `GRAFT` message. If it has
``fanout[topic]`` then it selects those peers to add to the mesh.

```
if mesh[topic] already exists
    return

if fanout[topic] has peers
    mesh[topic] = fanout[topic]
    fanout.remove(topic)
    seen.remove(topic)
else
    peers = get_gossip_peers(topic)
    mesh[topic] = peers

for all peers in mesh[topic]
    sendGraft(topic, peer)
```

#### LEAVE

Leaving a topic. Send prune to all peers in the mesh for that topic.

```
if mesh[topic] does not exist
    return

for all peers in mesh[topic]
    sendPrune(topic, peer)

mesh.remove(topic)
```

### Publish

Check the topic, send to *floodsub* peers, then in `mesh`, or use peer list in
`fanout`.

```
send_to = []

for all peers in peers
    if peers[peer].protocol == floodsub
        send_to.append(peer)

if mesh[topic] exists
    for each peer in mesh[topic]
        send_to.append(peer)
else if fanout[topic] exists
    for each peer in fanout[topic]
        send_to.append(peer)
else
    peers = get_gossip_peers(topic)
    for each peer in peers
        send_to.append(peer)

for all peers in send_to
    sendMessage(peer, message)
```

### HeartBeat

The heartbeat is used to maintain the peer connections in the mesh, emit
gossiping and shift the `memcache` to the next epoch window of messages.

```
to_graft = Map<topic, peers>
to_prune = Map<topic, peers>

for topics in mesh
    if number of peers in mesh[topic] < lower_bound
        peers = get_gossip_peers(topic)
        to_graft[topic] = filter_known(peers)

    if number of peers in mesh[topic] > upper_bound
        shuffle_peers_order(mesh[topic])
        for i in 0 to (length(mesh[topic]) - upper_bound)
            to_prune[topic].append(mesh[topic][i])


for each topic in seen
    if current time >  seen[topic].time + specified_fanout_TTL
        fanout.remove(topic)
        seen.remove(topic)


for topics in fanout
    for all peers in topic
        if peer not in topic
            fanout[topic].remove(peer)

    if number of peers in fanout < peer_number_threshold
        peers = get_gossip_peers(topic)
        for each peer in peers
            gossip_to(peer, topic)

for each topic in to_graft
    for each peer in to_graft[topic]
        sendGraft(peer, topic)

for each topic in to_prune
    for each peer in to_prune[topic]
        sendPrune(peer, topic)

mcache.shift_epoch()
```
