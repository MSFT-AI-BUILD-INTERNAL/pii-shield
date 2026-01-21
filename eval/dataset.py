"""
Evaluation Dataset Module

Provides dataset handling for PII detection evaluation.
Supports loading and managing labeled datasets.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union


@dataclass
class LabeledEntity:
    """
    A labeled PII entity in the dataset.
    
    Attributes:
        start: Start character index.
        end: End character index.
        entity_type: Type of PII entity (e.g., "EMAIL_ADDRESS").
        text: The actual PII text.
    """
    start: int
    end: int
    entity_type: str
    text: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "start": self.start,
            "end": self.end,
            "entity_type": self.entity_type,
            "text": self.text,
        }


@dataclass
class LabeledSample:
    """
    A single labeled sample for evaluation.
    
    Attributes:
        text: The input text.
        entities: List of labeled PII entities.
        language: Language code of the text.
        metadata: Optional additional metadata.
    """
    text: str
    entities: List[LabeledEntity]
    language: str = "en"
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "language": self.language,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LabeledSample":
        """Create from dictionary."""
        entities = [
            LabeledEntity(**e) for e in data.get("entities", [])
        ]
        return cls(
            text=data["text"],
            entities=entities,
            language=data.get("language", "en"),
            metadata=data.get("metadata", {}),
        )


class EvaluationDataset:
    """
    Dataset for PII detection evaluation.
    
    Supports loading from JSON files and iterating over samples.
    
    Example:
        >>> dataset = EvaluationDataset.from_json("eval_data.json")
        >>> for sample in dataset:
        ...     print(sample.text)
    """
    
    def __init__(self, samples: Optional[List[LabeledSample]] = None):
        """
        Initialize dataset.
        
        Args:
            samples: List of labeled samples.
        """
        self.samples: List[LabeledSample] = samples or []
    
    def __len__(self) -> int:
        """Return number of samples."""
        return len(self.samples)
    
    def __iter__(self) -> Iterator[LabeledSample]:
        """Iterate over samples."""
        return iter(self.samples)
    
    def __getitem__(self, index: int) -> LabeledSample:
        """Get sample by index."""
        return self.samples[index]
    
    def add_sample(self, sample: LabeledSample):
        """Add a sample to the dataset."""
        self.samples.append(sample)
    
    def add_samples(self, samples: List[LabeledSample]):
        """Add multiple samples to the dataset."""
        self.samples.extend(samples)
    
    def filter_by_language(self, language: str) -> "EvaluationDataset":
        """
        Filter samples by language.
        
        Args:
            language: Language code to filter by.
        
        Returns:
            New EvaluationDataset with filtered samples.
        """
        filtered = [s for s in self.samples if s.language == language]
        return EvaluationDataset(filtered)
    
    def filter_by_entity_type(self, entity_type: str) -> "EvaluationDataset":
        """
        Filter samples containing a specific entity type.
        
        Args:
            entity_type: Entity type to filter by.
        
        Returns:
            New EvaluationDataset with filtered samples.
        """
        filtered = [
            s for s in self.samples
            if any(e.entity_type == entity_type for e in s.entities)
        ]
        return EvaluationDataset(filtered)
    
    def get_entity_types(self) -> List[str]:
        """Get all unique entity types in the dataset."""
        entity_types = set()
        for sample in self.samples:
            for entity in sample.entities:
                entity_types.add(entity.entity_type)
        return sorted(entity_types)
    
    def get_statistics(self) -> Dict:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary with dataset statistics.
        """
        entity_counts = {}
        language_counts = {}
        
        for sample in self.samples:
            # Count languages
            lang = sample.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Count entities
            for entity in sample.entities:
                etype = entity.entity_type
                entity_counts[etype] = entity_counts.get(etype, 0) + 1
        
        return {
            "total_samples": len(self.samples),
            "total_entities": sum(entity_counts.values()),
            "entity_counts": entity_counts,
            "language_counts": language_counts,
        }
    
    def to_json(self, path: Union[str, Path]):
        """
        Save dataset to JSON file.
        
        Args:
            path: Output file path.
        """
        data = {
            "samples": [s.to_dict() for s in self.samples],
            "statistics": self.get_statistics(),
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "EvaluationDataset":
        """
        Load dataset from JSON file.
        
        Args:
            path: Input file path.
        
        Returns:
            EvaluationDataset instance.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        samples = [
            LabeledSample.from_dict(s) for s in data.get("samples", [])
        ]
        
        return cls(samples)
    
    @classmethod
    def create_sample_dataset(cls) -> "EvaluationDataset":
        """
        Create a sample dataset for testing.
        
        Returns:
            EvaluationDataset with sample data.
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
                text="김철수님의 전화번호는 010-1234-5678이고, 주민번호는 900101-1234567입니다.",
                entities=[
                    LabeledEntity(0, 3, "PERSON", "김철수"),
                    LabeledEntity(11, 24, "KR_PHONE_NUMBER", "010-1234-5678"),
                    LabeledEntity(31, 45, "KR_RESIDENT_REGISTRATION_NUMBER", "900101-1234567"),
                ],
                language="ko",
            ),
        ]
        
        return cls(samples)
