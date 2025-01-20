#!/usr/bin/env python3

import argparse

# Define the range of printable characters (ASCII 32 to 126)
START_PRINTABLE = 32
END_PRINTABLE = 126
PRINTABLE_LENGTH = END_PRINTABLE - START_PRINTABLE + 1

def validate_printable(input_string):
    """Ensure all characters in the input are printable ASCII characters."""
    for char in input_string:
        if not (START_PRINTABLE <= ord(char) <= END_PRINTABLE):
            raise ValueError(f"Non-printable character found: {repr(char)}")

#@TODO SAM, YOUR DOCUMENATION HAS " " AT POSITION 0 BUT THIS DOCUMENTATION ASSUMES IT'S AT 1 FIX YOUR INDEXING
def add_strings(message, otp):
    """Encrypt the message by adding the one-time pad, modulo printable characters range."""
    return ''.join(
        chr(((ord(m) - START_PRINTABLE + 1 + ord(o) - START_PRINTABLE  ) % PRINTABLE_LENGTH) + START_PRINTABLE)
        for m, o in zip(message, otp)
    )

def subtract_strings(message, otp):
    """Decrypt the message by subtracting the one-time pad, modulo printable characters range."""
    return ''.join(
        chr(((ord(m) - START_PRINTABLE - (ord(o) - START_PRINTABLE) -1 ) % PRINTABLE_LENGTH) + START_PRINTABLE)
        for m, o in zip(message, otp)
    )

def one_time_pad(input_message, otp, mode="encrypt"):
    # Ensure OTP is not shorter than the message
    if len(otp) < len(input_message):
        raise ValueError("Error: OTP must be at least as long as the message.")

    # Validate input message and OTP (ensure they contain only printable characters)
    validate_printable(input_message)
    validate_printable(otp)

    if mode == "encrypt":
        # Addition for encryption
        encrypted_message = add_strings(input_message, otp)
        return encrypted_message
    elif mode == "decrypt":
        # Subtraction for decryption
        decrypted_message = subtract_strings(input_message, otp)
        return decrypted_message
    else:
        raise ValueError("Invalid mode. Use 'encrypt' or 'decrypt'.")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a message using a one-time pad.")
    
    # Short options added here
    parser.add_argument("-m", "--message", type=str, required=True, help="The plaintext or ciphertext message (ASCII only).")
    parser.add_argument("-o", "--otp", type=str, required=True, help="The one-time pad string (must be same length as or longer than the message).")
    parser.add_argument("-t", "--mode", choices=["encrypt", "decrypt"], required=True, help="Specify whether to encrypt or decrypt the message.")
    
    # Parse command-line arguments
    args = parser.parse_args()

    try:
        result = one_time_pad(args.message, args.otp, args.mode)
        print(f"Result: {result}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()