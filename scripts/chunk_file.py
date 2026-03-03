"""
chunk_file.py - Split a large file into manageable chunks at sentence boundaries.

Each output chunk ends at the last period ('.') before the size limit,
so no sentence is split across files.

Usage:
    py scripts/chunk_file.py <input_file> [--max-lines 1500] [--output-dir chunks]
"""

import argparse
import os
import sys


def chunk_file(input_path: str, max_lines: int, output_dir: str) -> list[str]:
    """Split input_path into chunk files of approximately max_lines lines,
    breaking at sentence boundaries.

    Returns list of output file paths created.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        print("Input file is empty.")
        return []

    # Convert line limit to approximate character limit
    all_lines = content.splitlines(keepends=True)
    avg_line_len = len(content) / len(all_lines) if all_lines else 80
    max_chars = int(max_lines * avg_line_len)

    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    ext = os.path.splitext(input_path)[1] or '.txt'

    chunks = []
    start = 0
    chunk_num = 1
    total_len = len(content)

    while start < total_len:
        end_target = start + max_chars

        # If remaining text fits in one chunk, take it all
        if end_target >= total_len:
            chunk_text = content[start:]
        else:
            # Search backward from end_target for the last '.' within this chunk
            break_pos = content.rfind('.', start, end_target + 1)

            if break_pos == -1 or break_pos <= start:
                # No period in range — search forward for the next one
                break_pos = content.find('.', end_target)
                if break_pos == -1:
                    break_pos = total_len - 1  # take the rest

            # Include the period itself, then move past any trailing whitespace
            split_at = break_pos + 1
            # Advance past the newline after the period so next chunk starts clean
            while split_at < total_len and content[split_at] in ('\n', '\r'):
                split_at += 1

            chunk_text = content[start:split_at]

        # Write the chunk
        out_name = f"{base_name}_chunk{chunk_num:03d}{ext}"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chunk_text)

        line_count = chunk_text.count('\n')
        print(f"  {out_name}: {len(chunk_text):>8,} chars, ~{line_count:>5} lines")
        chunks.append(out_path)

        start += len(chunk_text)
        chunk_num += 1

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Split a large file into chunks at sentence boundaries."
    )
    parser.add_argument("input_file", help="Path to the file to split")
    parser.add_argument(
        "--max-lines", type=int, default=1500,
        help="Approximate max lines per chunk (default: 1500)"
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Directory for output chunks (default: <input_dir>/chunks)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: '{args.input_file}' not found.")
        sys.exit(1)

    if args.output_dir is None:
        args.output_dir = os.path.join(
            os.path.dirname(args.input_file) or '.', 'chunks'
        )

    total_lines = sum(1 for _ in open(args.input_file, encoding='utf-8'))
    file_size = os.path.getsize(args.input_file)

    print(f"Splitting: {args.input_file}")
    print(f"File size: {file_size:,} bytes, {total_lines:,} lines")
    print(f"Max lines per chunk: {args.max_lines}")
    print(f"Output dir: {args.output_dir}")
    print()

    chunks = chunk_file(args.input_file, args.max_lines, args.output_dir)

    print(f"\nDone. Created {len(chunks)} chunk(s).")


if __name__ == "__main__":
    main()
