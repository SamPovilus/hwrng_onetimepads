This contains two scripts,

one_time_pad.py: uses the hardware random number generator (on a raspberry pi 5 in my testing) to generate a PDF of a one time pad, the intent is to allow this script to be hooked up to a printer and entierly offline create a one time pad (depending on how paranod you are you should not save the OTP to non-volatile memory on your printer or on your pi)

encrypt_decrypt.py: allows users to type in (or copy depending on paranoia levels) the message, the one time pad,  and encrypt or decrypt automatically, supports automatic hashing via crc32 or sha256 on encryption, and verificatoin of the hash on decrption