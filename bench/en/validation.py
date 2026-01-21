"""
English PII Detection Validation Script.

Loads dataset.csv and evaluates PII detection performance.
"""

import csv
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core import PIIShield
from core.masker import MaskingStrategy


def load_dataset(csv_path: str) -> List[Tuple[str, str]]:
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
    language: str = "en"
) -> Dict:
    """
    Evaluate PII masking performance.
    
    Args:
        shield: PIIShield instance.
        dataset: List of (test_case, expected_label) tuples.
        language: Language code for detection.
    
    Returns:
        Dictionary with evaluation results.
    """
    total = len(dataset)
    exact_matches = 0
    partial_matches = 0
    results = []
    
    for test_case, expected_label in dataset:
        result = shield.protect(test_case, language=language)
        predicted = result.masked_text
        
        # Check exact match
        is_exact = predicted.strip() == expected_label.strip()
        if is_exact:
            exact_matches += 1
        
        # Check partial match (all expected entity types are present)
        expected_entities = set()
        for token in expected_label.split():
            if token.startswith('<') and token.endswith('>'):
                expected_entities.add(token)
        
        predicted_entities = set()
        for token in predicted.split():
            if token.startswith('<') and token.endswith('>'):
                predicted_entities.add(token)
        
        is_partial = expected_entities.issubset(predicted_entities) or predicted_entities.issubset(expected_entities)
        if is_partial and not is_exact:
            partial_matches += 1
        
        results.append({
            'test_case': test_case,
            'expected': expected_label,
            'predicted': predicted,
            'exact_match': is_exact,
            'entity_count': result.entity_count,
        })
    
    return {
        'total': total,
        'exact_matches': exact_matches,
        'partial_matches': partial_matches,
        'exact_accuracy': exact_matches / total if total > 0 else 0,
        'partial_accuracy': (exact_matches + partial_matches) / total if total > 0 else 0,
        'results': results,
    }


def print_report(evaluation: Dict):
    """Print evaluation report."""
    print("=" * 70)
    print("PII MASKING EVALUATION REPORT - ENGLISH")
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
        if result['entity_count']:
            print(f"  Entities: {result['entity_count']}")
    
    print("\n" + "=" * 70)


def main():
    """Run validation."""
    print("\n🔍 Loading English PII Dataset...\n")
    
    # Load dataset
    csv_path = Path(__file__).parent / "dataset.csv"
    dataset = load_dataset(str(csv_path))
    print(f"Loaded {len(dataset)} test cases from {csv_path}\n")
    
    # Initialize shield
    shield = PIIShield(
        languages=["en"],
        default_language="en",
        default_strategy=MaskingStrategy.REPLACE
    )
    
    # Evaluate
    print("Running evaluation...")
    evaluation = evaluate_masking(shield, dataset, language="en")
    
    # Print report
    print_report(evaluation)
    
    # Return exit code based on accuracy
    if evaluation['exact_accuracy'] >= 0.8:
        print("✅ Validation PASSED (accuracy >= 80%)")
        return 0
    else:
        print("❌ Validation FAILED (accuracy < 80%)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
