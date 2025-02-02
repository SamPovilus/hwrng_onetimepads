#!/usr/bin/env python3

import argparse
import binascii
import hashlib

# Predefined character sets
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
CUSTOM_SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?@#$%^&*()-_=+[]{}|;:'\"<>/\\`~"

def get_supported_chars(charset, extra_chars):
    """Returns the character set based on user selection."""
    if charset == "base64":
        return BASE64_CHARS
    elif charset == "base64-extra":
        return BASE64_CHARS + extra_chars
    else:
        return CUSTOM_SUPPORTED_CHARS

def prepare_char_mapping(supported_chars):
    """Prepares character index mappings for encryption/decryption."""
    return {c: i for i, c in enumerate(supported_chars)}

def validate_printable(input_string, supported_chars):
    """Ensures all characters in the input are within the supported character set."""
    for char in input_string:
        if char not in supported_chars:
            raise ValueError(f"Unsupported character found: {repr(char)}")

def compute_checksum(message, checksum_type):
    """Computes CRC32 or SHA256 checksum."""
    if checksum_type == "crc32":
        return format(binascii.crc32(message.encode()), '08X')  # 8-char hex CRC32
    elif checksum_type == "sha256":
        return hashlib.sha256(message.encode()).hexdigest()[:16]  # First 16 chars of SHA256
    return ""

def add_strings(message, otp, supported_chars, char_index):
    """Encrypts the message by adding the one-time pad using modular arithmetic."""
    char_count = len(supported_chars)
    return ''.join(
        supported_chars[(char_index[m] + char_index[o]) % char_count]
        for m, o in zip(message, otp)
    )

def subtract_strings(message, otp, supported_chars, char_index):
    """Decrypts the message by subtracting the one-time pad using modular arithmetic."""
    char_count = len(supported_chars)
    return ''.join(
        supported_chars[(char_index[m] - char_index[o]) % char_count]
        for m, o in zip(message, otp)
    )

def one_time_pad(input_message, otp, mode, supported_chars, checksum_type):
    """Performs encryption or decryption using the one-time pad algorithm."""
    if mode == "encrypt" and checksum_type:
        checksum = compute_checksum(input_message, checksum_type)
        input_message += checksum

    if len(otp) < len(input_message):
        raise ValueError("Error: OTP must be at least as long as the message.")

    validate_printable(input_message, supported_chars)
    validate_printable(otp, supported_chars)
    char_index = prepare_char_mapping(supported_chars)

    if mode == "encrypt":
        return add_strings(input_message, otp, supported_chars, char_index)
    elif mode == "decrypt":
        decrypted_message = subtract_strings(input_message, otp, supported_chars, char_index)
        if checksum_type:
            checksum_length = 8 if checksum_type == "crc32" else 16
            message_body, extracted_checksum = decrypted_message[:-checksum_length], decrypted_message[-checksum_length:]
            expected_checksum = compute_checksum(message_body, checksum_type)
            if extracted_checksum != expected_checksum:
                raise ValueError("Checksum verification failed. Message may be corrupted.")
            return message_body
        return decrypted_message
    else:
        raise ValueError("Invalid mode. Use 'encrypt' or 'decrypt'.")

def main():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a message using a one-time pad.")
    parser.add_argument("-m", "--message", type=str, required=True, help="The plaintext or ciphertext message.")
    parser.add_argument("-o", "--otp", type=str, required=True, help="The one-time pad string (must be at least as long as the message).")
    parser.add_argument("-t", "--mode", choices=["encrypt", "decrypt"], required=True, help="Specify whether to encrypt or decrypt the message.")
    parser.add_argument("-s", "--charset", choices=["custom", "base64", "base64-extra"], default="custom",
                        help="Choose the character set: 'custom' (default), 'base64', or 'base64-extra'.")
    parser.add_argument("-e", "--extra-chars", type=str, default="", help="Extra characters for 'base64-extra' mode.")
    parser.add_argument("-c", "--checksum", choices=["crc32", "sha256"], help="Append a CRC32 or SHA256 checksum to the message before encryption.")
    args = parser.parse_args()

    supported_chars = get_supported_chars(args.charset, args.extra_chars)
    print(f"Supported charcaters:::{supported_chars}:::")
    try:
        result = one_time_pad(args.message, args.otp, args.mode, supported_chars, args.checksum)
        print(f"Result: {result}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
