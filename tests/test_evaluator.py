"""
Tests for Evaluation module.
"""

import pytest
from eval.metrics import DetectionMetrics, calculate_span_overlap


class TestDetectionMetrics:
    """Tests for DetectionMetrics class."""
    
    def test_precision_calculation(self):
        """Test precision calculation."""
        metrics = DetectionMetrics(
            true_positives=8,
            false_positives=2,
            false_negatives=0,
        )
        assert metrics.precision == 0.8
    
    def test_recall_calculation(self):
        """Test recall calculation."""
        metrics = DetectionMetrics(
            true_positives=8,
            false_positives=0,
            false_negatives=2,
        )
        assert metrics.recall == 0.8
    
    def test_f1_calculation(self):
        """Test F1 score calculation."""
        metrics = DetectionMetrics(
            true_positives=8,
            false_positives=2,
            false_negatives=2,
        )
        # precision = 8/10 = 0.8, recall = 8/10 = 0.8
        # f1 = 2 * 0.8 * 0.8 / (0.8 + 0.8) = 0.8
        assert metrics.f1_score == 0.8
    
    def test_zero_division(self):
        """Test zero division handling."""
        metrics = DetectionMetrics(
            true_positives=0,
            false_positives=0,
            false_negatives=0,
        )
        assert metrics.precision == 0.0
        assert metrics.recall == 0.0
        assert metrics.f1_score == 0.0
    
    def test_metrics_addition(self):
        """Test adding metrics together."""
        metrics1 = DetectionMetrics(true_positives=5, false_positives=2, false_negatives=1)
        metrics2 = DetectionMetrics(true_positives=3, false_positives=1, false_negatives=2)
        
        combined = metrics1 + metrics2
        
        assert combined.true_positives == 8
        assert combined.false_positives == 3
        assert combined.false_negatives == 3


class TestSpanOverlap:
    """Tests for span overlap calculation."""
    
    def test_exact_match(self):
        """Test exact span match."""
        assert calculate_span_overlap((10, 20), (10, 20), threshold=0.5) is True
    
    def test_partial_overlap(self):
        """Test partial span overlap."""
        # Intersection: 15-20 = 5, Union: 10-25 = 15, IoU = 5/15 ≈ 0.33
        assert calculate_span_overlap((10, 20), (15, 25), threshold=0.3) is True
        assert calculate_span_overlap((10, 20), (15, 25), threshold=0.5) is False
    
    def test_no_overlap(self):
        """Test non-overlapping spans."""
        assert calculate_span_overlap((10, 20), (30, 40), threshold=0.1) is False
    
    def test_contained_span(self):
        """Test contained span."""
        # Inner span fully contained in outer
        # Intersection: 12-18 = 6, Union: 10-20 = 10, IoU = 0.6
        assert calculate_span_overlap((10, 20), (12, 18), threshold=0.5) is True


class TestEvaluationDataset:
    """Tests for EvaluationDataset class."""
    
    def test_create_sample_dataset(self):
        """Test creating sample dataset."""
        pass
    
    def test_filter_by_language(self):
        """Test filtering by language."""
        pass
    
    def test_filter_by_entity_type(self):
        """Test filtering by entity type."""
        pass
    
    def test_save_load_json(self):
        """Test saving and loading from JSON."""
        pass
