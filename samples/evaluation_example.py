"""
Evaluation Example for PII Shield.

Demonstrates how to evaluate PII detection performance using the eval module.
"""

from core import PIIShield
from eval import PIIEvaluator, EvaluationDataset
from eval.dataset import LabeledSample, LabeledEntity


def create_test_dataset() -> EvaluationDataset:
    """
    Create a test dataset for evaluation.
    
    Returns:
        EvaluationDataset with test samples.
    """
    samples = [
        LabeledSample(
            text="Contact John Doe at john.doe@example.com or call 555-123-4567.",
            entities=[
                LabeledEntity(8, 16, "PERSON", "John Doe"),
                LabeledEntity(20, 40, "EMAIL_ADDRESS", "john.doe@example.com"),
                LabeledEntity(49, 61, "PHONE_NUMBER", "555-123-4567"),
            ],
            language="en",
        ),
        LabeledSample(
            text="My email is alice@company.org and my phone is 555-987-6543.",
            entities=[
                LabeledEntity(12, 29, "EMAIL_ADDRESS", "alice@company.org"),
                LabeledEntity(47, 59, "PHONE_NUMBER", "555-987-6543"),
            ],
            language="en",
        ),
        LabeledSample(
            text="Send payment to credit card 4111-1111-1111-1111.",
            entities=[
                LabeledEntity(27, 46, "CREDIT_CARD", "4111-1111-1111-1111"),
            ],
            language="en",
        ),
        LabeledSample(
            text="Visit our website at https://example.com for more info.",
            entities=[
                LabeledEntity(21, 40, "URL", "https://example.com"),
            ],
            language="en",
        ),
        LabeledSample(
            text="The meeting is scheduled for January 15, 2024 at 10:00 AM.",
            entities=[
                LabeledEntity(29, 56, "DATE_TIME", "January 15, 2024 at 10:00 AM"),
            ],
            language="en",
        ),
    ]
    
    return EvaluationDataset(samples)


def example_basic_evaluation():
    """
    Example: Basic evaluation workflow.
    """
    print("=" * 60)
    print("Basic Evaluation Example")
    print("=" * 60)
    
    # Create test dataset
    dataset = create_test_dataset()
    
    # Show dataset statistics
    stats = dataset.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  • Total samples: {stats['total_samples']}")
    print(f"  • Total entities: {stats['total_entities']}")
    print(f"  • Entity types: {list(stats['entity_counts'].keys())}")
    
    # Create evaluator
    evaluator = PIIEvaluator()
    
    # Run evaluation
    print("\nRunning evaluation...")
    results = evaluator.evaluate(dataset)
    
    # Print report
    evaluator.print_report(results)


def example_single_text_evaluation():
    """
    Example: Evaluate a single text with ground truth.
    """
    print("\n" + "=" * 60)
    print("Single Text Evaluation Example")
    print("=" * 60)
    
    evaluator = PIIEvaluator()
    
    # Define text and ground truth
    text = "Contact support@example.com for assistance."
    ground_truth = [
        {"start": 8, "end": 27, "entity_type": "EMAIL_ADDRESS"},
    ]
    
    # Evaluate
    result = evaluator.evaluate_single(text, ground_truth)
    
    print(f"\nText: {text}")
    print(f"\nGround Truth:")
    for gt in ground_truth:
        print(f"  • {gt['entity_type']}: {text[gt['start']:gt['end']]}")
    
    print(f"\nPredictions:")
    for pred in result["predictions"]:
        print(f"  • {pred['entity_type']}: {text[pred['start']:pred['end']]} (score: {pred['score']:.2f})")
    
    print(f"\nResults:")
    print(f"  • True Positives: {result['matched_count']}")
    print(f"  • False Positives: {result['false_positive_count']}")
    print(f"  • False Negatives: {result['false_negative_count']}")


def example_save_load_dataset():
    """
    Example: Save and load evaluation dataset.
    """
    print("\n" + "=" * 60)
    print("Save/Load Dataset Example")
    print("=" * 60)
    
    # Create dataset
    dataset = create_test_dataset()
    
    # Save to JSON
    output_path = "/tmp/eval_dataset.json"
    dataset.to_json(output_path)
    print(f"\nDataset saved to: {output_path}")
    
    # Load from JSON
    loaded_dataset = EvaluationDataset.from_json(output_path)
    print(f"Loaded {len(loaded_dataset)} samples from file")
    
    # Verify
    print("\nFirst sample:")
    sample = loaded_dataset[0]
    print(f"  Text: {sample.text[:50]}...")
    print(f"  Entities: {[e.entity_type for e in sample.entities]}")


def example_filter_dataset():
    """
    Example: Filter dataset by language or entity type.
    """
    print("\n" + "=" * 60)
    print("Filter Dataset Example")
    print("=" * 60)
    
    # Create sample dataset
    dataset = EvaluationDataset.create_sample_dataset()
    
    print(f"\nFull dataset: {len(dataset)} samples")
    
    # Filter by language
    en_dataset = dataset.filter_by_language("en")
    print(f"English only: {len(en_dataset)} samples")
    
    ko_dataset = dataset.filter_by_language("ko")
    print(f"Korean only: {len(ko_dataset)} samples")
    
    # Filter by entity type
    email_dataset = dataset.filter_by_entity_type("EMAIL_ADDRESS")
    print(f"With EMAIL_ADDRESS: {len(email_dataset)} samples")


def main():
    """Run all evaluation examples."""
    print("\n📊 PII Shield - Evaluation Examples\n")
    
    try:
        example_basic_evaluation()
        example_single_text_evaluation()
        example_save_load_dataset()
        example_filter_dataset()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure to install required packages first.")


if __name__ == "__main__":
    main()
