"""
Evaluation Metrics for PII Detection.

Provides precision, recall, F1-score and other metrics
for evaluating PII detection performance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from presidio_analyzer import RecognizerResult


@dataclass
class DetectionMetrics:
    """
    Metrics for PII detection evaluation.
    
    Attributes:
        true_positives: Correctly detected PII entities.
        false_positives: Incorrectly detected entities (not actual PII).
        false_negatives: Missed PII entities.
        precision: TP / (TP + FP)
        recall: TP / (TP + FN)
        f1_score: Harmonic mean of precision and recall.
    """
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    
    @property
    def precision(self) -> float:
        """Calculate precision: TP / (TP + FP)"""
        total = self.true_positives + self.false_positives
        return self.true_positives / total if total > 0 else 0.0
    
    @property
    def recall(self) -> float:
        """Calculate recall: TP / (TP + FN)"""
        total = self.true_positives + self.false_negatives
        return self.true_positives / total if total > 0 else 0.0
    
    @property
    def f1_score(self) -> float:
        """Calculate F1 score: 2 * (precision * recall) / (precision + recall)"""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy: TP / (TP + FP + FN)"""
        total = self.true_positives + self.false_positives + self.false_negatives
        return self.true_positives / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "accuracy": self.accuracy,
        }
    
    def __add__(self, other: "DetectionMetrics") -> "DetectionMetrics":
        """Add two metrics together."""
        return DetectionMetrics(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
        )


@dataclass
class EntityMetrics:
    """
    Per-entity type metrics.
    
    Tracks detection performance for each PII entity type separately.
    """
    entity_metrics: Dict[str, DetectionMetrics] = field(default_factory=dict)
    
    def add_entity_result(
        self,
        entity_type: str,
        is_true_positive: bool = False,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
    ):
        """Add a single detection result for an entity type."""
        if entity_type not in self.entity_metrics:
            self.entity_metrics[entity_type] = DetectionMetrics()
        
        metrics = self.entity_metrics[entity_type]
        if is_true_positive:
            metrics.true_positives += 1
        if is_false_positive:
            metrics.false_positives += 1
        if is_false_negative:
            metrics.false_negatives += 1
    
    def get_overall_metrics(self) -> DetectionMetrics:
        """Get aggregated metrics across all entity types."""
        overall = DetectionMetrics()
        for metrics in self.entity_metrics.values():
            overall = overall + metrics
        return overall
    
    def get_entity_metrics(self, entity_type: str) -> Optional[DetectionMetrics]:
        """Get metrics for a specific entity type."""
        return self.entity_metrics.get(entity_type)
    
    def to_dict(self) -> Dict[str, Dict[str, float]]:
        """Convert all metrics to dictionary."""
        result = {
            entity_type: metrics.to_dict()
            for entity_type, metrics in self.entity_metrics.items()
        }
        result["overall"] = self.get_overall_metrics().to_dict()
        return result


def calculate_span_overlap(
    predicted: Tuple[int, int],
    ground_truth: Tuple[int, int],
    threshold: float = 0.5,
) -> bool:
    """
    Calculate if two spans overlap above a threshold.
    
    Args:
        predicted: (start, end) of predicted span.
        ground_truth: (start, end) of ground truth span.
        threshold: Minimum IoU (Intersection over Union) threshold.
    
    Returns:
        True if overlap ratio >= threshold.
    """
    pred_start, pred_end = predicted
    gt_start, gt_end = ground_truth
    
    # Calculate intersection
    intersection_start = max(pred_start, gt_start)
    intersection_end = min(pred_end, gt_end)
    intersection = max(0, intersection_end - intersection_start)
    
    # Calculate union
    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    
    # IoU (Intersection over Union)
    iou = intersection / union if union > 0 else 0
    
    return iou >= threshold


def match_predictions_to_ground_truth(
    predictions: List[RecognizerResult],
    ground_truth: List[Dict],
    overlap_threshold: float = 0.5,
) -> Tuple[Set[int], Set[int], Set[int]]:
    """
    Match predicted entities to ground truth entities.
    
    Args:
        predictions: List of predicted RecognizerResult.
        ground_truth: List of ground truth dicts with keys: start, end, entity_type.
        overlap_threshold: Minimum overlap ratio for a match.
    
    Returns:
        Tuple of (matched_pred_indices, unmatched_pred_indices, unmatched_gt_indices).
    """
    matched_predictions = set()
    matched_ground_truth = set()
    
    for pred_idx, pred in enumerate(predictions):
        pred_span = (pred.start, pred.end)
        
        for gt_idx, gt in enumerate(ground_truth):
            if gt_idx in matched_ground_truth:
                continue
            
            gt_span = (gt["start"], gt["end"])
            
            # Check entity type match and span overlap
            if (pred.entity_type == gt["entity_type"] and
                calculate_span_overlap(pred_span, gt_span, overlap_threshold)):
                matched_predictions.add(pred_idx)
                matched_ground_truth.add(gt_idx)
                break
    
    unmatched_predictions = set(range(len(predictions))) - matched_predictions
    unmatched_ground_truth = set(range(len(ground_truth))) - matched_ground_truth
    
    return matched_predictions, unmatched_predictions, unmatched_ground_truth
