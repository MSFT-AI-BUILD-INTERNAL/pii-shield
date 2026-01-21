"""
PII Shield Evaluation Module

Provides tools and metrics for evaluating PII detection and masking performance.
"""

from eval.evaluator import PIIEvaluator
from eval.metrics import DetectionMetrics
from eval.dataset import EvaluationDataset

__all__ = ["PIIEvaluator", "DetectionMetrics", "EvaluationDataset"]
