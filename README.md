# Ethereum 2.0 Resources

This repository contains some resources generated during the development of
[Lighthouse](https://github.com/sigp/lighthouse). They are not guaranteed to be
accurate or useful.

This is not a collection of useful resources from abroad, it is a place to
keep scrappy little scripts used during Sigma Prime Eth 2.0 research.

## Contents

- [shuffling.md](shuffling.md): A walk-through of the shuffling used algorithm in
  the Eth 2.0 spec.
- [WIP] [delegation.md](delegation.md): A document intending to define the
  requirements for a validator delegation function.
- [get_new_shuffling.py](get_new_shuffling/) - a very scrappy setup for
 examining the `get_new_shuffling()` code from the Eth 2.0 spec.
- [gossipsub_notes.md](gossipsub_notes.md): A document simplifying the details
  about gossipsub in [libp2p](https://libp2p.io/).


## Other Useful Resources

Other useful resources generated by the lighthouse team.

- [AttestationSignatures Google Slides](https://docs.google.com/presentation/d/15-LLKmQO6vAUMGxmiHpX1US9bofHpZoy_8Cc8IAc1nI/edit#slide=id.p) a series of slides explaining how to generate the `parent_hashes` array which goes into the block signature message.


