#!/usr/bin/env python3

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import argparse

# Constants for PDF formatting
FONT_NAME = "Courier"
FONT_SIZE = 8  # Default, can be set via CLI
LINE_SPACING = 2 * FONT_SIZE  # Double spacing
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * 72  # 3/4 inch in points
MAX_WIDTH = PAGE_WIDTH - 2 * MARGIN
MAX_HEIGHT = PAGE_HEIGHT - 2 * MARGIN

# Define supported characters options
BASE64_RFC4648 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
SUPPORTED_CHARACTERS = BASE64_RFC4648  # Default to base64 table

# Calculate maximum characters per line based on font metrics and width
def update_character_limits():
    global MAX_CHARS_PER_LINE, MAX_LINES_PER_PAGE
    MAX_CHARS_PER_LINE = int(MAX_WIDTH / (FONT_SIZE * 0.6))  # Adjusted for Courier font width
    MAX_CHARS_PER_LINE -= MAX_CHARS_PER_LINE % 5
    MAX_CHARS_PER_LINE -= 5  # Compensate for character count at start of lines
    MAX_LINES_PER_PAGE = int(MAX_HEIGHT / LINE_SPACING)
update_character_limits()

# Function to generate random text from /dev/hwrng and map to supported characters
def generate_random_text(file_path="/dev/hwrng"):
    char_count_needed = MAX_LINES_PER_PAGE * MAX_CHARS_PER_LINE
    try:
        with open(file_path, "rb") as rng:
            raw_data = rng.read(char_count_needed)
        # Map raw bytes into the supported character range
        mapped_chars = [SUPPORTED_CHARACTERS[byte % len(SUPPORTED_CHARACTERS)] for byte in raw_data]
        return "".join(mapped_chars)
    except FileNotFoundError:
        print("/dev/hwrng not found. Ensure you're on a system with hardware RNG.")
        return ""
    except Exception as e:
        print(f"Error reading /dev/hwrng: {e}")
        return ""

# Function to create the PDF
def create_pdf(output_path="output.pdf", text=""):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont(FONT_NAME, FONT_SIZE)
    x = MARGIN
    y = PAGE_HEIGHT - MARGIN  # Start from top margin
    
    # Print documentation line
    documentation_line = f"encryption is (message+otp)%{len(SUPPORTED_CHARACTERS)}, decryption is (message-otp)%{len(SUPPORTED_CHARACTERS)}"
    c.drawString(x + 4 * ((FONT_SIZE * 0.6)), y, documentation_line)
    y -= (LINE_SPACING / LINE_SPACING) * FONT_SIZE

    # Print column numbers every 5 columns
    column_numbers = "".join(f"{i:<5}" for i in range(0, MAX_CHARS_PER_LINE, 5))
    c.drawString(x + 4 * ((FONT_SIZE * 0.6)), y, column_numbers)
    y -= (LINE_SPACING / LINE_SPACING) * FONT_SIZE

    # Print supported characters as a key
    key_lines = [SUPPORTED_CHARACTERS[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(SUPPORTED_CHARACTERS), MAX_CHARS_PER_LINE)]
    for key_line in key_lines:
        if y < MARGIN:
            break
        c.drawString(x + 4 * (FONT_SIZE * 0.6), y, key_line)
        y -= LINE_SPACING / 2

    # Draw vertical lines every 5 characters, alternating between solid and dashed
    c.setLineWidth(0.5)
    for i in range(5, MAX_CHARS_PER_LINE + 1, 5):
        x_pos = MARGIN + (i - 1) * (FONT_SIZE * 0.6)
        if (i // 5) % 2 == 0:
            c.line(x_pos, PAGE_HEIGHT - MARGIN, x_pos, MARGIN)
        else:
            c.setDash(3, 2)
            c.line(x_pos, PAGE_HEIGHT - MARGIN, x_pos, MARGIN)
            c.setDash()

    # Split text into lines of equal length (multiple of 5 characters)
    lines = [text[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(text), MAX_CHARS_PER_LINE)]
    total_char_count = 0

    for line in lines:
        if y < MARGIN:
            break
        line_with_count = f"{total_char_count:<5}{line}"
        c.drawString(x - 1 * (FONT_SIZE * 0.6), y, line_with_count)
        total_char_count += len(line)
        y -= LINE_SPACING * 1.5

    c.save()

# Main logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a PDF filled with random text from /dev/hwrng.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output PDF file.")
    parser.add_argument("-c", "--charset", choices=["base64", "base64+sup"], default="base64", help="Character set to use (default: base64). Use 'base64+sup' for additional symbols.")
    parser.add_argument("-s", "--font-size", type=int, default=8, help="Font size for the output PDF (default: 8).")
    parser.add_argument("-a", "--additional-chars", type=str, default="", help="Additional characters to include in the character set.")
    args = parser.parse_args()

    # Set character set based on argument
    if args.charset == "base64+sup":
        SUPPORTED_CHARACTERS = BASE64_RFC4648 + args.additional_chars
    
    FONT_SIZE = args.font_size
    update_character_limits()

    random_text = generate_random_text()
    if random_text:
        create_pdf(output_path=args.output, text=random_text)
        print(f"PDF created: {args.output}")
    else:
        print("No data to write to PDF.")
