"""
Unified Multi-language PII Detection Validation Script.

Runs validation for all supported languages (en, ko) and generates
individual reports for each language.

Usage:
    python -m bench.validation              # Run all languages
    python -m bench.validation --lang en    # Run English only
    python -m bench.validation --lang ko    # Run Korean only
    python -m bench.validation --lang en ko # Run specific languages
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import PIIShield
from core.masker import MaskingStrategy


# Language display names
LANGUAGE_NAMES = {
    "en": "English",
    "ko": "Korean",
}

# Available language directories
BENCH_DIR = Path(__file__).parent


def get_available_languages() -> List[str]:
    """Get list of available language directories with dataset.csv."""
    languages = []
    for lang_dir in BENCH_DIR.iterdir():
        if lang_dir.is_dir() and (lang_dir / "dataset.csv").exists():
            languages.append(lang_dir.name)
    return sorted(languages)


def load_dataset(csv_path: Path) -> List[Tuple[str, str]]:
    """
    Load test cases from CSV file.
    
    Args:
        csv_path: Path to the dataset CSV file.
    
    Returns:
        List of (test_case, label) tuples.
    """
    dataset = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_case = row['test_case'].strip()
            label = row['label'].strip()
            dataset.append((test_case, label))
    return dataset


def evaluate_masking(
    shield: PIIShield,
    dataset: List[Tuple[str, str]],
    language: str
) -> Dict:
    """
    Evaluate PII masking performance.
    
    Args:
        shield: PIIShield instance.
        dataset: List of (test_case, expected_masked) tuples.
        language: Language code for detection.
    
    Returns:
        Dictionary with evaluation results.
    """
    total = len(dataset)
    exact_matches = 0
    partial_matches = 0
    results = []
    
    for test_case, expected_masked in dataset:
        result = shield.protect(test_case, language=language, strategy=MaskingStrategy.MASK)
        predicted = result.masked_text
        
        # Check exact match (masked text should match expected)
        is_exact = predicted.strip() == expected_masked.strip()
        if is_exact:
            exact_matches += 1
        
        # Check partial match based on masking pattern
        # Count the number of '*' characters and check if similar
        expected_mask_count = expected_masked.count('*')
        predicted_mask_count = predicted.count('*')
        
        # Partial match if at least one PII was detected and masked
        is_partial = False
        if predicted_mask_count > 0 and len(result.detected_entities) > 0:
            # Allow some tolerance in mask count (within 20%)
            if expected_mask_count > 0:
                diff_ratio = abs(predicted_mask_count - expected_mask_count) / expected_mask_count
                is_partial = diff_ratio <= 0.3  # 30% tolerance
            else:
                is_partial = True
        
        if is_partial and not is_exact:
            partial_matches += 1
        
        results.append({
            'test_case': test_case,
            'expected': expected_masked,
            'predicted': predicted,
            'exact_match': is_exact,
            'entity_count': result.entity_count,
            'expected_masks': expected_mask_count,
            'predicted_masks': predicted_mask_count,
        })
    
    return {
        'language': language,
        'total': total,
        'exact_matches': exact_matches,
        'partial_matches': partial_matches,
        'exact_accuracy': exact_matches / total if total > 0 else 0,
        'partial_accuracy': (exact_matches + partial_matches) / total if total > 0 else 0,
        'results': results,
        'passed': (exact_matches / total if total > 0 else 0) >= 0.8,
    }


def print_report(evaluation: Dict):
    """Print evaluation report to console."""
    lang = evaluation['language']
    lang_name = LANGUAGE_NAMES.get(lang, lang.upper())
    
    print("=" * 70)
    print(f"PII MASKING EVALUATION REPORT - {lang_name.upper()}")
    print("=" * 70)
    
    print(f"\n📊 Summary:")
    print(f"  • Total test cases: {evaluation['total']}")
    print(f"  • Exact matches: {evaluation['exact_matches']}")
    print(f"  • Partial matches: {evaluation['partial_matches']}")
    print(f"  • Exact accuracy: {evaluation['exact_accuracy']:.2%}")
    print(f"  • Partial accuracy: {evaluation['partial_accuracy']:.2%}")
    
    print(f"\n📋 Detailed Results:")
    print("-" * 70)
    
    for i, result in enumerate(evaluation['results'], 1):
        status = "✅" if result['exact_match'] else "❌"
        print(f"\n[{i}] {status}")
        print(f"  Input:    {result['test_case']}")
        print(f"  Expected: {result['expected']}")
        print(f"  Got:      {result['predicted']}")
        if result.get('entity_count'):
            print(f"  Entities: {result['entity_count']}")
        if not result['exact_match']:
            print(f"  Masks:    Expected={result.get('expected_masks', 0)}, Got={result.get('predicted_masks', 0)}")
    
    print("\n" + "=" * 70)


def generate_markdown_report(evaluation: Dict) -> str:
    """Generate a markdown report from evaluation results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lang = evaluation['language']
    lang_name = LANGUAGE_NAMES.get(lang, lang.upper())
    
    lines = [
        f"# PII Masking Validation Report - {lang_name}",
        "",
        f"**Generated:** {timestamp}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total test cases | {evaluation['total']} |",
        f"| Exact matches | {evaluation['exact_matches']} |",
        f"| Partial matches | {evaluation['partial_matches']} |",
        f"| Exact accuracy | {evaluation['exact_accuracy']:.2%} |",
        f"| Partial accuracy | {evaluation['partial_accuracy']:.2%} |",
        "",
        "## Detailed Results",
        "",
    ]
    
    # Separate passed and failed cases
    passed = [r for r in evaluation['results'] if r['exact_match']]
    failed = [r for r in evaluation['results'] if not r['exact_match']]
    
    if failed:
        lines.append("### ❌ Failed Cases")
        lines.append("")
        for i, result in enumerate(failed, 1):
            lines.append(f"#### Case {i}")
            lines.append("")
            lines.append(f"- **Input:** `{result['test_case']}`")
            lines.append(f"- **Expected:** `{result['expected']}`")
            lines.append(f"- **Got:** `{result['predicted']}`")
            if result['entity_count']:
                lines.append(f"- **Entities detected:** {result['entity_count']}")
            lines.append("")
    
    if passed:
        lines.append("### ✅ Passed Cases")
        lines.append("")
        for i, result in enumerate(passed, 1):
            lines.append(f"- `{result['test_case']}` → `{result['predicted']}`")
        lines.append("")
    
    # Status
    status = "PASSED ✅" if evaluation['passed'] else "FAILED ❌"
    lines.append(f"## Overall Status: {status}")
    lines.append("")
    
    return "\n".join(lines)


def save_report(evaluation: Dict) -> Path:
    """Save evaluation report to markdown file."""
    lang = evaluation['language']
    
    # Create report directory
    report_dir = BENCH_DIR / "report"
    report_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{lang}_validation_report.md"
    filepath = report_dir / filename
    
    # Generate and save report
    report_content = generate_markdown_report(evaluation)
    filepath.write_text(report_content, encoding="utf-8")
    
    return filepath


def print_summary_table(evaluations: List[Dict]):
    """Print summary table for all languages."""
    print("\n" + "=" * 70)
    print("📊 UNIFIED VALIDATION SUMMARY")
    print("=" * 70)
    
    print("\n| Language | Cases | Exact | Partial | Accuracy | Status |")
    print("|----------|-------|-------|---------|----------|--------|")
    
    for eval_result in evaluations:
        lang = eval_result['language']
        lang_name = LANGUAGE_NAMES.get(lang, lang.upper())
        status = "✅ PASS" if eval_result['passed'] else "❌ FAIL"
        print(
            f"| {lang_name:<8} | "
            f"{eval_result['total']:>5} | "
            f"{eval_result['exact_matches']:>5} | "
            f"{eval_result['partial_matches']:>7} | "
            f"{eval_result['exact_accuracy']:>7.2%} | "
            f"{status} |"
        )
    
    print("\n" + "=" * 70)
    
    # Overall status
    all_passed = all(e['passed'] for e in evaluations)
    total_cases = sum(e['total'] for e in evaluations)
    total_exact = sum(e['exact_matches'] for e in evaluations)
    overall_accuracy = total_exact / total_cases if total_cases > 0 else 0
    
    print(f"\n📈 Overall Statistics:")
    print(f"  • Total test cases (all languages): {total_cases}")
    print(f"  • Total exact matches: {total_exact}")
    print(f"  • Overall accuracy: {overall_accuracy:.2%}")
    
    if all_passed:
        print("\n🎉 All language validations PASSED!")
    else:
        failed_langs = [LANGUAGE_NAMES.get(e['language'], e['language']) 
                       for e in evaluations if not e['passed']]
        print(f"\n⚠️  Failed languages: {', '.join(failed_langs)}")
    
    return all_passed


def run_validation(
    languages: Optional[List[str]] = None,
    verbose: bool = True
) -> Tuple[List[Dict], bool]:
    """
    Run validation for specified languages.
    
    Args:
        languages: List of language codes to validate. If None, validates all.
        verbose: Whether to print detailed reports.
    
    Returns:
        Tuple of (list of evaluation results, overall pass status)
    """
    available = get_available_languages()
    
    if languages is None:
        languages = available
    else:
        # Validate requested languages exist
        for lang in languages:
            if lang not in available:
                print(f"❌ Error: Language '{lang}' not found. Available: {available}")
                return [], False
    
    print("\n" + "=" * 70)
    print("🔍 PII-SHIELD UNIFIED VALIDATION")
    print("=" * 70)
    print(f"\n📌 Languages to validate: {', '.join(languages)}")
    
    # Initialize PIIShield with all languages using MASK strategy
    shield = PIIShield(
        languages=["en", "ko"],
        default_language="en",
        default_strategy=MaskingStrategy.MASK
    )
    
    evaluations = []
    
    for lang in languages:
        lang_name = LANGUAGE_NAMES.get(lang, lang.upper())
        print(f"\n{'─' * 70}")
        print(f"🌐 Validating {lang_name} ({lang})...")
        print(f"{'─' * 70}")
        
        # Load dataset
        dataset_path = BENCH_DIR / lang / "dataset.csv"
        dataset = load_dataset(dataset_path)
        print(f"📂 Loaded {len(dataset)} test cases from {dataset_path.name}")
        
        # Evaluate
        evaluation = evaluate_masking(shield, dataset, language=lang)
        evaluations.append(evaluation)
        
        # Print detailed report if verbose
        if verbose:
            print_report(evaluation)
        
        # Save report
        report_path = save_report(evaluation)
        print(f"📄 Report saved to: {report_path}")
        
        # Status
        if evaluation['passed']:
            print(f"✅ {lang_name} validation PASSED (accuracy >= 80%)")
        else:
            print(f"❌ {lang_name} validation FAILED (accuracy < 80%)")
    
    # Print summary
    all_passed = print_summary_table(evaluations)
    
    return evaluations, all_passed


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Unified PII Detection Validation for multiple languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m bench.validation              # Validate all languages
    python -m bench.validation --lang en    # Validate English only
    python -m bench.validation --lang ko    # Validate Korean only
    python -m bench.validation --lang en ko # Validate specific languages
    python -m bench.validation --quiet      # Summary only (no detailed results)
        """
    )
    
    parser.add_argument(
        "--lang", "-l",
        nargs="*",
        default=None,
        help="Language code(s) to validate. If not specified, validates all available."
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show summary, skip detailed results."
    )
    
    parser.add_argument(
        "--list", "-L",
        action="store_true",
        help="List available languages and exit."
    )
    
    args = parser.parse_args()
    
    # List available languages
    if args.list:
        available = get_available_languages()
        print("Available languages:")
        for lang in available:
            lang_name = LANGUAGE_NAMES.get(lang, lang.upper())
            print(f"  • {lang} ({lang_name})")
        return 0
    
    # Run validation
    _, all_passed = run_validation(
        languages=args.lang,
        verbose=not args.quiet
    )
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
