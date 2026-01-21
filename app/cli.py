"""
Command Line Interface for PII Shield.

Provides CLI commands for PII detection and masking.
"""

import argparse
import json
import sys
from typing import List, Optional

from core import PIIShield
from core.masker import MaskingStrategy


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pii-shield",
        description="PII Detection and Masking Tool",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect PII in text")
    detect_parser.add_argument("text", help="Text to analyze")
    detect_parser.add_argument(
        "-l", "--language",
        default="en",
        help="Language code (default: en)",
    )
    detect_parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.5,
        help="Confidence threshold (default: 0.5)",
    )
    detect_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    # Mask command
    mask_parser = subparsers.add_parser("mask", help="Mask PII in text")
    mask_parser.add_argument("text", help="Text to mask")
    mask_parser.add_argument(
        "-l", "--language",
        default="en",
        help="Language code (default: en)",
    )
    mask_parser.add_argument(
        "-s", "--strategy",
        choices=["replace", "redact", "hash", "mask"],
        default="replace",
        help="Masking strategy (default: replace)",
    )
    mask_parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.5,
        help="Confidence threshold (default: 0.5)",
    )
    mask_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    # File command
    file_parser = subparsers.add_parser("file", help="Process a file")
    file_parser.add_argument("input", help="Input file path")
    file_parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
    )
    file_parser.add_argument(
        "-l", "--language",
        default="en",
        help="Language code (default: en)",
    )
    file_parser.add_argument(
        "-s", "--strategy",
        choices=["replace", "redact", "hash", "mask"],
        default="replace",
        help="Masking strategy (default: replace)",
    )
    
    return parser.parse_args(args)


def get_strategy(strategy_name: str) -> MaskingStrategy:
    """Convert strategy name to MaskingStrategy enum."""
    strategies = {
        "replace": MaskingStrategy.REPLACE,
        "redact": MaskingStrategy.REDACT,
        "hash": MaskingStrategy.HASH,
        "mask": MaskingStrategy.MASK,
    }
    return strategies.get(strategy_name, MaskingStrategy.REPLACE)


def command_detect(args: argparse.Namespace):
    """Execute detect command."""
    shield = PIIShield()
    
    results = shield.detect_only(
        text=args.text,
        language=args.language,
        score_threshold=args.threshold,
    )
    
    if args.json:
        output = [
            {
                "entity_type": r.entity_type,
                "text": args.text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "score": r.score,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        if not results:
            print("No PII detected.")
        else:
            print(f"Found {len(results)} PII entities:\n")
            for r in results:
                text = args.text[r.start:r.end]
                print(f"  • {r.entity_type}: '{text}' (score: {r.score:.2f})")


def command_mask(args: argparse.Namespace):
    """Execute mask command."""
    shield = PIIShield(default_strategy=get_strategy(args.strategy))
    
    result = shield.protect(
        text=args.text,
        language=args.language,
        score_threshold=args.threshold,
    )
    
    if args.json:
        output = shield.to_dict(result)
        print(json.dumps(output, indent=2))
    else:
        print(f"Original: {result.original_text}")
        print(f"Masked:   {result.masked_text}")
        if result.entity_count:
            print(f"\nEntities found: {result.entity_count}")


def command_file(args: argparse.Namespace):
    """Execute file command."""
    shield = PIIShield(default_strategy=get_strategy(args.strategy))
    
    # Read input file
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Process
    result = shield.protect(text=text, language=args.language)
    
    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.masked_text)
        print(f"Processed file saved to: {args.output}")
        print(f"Entities found: {result.entity_count}")
    else:
        print(result.masked_text)


def main(args: Optional[List[str]] = None):
    """Main entry point."""
    parsed_args = parse_args(args)
    
    if parsed_args.command == "detect":
        command_detect(parsed_args)
    elif parsed_args.command == "mask":
        command_mask(parsed_args)
    elif parsed_args.command == "file":
        command_file(parsed_args)
    else:
        parse_args(["--help"])
        sys.exit(1)


if __name__ == "__main__":
    main()
