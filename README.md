# 🛡️ PII Shield

**Protect Your PII with Microsoft Presidio**

PII Shield is a comprehensive library for detecting and masking Personally Identifiable Information (PII) in text data. Built on top of [Microsoft Presidio](https://github.com/microsoft/presidio), it provides an easy-to-use interface for PII protection with multi-language support.

## ✨ Features

- **PII Detection**: Detect various types of PII including names, emails, phone numbers, credit cards, and more
- **PII Masking**: Multiple masking strategies (replace, redact, hash, mask)
- **Multi-language Support**: Built-in support for English and Korean
- **Custom Recognizers**: Easily extend with custom PII recognizers
- **Evaluation Tools**: Comprehensive metrics for evaluating detection performance
- **REST API**: Ready-to-use API server for integration
- **CLI Tool**: Command-line interface for quick operations

## 📁 Project Structure

```
pii-shield/
├── core/                    # Core PII detection and masking module
│   ├── __init__.py
│   ├── detector.py          # PII detection using Presidio Analyzer
│   ├── masker.py            # PII masking using Presidio Anonymizer
│   ├── shield.py            # High-level unified interface
│   └── recognizers/         # Custom PII recognizers
│       ├── __init__.py
│       └── korean.py        # Korean-specific recognizers
├── eval/                    # Evaluation module
│   ├── __init__.py
│   ├── evaluator.py         # PII detection evaluator
│   ├── metrics.py           # Evaluation metrics (precision, recall, F1)
│   └── dataset.py           # Evaluation dataset handling
├── app/                     # Application module
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   └── api.py               # REST API server
├── samples/                 # Sample code and examples
│   ├── basic_usage.py       # Basic usage examples
│   ├── custom_recognizer.py # Custom recognizer examples
│   └── evaluation_example.py# Evaluation examples
├── tests/                   # Unit tests
├── pyproject.toml           # Project configuration
└── README.md
```

## 🚀 Installation

### Basic Installation

```bash
pip install pii-shield
```

### Install with API support

```bash
pip install pii-shield[api]
```

### Install from source

```bash
git clone https://github.com/MSFT-AI-BUILD-INTERNAL/pii-shield.git
cd pii-shield
pip install -e .
```

### Download Language Models

After installation, download the required spaCy language models:

```bash
# English model (required)
python -m spacy download en_core_web_lg

# Korean model (optional, for Korean language support)
python -m spacy download ko_core_news_lg
```

## 📖 How to Use

### Basic Usage

```python
from core import PIIShield

# Initialize PII Shield
shield = PIIShield()

# Detect and mask PII
text = "Contact John Doe at john.doe@example.com or call 555-123-4567."
result = shield.protect(text)

print(f"Original: {result.original_text}")
print(f"Masked:   {result.masked_text}")
print(f"Detected: {result.entity_count}")
```

Output:
```
Original: Contact John Doe at john.doe@example.com or call 555-123-4567.
Masked:   Contact <PERSON> at <EMAIL_ADDRESS> or call <PHONE_NUMBER>.
Detected: {'PERSON': 1, 'EMAIL_ADDRESS': 1, 'PHONE_NUMBER': 1}
```

### Detection Only

```python
from core import PIIShield

shield = PIIShield()
text = "My credit card is 4111-1111-1111-1111"

# Detect without masking
entities = shield.detect_only(text)

for entity in entities:
    print(f"{entity.entity_type}: {text[entity.start:entity.end]} (score: {entity.score:.2f})")
```

### Different Masking Strategies

```python
from core import PIIShield
from core.masker import MaskingStrategy

text = "Email: alice@example.com"

# Replace strategy (default)
shield = PIIShield(default_strategy=MaskingStrategy.REPLACE)
result = shield.protect(text)
print(result.masked_text)  # Email: <EMAIL_ADDRESS>

# Redact strategy
shield = PIIShield(default_strategy=MaskingStrategy.REDACT)
result = shield.protect(text)
print(result.masked_text)  # Email: 

# Hash strategy
shield = PIIShield(default_strategy=MaskingStrategy.HASH)
result = shield.protect(text)
print(result.masked_text)  # Email: a1b2c3d4...

# Mask strategy
shield = PIIShield(default_strategy=MaskingStrategy.MASK)
result = shield.protect(text)
print(result.masked_text)  # Email: *****************
```

### Korean Language Support

```python
from core import PIIShield

# Initialize with Korean support
shield = PIIShield(languages=["en", "ko"], default_language="ko")

text = "김철수님의 이메일은 chulsoo@example.com입니다."
result = shield.protect(text, language="ko")

print(result.masked_text)
```

### CLI Usage

```bash
# Detect PII
pii-shield detect "Contact john@example.com for help"

# Mask PII
pii-shield mask "My email is john@example.com" --strategy replace

# Process a file
pii-shield file input.txt -o output.txt --strategy redact
```

### REST API

```bash
# Start the API server
python -m app.api

# Or with uvicorn
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

API Endpoints:
- `POST /detect` - Detect PII in text
- `POST /mask` - Detect and mask PII
- `GET /entities` - Get supported entity types
- `GET /health` - Health check

## 🔧 How to Customize

### Adding Custom Recognizers

```python
from presidio_analyzer import Pattern, PatternRecognizer
from core import PIIDetector

# Create a custom recognizer
class EmployeeIDRecognizer(PatternRecognizer):
    PATTERNS = [
        Pattern("Employee ID", r"\bEMP-\d{4}-\d{4}\b", 0.9),
    ]
    
    def __init__(self):
        super().__init__(
            supported_entity="EMPLOYEE_ID",
            patterns=self.PATTERNS,
            context=["employee", "id", "staff"],
            supported_language="en",
        )

# Register the recognizer
detector = PIIDetector()
detector.analyzer.registry.add_recognizer(EmployeeIDRecognizer())

# Use the detector
text = "Employee EMP-1234-5678 reported an issue."
results = detector.detect(text)
```

### Custom Masking Operators

```python
from core import PIIShield, PIIMasker
from presidio_anonymizer.entities import OperatorConfig

shield = PIIShield()
text = "Contact john@example.com"

# Detect first
entities = shield.detect_only(text)

# Create custom operator
custom_operators = {
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL HIDDEN]"})
}

# Mask with custom operator
masked = shield.masker.mask(text, entities, operators=custom_operators)
print(masked)  # Contact [EMAIL HIDDEN]
```

### Evaluation

```python
from core import PIIShield
from eval import PIIEvaluator, EvaluationDataset
from eval.dataset import LabeledSample, LabeledEntity

# Create test dataset
samples = [
    LabeledSample(
        text="Contact john@example.com",
        entities=[LabeledEntity(8, 24, "EMAIL_ADDRESS", "john@example.com")],
        language="en",
    ),
]
dataset = EvaluationDataset(samples)

# Evaluate
evaluator = PIIEvaluator()
results = evaluator.evaluate(dataset)

# Print report
evaluator.print_report(results)
```

## 📊 Supported Entity Types

| Entity Type | Description |
|-------------|-------------|
| PERSON | Person names |
| EMAIL_ADDRESS | Email addresses |
| PHONE_NUMBER | Phone numbers |
| CREDIT_CARD | Credit card numbers |
| IBAN_CODE | International Bank Account Numbers |
| IP_ADDRESS | IP addresses |
| DATE_TIME | Dates and times |
| LOCATION | Geographic locations |
| URL | Web URLs |
| NRP | Nationality, Religion, Political group |
| MEDICAL_LICENSE | Medical license numbers |
| KR_RESIDENT_REGISTRATION_NUMBER | Korean resident registration numbers |
| KR_PHONE_NUMBER | Korean phone numbers |
| KR_BANK_ACCOUNT | Korean bank account numbers |

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=core --cov=eval --cov-report=term-missing
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Microsoft Presidio](https://github.com/microsoft/presidio) - The underlying PII detection and anonymization engine
- [spaCy](https://spacy.io/) - NLP library used for named entity recognition