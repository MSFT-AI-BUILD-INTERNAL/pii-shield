"""
PII Evaluator Module

Provides evaluation functionality for PII detection systems.
"""

from typing import Dict, List, Optional

from core import PIIShield
from eval.dataset import EvaluationDataset, LabeledSample
from eval.metrics import (
    DetectionMetrics,
    EntityMetrics,
    match_predictions_to_ground_truth,
)


class PIIEvaluator:
    """
    Evaluator for PII detection systems.
    
    Compares predictions against ground truth labels
    and computes evaluation metrics.
    
    Example:
        >>> evaluator = PIIEvaluator()
        >>> dataset = EvaluationDataset.from_json("test_data.json")
        >>> results = evaluator.evaluate(dataset)
        >>> print(results["overall"]["f1_score"])
    """
    
    def __init__(
        self,
        shield: Optional[PIIShield] = None,
        overlap_threshold: float = 0.5,
    ):
        """
        Initialize evaluator.
        
        Args:
            shield: PIIShield instance to evaluate. Creates default if None.
            overlap_threshold: Minimum overlap ratio for matching entities.
        """
        self.shield = shield or PIIShield()
        self.overlap_threshold = overlap_threshold
    
    def evaluate(
        self,
        dataset: EvaluationDataset,
        score_threshold: float = 0.5,
    ) -> Dict:
        """
        Evaluate PII detection on a dataset.
        
        Args:
            dataset: EvaluationDataset with labeled samples.
            score_threshold: Minimum confidence score for detections.
        
        Returns:
            Dictionary with evaluation results and metrics.
        """
        entity_metrics = EntityMetrics()
        sample_results = []
        
        for sample in dataset:
            result = self._evaluate_sample(sample, score_threshold)
            sample_results.append(result)
            
            # Update metrics
            for entity_type in result["entity_metrics"]:
                metrics = result["entity_metrics"][entity_type]
                entity_metrics.add_entity_result(
                    entity_type,
                    is_true_positive=False,
                    is_false_positive=False,
                    is_false_negative=False,
                )
                entity_metrics.entity_metrics[entity_type].true_positives += metrics["tp"]
                entity_metrics.entity_metrics[entity_type].false_positives += metrics["fp"]
                entity_metrics.entity_metrics[entity_type].false_negatives += metrics["fn"]
        
        return {
            "overall": entity_metrics.get_overall_metrics().to_dict(),
            "per_entity": entity_metrics.to_dict(),
            "sample_results": sample_results,
            "dataset_statistics": dataset.get_statistics(),
        }
    
    def _evaluate_sample(
        self,
        sample: LabeledSample,
        score_threshold: float,
    ) -> Dict:
        """
        Evaluate a single sample.
        
        Args:
            sample: Labeled sample to evaluate.
            score_threshold: Minimum confidence score.
        
        Returns:
            Dictionary with sample evaluation results.
        """
        # Get predictions
        predictions = self.shield.detect_only(
            text=sample.text,
            language=sample.language,
            score_threshold=score_threshold,
        )
        
        # Convert ground truth to dict format
        ground_truth = [e.to_dict() for e in sample.entities]
        
        # Match predictions to ground truth
        matched, unmatched_pred, unmatched_gt = match_predictions_to_ground_truth(
            predictions, ground_truth, self.overlap_threshold
        )
        
        # Calculate per-entity metrics
        entity_metrics = {}
        
        # True positives
        for pred_idx in matched:
            entity_type = predictions[pred_idx].entity_type
            if entity_type not in entity_metrics:
                entity_metrics[entity_type] = {"tp": 0, "fp": 0, "fn": 0}
            entity_metrics[entity_type]["tp"] += 1
        
        # False positives
        for pred_idx in unmatched_pred:
            entity_type = predictions[pred_idx].entity_type
            if entity_type not in entity_metrics:
                entity_metrics[entity_type] = {"tp": 0, "fp": 0, "fn": 0}
            entity_metrics[entity_type]["fp"] += 1
        
        # False negatives
        for gt_idx in unmatched_gt:
            entity_type = ground_truth[gt_idx]["entity_type"]
            if entity_type not in entity_metrics:
                entity_metrics[entity_type] = {"tp": 0, "fp": 0, "fn": 0}
            entity_metrics[entity_type]["fn"] += 1
        
        return {
            "text": sample.text,
            "language": sample.language,
            "predictions": [
                {
                    "entity_type": p.entity_type,
                    "start": p.start,
                    "end": p.end,
                    "score": p.score,
                }
                for p in predictions
            ],
            "ground_truth": ground_truth,
            "entity_metrics": entity_metrics,
            "matched_count": len(matched),
            "false_positive_count": len(unmatched_pred),
            "false_negative_count": len(unmatched_gt),
        }
    
    def evaluate_single(
        self,
        text: str,
        ground_truth: List[Dict],
        language: str = "en",
        score_threshold: float = 0.5,
    ) -> Dict:
        """
        Evaluate a single text with ground truth.
        
        Args:
            text: Input text to evaluate.
            ground_truth: List of ground truth entities.
            language: Language code.
            score_threshold: Minimum confidence score.
        
        Returns:
            Evaluation results for the single text.
        """
        from eval.dataset import LabeledEntity
        
        entities = [
            LabeledEntity(
                start=gt["start"],
                end=gt["end"],
                entity_type=gt["entity_type"],
                text=text[gt["start"]:gt["end"]],
            )
            for gt in ground_truth
        ]
        
        sample = LabeledSample(
            text=text,
            entities=entities,
            language=language,
        )
        
        return self._evaluate_sample(sample, score_threshold)
    
    def print_report(self, results: Dict):
        """
        Print a formatted evaluation report.
        
        Args:
            results: Results from evaluate() method.
        """
        print("=" * 60)
        print("PII DETECTION EVALUATION REPORT")
        print("=" * 60)
        
        # Overall metrics
        overall = results["overall"]
        print("\n📊 Overall Metrics:")
        print(f"  • Precision: {overall['precision']:.4f}")
        print(f"  • Recall:    {overall['recall']:.4f}")
        print(f"  • F1 Score:  {overall['f1_score']:.4f}")
        print(f"  • TP: {overall['true_positives']}, FP: {overall['false_positives']}, FN: {overall['false_negatives']}")
        
        # Per-entity metrics
        print("\n📋 Per-Entity Metrics:")
        for entity_type, metrics in results["per_entity"].items():
            if entity_type == "overall":
                continue
            print(f"\n  {entity_type}:")
            print(f"    Precision: {metrics['precision']:.4f}")
            print(f"    Recall:    {metrics['recall']:.4f}")
            print(f"    F1 Score:  {metrics['f1_score']:.4f}")
        
        # Dataset statistics
        stats = results["dataset_statistics"]
        print("\n📈 Dataset Statistics:")
        print(f"  • Total samples: {stats['total_samples']}")
        print(f"  • Total entities: {stats['total_entities']}")
        
        print("\n" + "=" * 60)
