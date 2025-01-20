#!/usr/bin/env python3

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import argparse

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
# Ensure lines contain a multiple of 5 characters
MAX_CHARS_PER_LINE -= MAX_CHARS_PER_LINE % 5
MAX_CHARS_PER_LINE -= 5  # Compensate for character count at start of lines
MAX_LINES_PER_PAGE = int(MAX_HEIGHT / LINE_SPACING)

# Function to generate random text from /dev/hwrng and map to printable ASCII
def generate_random_text(file_path="/dev/hwrng", char_limit=5000):
    char_count_needed = MAX_LINES_PER_PAGE * MAX_CHARS_PER_LINE
    if MAX_CHARS_PER_LINE != 100:
        print("Warning: The math will be harder if rows are not exactly 100 characters long.")
    try:
        with open(file_path, "rb") as rng:
            raw_data = rng.read(char_count_needed)
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

    documentation_lines = ["There is a space at the beginning of the printable caracters"]
    documentation_lines += ["encryption is (message+otp)%95, decrpytion is (message-otp)%95"]
    for documentation_line in documentation_lines:
        if y < MARGIN:
            break
        c.drawString(x + ((FONT_SIZE * 0.6)*4), y, documentation_line)  # Start key at the data column
        y -= (LINE_SPACING/LINE_SPACING)* FONT_SIZE

    # Print column numbers every 5 columns, aligned with data
    column_numbers = "".join(f"{i:<5}" for i in range(0, MAX_CHARS_PER_LINE, 5))
    c.drawString(x + ((FONT_SIZE * 0.6) *4), y, column_numbers)  # Shifted to align with data
    y -= (LINE_SPACING/LINE_SPACING)* FONT_SIZE


    # Print ASCII printable characters as a key starting at the same column as data
    printable_key = "".join(chr(i) for i in range(32, 127))
    key_lines = [printable_key[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(printable_key), MAX_CHARS_PER_LINE)]
    for key_line in key_lines:
        if y < MARGIN:
            break
        c.drawString(x + ((FONT_SIZE * 0.6)*4), y, key_line)  # Start key at the data column
        y -= (LINE_SPACING/LINE_SPACING)* FONT_SIZE

    # Draw vertical lines every 5 characters, alternating between solid and dashed
    c.setLineWidth(0.5)
    for i in range(5, MAX_CHARS_PER_LINE + 1, 5):
        x_pos = MARGIN + (i - 1) * (FONT_SIZE * 0.6)  # Adjust to align correctly with character positions
        if (i // 5) % 2 == 0:
            c.line(x_pos, PAGE_HEIGHT - MARGIN - (FONT_SIZE*1), x_pos, MARGIN)
        else:
            c.setDash(3, 2)
            c.line(x_pos, PAGE_HEIGHT - MARGIN - (FONT_SIZE*1), x_pos, MARGIN)
            c.setDash()  # Reset to solid

    # Split text into lines of equal length (multiple of 5 characters)
    lines = [text[i:i + MAX_CHARS_PER_LINE] for i in range(0, len(text), MAX_CHARS_PER_LINE)]
    total_char_count = 0

    for line in lines:
        if y < MARGIN:
            break
        line_with_count = f"{total_char_count:<4}{line}"
        c.drawString(x, y, line_with_count)
        total_char_count += len(line)
        y -= LINE_SPACING

    c.save()

# Main logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a PDF filled with random text from /dev/hwrng.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output PDF file.")
    args = parser.parse_args()

    random_text = generate_random_text()
    if random_text:
        create_pdf(output_path=args.output, text=random_text)
        print(f"PDF created: {args.output}")
    else:
        print("No data to write to PDF.")
