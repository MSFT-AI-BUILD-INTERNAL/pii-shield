"""
Korean PII Detection and Masking Example.

This file demonstrates the full pipeline for Korean PII protection:
1. Detection - Detect PII entities in Korean text
2. Masking - Anonymize detected PII
3. Evaluation - Evaluate detection performance
"""

from core import PIIShield, PIIDetector
from core.masker import MaskingStrategy
from core.recognizers.korean import KoreanRecognizers
from eval import PIIEvaluator, EvaluationDataset
from eval.dataset import LabeledSample, LabeledEntity


def setup_korean_detector() -> PIIDetector:
    """
    Set up a PII detector with Korean recognizers.
    
    Returns:
        PIIDetector with Korean recognizers registered.
    """
    detector = PIIDetector(languages=["en", "ko"], default_language="ko")
    
    # Register all Korean recognizers
    for recognizer in KoreanRecognizers.get_all_recognizers():
        detector.analyzer.registry.add_recognizer(recognizer)
    
    return detector


def example_korean_detection():
    """
    Example 1: Detect Korean PII entities.
    """
    print("=" * 70)
    print("Example 1: Korean PII Detection")
    print("=" * 70)
    
    detector = setup_korean_detector()
    
    # Sample Korean texts with various PII
    texts = [
        "안녕하세요, 저는 김철수입니다. 연락처는 010-1234-5678입니다.",
        "홍길동님의 이메일: hong@example.com, 주민번호: 900101-1234567",
        "계좌번호 123-456-789012로 입금해주세요. 담당자 이영희",
        "박민수 고객님, 카드번호 4111-1111-1111-1111 확인 부탁드립니다.",
    ]
    
    for i, text in enumerate(texts, 1):
        print(f"\n[Text {i}] {text}")
        
        results = detector.detect(text, language="ko")
        
        if results:
            print(f"  Detected {len(results)} PII entities:")
            for r in results:
                entity_text = text[r.start:r.end]
                print(f"    • {r.entity_type}: '{entity_text}' (score: {r.score:.2f})")
        else:
            print("  No PII detected.")
    
    print()


def example_korean_masking():
    """
    Example 2: Mask Korean PII with different strategies.
    """
    print("=" * 70)
    print("Example 2: Korean PII Masking")
    print("=" * 70)
    
    # Initialize shield with Korean support
    shield = PIIShield(
        languages=["en", "ko"],
        default_language="ko",
        default_strategy=MaskingStrategy.REPLACE
    )
    
    # Register Korean recognizers
    for recognizer in KoreanRecognizers.get_all_recognizers():
        shield.detector.analyzer.registry.add_recognizer(recognizer)
    
    text = "김철수님 연락처: 010-9876-5432, 이메일: chulsoo.kim@company.co.kr"
    
    print(f"\nOriginal: {text}\n")
    print("Masking with different strategies:")
    
    strategies = [
        (MaskingStrategy.REPLACE, "REPLACE"),
        (MaskingStrategy.REDACT, "REDACT"),
        (MaskingStrategy.MASK, "MASK"),
        (MaskingStrategy.HASH, "HASH"),
    ]
    
    for strategy, name in strategies:
        result = shield.protect(text, language="ko", strategy=strategy)
        print(f"  {name:10} → {result.masked_text}")
    
    print()


def example_korean_full_pipeline():
    """
    Example 3: Full pipeline - Detection, Masking, and JSON output.
    """
    print("=" * 70)
    print("Example 3: Full Korean PII Protection Pipeline")
    print("=" * 70)
    
    import json
    
    # Initialize
    shield = PIIShield(
        languages=["en", "ko"],
        default_language="ko",
        default_strategy=MaskingStrategy.REPLACE
    )
    
    # Register Korean recognizers
    for recognizer in KoreanRecognizers.get_all_recognizers():
        shield.detector.analyzer.registry.add_recognizer(recognizer)
    
    # Sample document
    document = """
    [고객 정보]
    이름: 박지영
    전화번호: 010-5555-1234
    이메일: jiyoung.park@email.com
    주민등록번호: 850315-2345678
    
    [상담 내용]
    박지영 고객님께서 2024년 1월 15일에 문의하셨습니다.
    연락처 010-5555-1234로 회신 부탁드립니다.
    """
    
    print(f"\n[Original Document]{document}")
    
    # Step 1: Detect
    print("\n[Step 1: Detection]")
    entities = shield.detect_only(document, language="ko")
    print(f"  Found {len(entities)} PII entities:")
    for e in entities:
        print(f"    • {e.entity_type}: '{document[e.start:e.end]}' (score: {e.score:.2f})")
    
    # Step 2: Mask
    print("\n[Step 2: Masking]")
    result = shield.protect(document, language="ko")
    print(f"  Masked Document:{result.masked_text}")
    
    # Step 3: Export as JSON
    print("\n[Step 3: JSON Export]")
    json_output = shield.to_dict(result)
    print(json.dumps(json_output, indent=2, ensure_ascii=False))
    
    print()


def example_korean_batch_processing():
    """
    Example 4: Batch processing of multiple Korean texts.
    """
    print("=" * 70)
    print("Example 4: Batch Processing Korean Texts")
    print("=" * 70)
    
    shield = PIIShield(
        languages=["en", "ko"],
        default_language="ko"
    )
    
    # Register Korean recognizers
    for recognizer in KoreanRecognizers.get_all_recognizers():
        shield.detector.analyzer.registry.add_recognizer(recognizer)
    
    # Batch of customer messages
    messages = [
        "이순신입니다. 010-1111-2222로 연락주세요.",
        "강감찬 고객님, 주문이 완료되었습니다.",
        "문의사항은 support@company.kr로 보내주세요.",
        "세종대왕님의 배송지 확인 부탁드립니다.",
    ]
    
    print("\nProcessing batch of messages:\n")
    
    results = shield.protect_batch(messages, language="ko")
    
    for i, (original, result) in enumerate(zip(messages, results), 1):
        print(f"[Message {i}]")
        print(f"  Original: {original}")
        print(f"  Masked:   {result.masked_text}")
        if result.entity_count:
            print(f"  Entities: {result.entity_count}")
        print()


def example_korean_evaluation():
    """
    Example 5: Evaluate Korean PII detection performance.
    """
    print("=" * 70)
    print("Example 5: Korean PII Detection Evaluation")
    print("=" * 70)
    
    # Create evaluation dataset with Korean samples
    samples = [
        LabeledSample(
            text="김철수님의 전화번호는 010-1234-5678입니다.",
            entities=[
                LabeledEntity(0, 3, "KR_NAME", "김철수"),
                LabeledEntity(10, 23, "KR_PHONE_NUMBER", "010-1234-5678"),
            ],
            language="ko",
        ),
        LabeledSample(
            text="이메일 주소: hong@example.com, 담당자 홍길동",
            entities=[
                LabeledEntity(7, 23, "KR_EMAIL", "hong@example.com"),
                LabeledEntity(30, 33, "KR_NAME", "홍길동"),
            ],
            language="ko",
        ),
        LabeledSample(
            text="주민번호 900101-1234567을 확인해주세요.",
            entities=[
                LabeledEntity(4, 18, "KR_SSN", "900101-1234567"),
            ],
            language="ko",
        ),
        LabeledSample(
            text="박민수 고객님, 연락처 010-9999-8888로 회신드리겠습니다.",
            entities=[
                LabeledEntity(0, 3, "KR_NAME", "박민수"),
                LabeledEntity(11, 24, "KR_PHONE_NUMBER", "010-9999-8888"),
            ],
            language="ko",
        ),
    ]
    
    dataset = EvaluationDataset(samples)
    
    # Show dataset statistics
    stats = dataset.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  • Total samples: {stats['total_samples']}")
    print(f"  • Total entities: {stats['total_entities']}")
    print(f"  • Entity types: {list(stats['entity_counts'].keys())}")
    
    # Create shield with Korean recognizers
    shield = PIIShield(languages=["en", "ko"], default_language="ko")
    for recognizer in KoreanRecognizers.get_all_recognizers():
        shield.detector.analyzer.registry.add_recognizer(recognizer)
    
    # Evaluate
    print("\nRunning evaluation...")
    evaluator = PIIEvaluator(shield=shield)
    results = evaluator.evaluate(dataset)
    
    # Print results
    evaluator.print_report(results)


def example_korean_custom_masking():
    """
    Example 6: Custom masking for Korean PII.
    """
    print("=" * 70)
    print("Example 6: Custom Masking for Korean PII")
    print("=" * 70)
    
    from presidio_anonymizer.entities import OperatorConfig
    
    shield = PIIShield(languages=["en", "ko"], default_language="ko")
    
    # Register Korean recognizers
    for recognizer in KoreanRecognizers.get_all_recognizers():
        shield.detector.analyzer.registry.add_recognizer(recognizer)
    
    text = "김철수님 연락처: 010-1234-5678, 이메일: kim@test.com"
    
    print(f"\nOriginal: {text}\n")
    
    # Detect entities
    entities = shield.detect_only(text, language="ko")
    
    # Custom operators for each entity type
    custom_operators = {
        "KR_NAME": OperatorConfig("replace", {"new_value": "[이름]"}),
        "KR_PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[전화번호]"}),
        "KR_EMAIL": OperatorConfig("replace", {"new_value": "[이메일]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[이메일]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[전화번호]"}),
        "PERSON": OperatorConfig("replace", {"new_value": "[이름]"}),
    }
    
    # Apply custom masking
    masked = shield.masker.mask(text, entities, operators=custom_operators)
    
    print(f"Custom Masked: {masked}")
    print()


def main():
    """Run all Korean PII examples."""
    print("\n" + "=" * 70)
    print("🇰🇷 PII Shield - Korean Language Examples")
    print("=" * 70 + "\n")
    
    try:
        example_korean_detection()
        example_korean_masking()
        example_korean_full_pipeline()
        example_korean_batch_processing()
        example_korean_evaluation()
        example_korean_custom_masking()
        
        print("=" * 70)
        print("✅ All Korean examples completed successfully!")
        print("=" * 70)
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMake sure to install required packages:")
        print("  uv sync")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
