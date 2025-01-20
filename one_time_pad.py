#!/usr/bin/env python3

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import argparse

# pi hwrng http://scruss.com/blog/2013/06/07/well-that-was-unexpected-the-raspberry-pis-hardware-random-number-generator/

# Constants for PDF formatting
FONT_NAME = "Courier"
FONT_SIZE = 8
LINE_SPACING = 2 * FONT_SIZE  # Double spacing
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.75 * 72  # 3/4 inch in points
MAX_WIDTH = PAGE_WIDTH - 2 * MARGIN
MAX_HEIGHT = PAGE_HEIGHT - 2 * MARGIN

# Calculate maximum characters per line based on font metrics and width
MAX_CHARS_PER_LINE = int(MAX_WIDTH / (FONT_SIZE * 0.6))  # Adjusted for Courier font width
MAX_LINES_PER_PAGE = int(MAX_HEIGHT / LINE_SPACING)

# Function to generate random text from /dev/hwrng and map to printable ASCII
def generate_random_text(file_path="/dev/hwrng", char_limit=5000):
    try:
        with open(file_path, "rb") as rng:
            raw_data = rng.read(char_limit)
        # Map raw bytes into the printable ASCII range (32-126)
        mapped_chars = [chr(32 + (byte % 95)) for byte in raw_data]
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

    # Print ASCII printable characters as a key at the top
    printable_key = "".join(chr(i) for i in range(32, 127))
    key_lines = [''.join(f"{n//10 if n % 10 == 0 else n % 10}" for n in range(1, 96))]
    key_lines += [printable_key[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(printable_key), MAX_CHARS_PER_LINE)]
    for key_line in key_lines:
        if y < MARGIN:
            break
        c.drawString(x, y, key_line)
        y -= (LINE_SPACING/LINE_SPACING) * FONT_SIZE

    # Split text into lines of equal length
    lines = [text[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(text), MAX_CHARS_PER_LINE)]

    for line in lines[:-1]:
        if y < MARGIN:
            break
        c.drawString(x, y, line)
        y -= LINE_SPACING

    # Render the last line in bold
    if y >= MARGIN and lines:
        c.setFont(FONT_NAME, FONT_SIZE + 2)  # Slightly larger font for emphasis
        c.drawString(x, y, lines[-1])
        y -= LINE_SPACING

    c.save()

# Main logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a pdf of a one time pad")
    parser.add_argument("-o", "--outfile", type=str, required=True, help="Output file name")
    args = parser.parse_args()

    random_text = generate_random_text()
    if random_text:
        create_pdf(output_path=args.outfile, text=random_text)
        print("PDF created: " + args.outfile)
    else:
        print("No data to write to PDF.")
