# About the Challenge

This challenge looks at a simple case for breaking a stream cipher. Plaintext is XORed with a secret pad, but if both plaintext and ciphertext of a message are known, then the pad for that message can be recovered. If pads are reused (they should not be reused!!), then any other messages encrypted with the same pad can be easily recovered.

# Solution

See `solve_script.py`. All four given files are read in, the pad is reconstructed, and then the two unknown ciphertexts are XORed with the pad to recover plaintext.
