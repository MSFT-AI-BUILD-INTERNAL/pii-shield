# 🛡️ PII Shield

**Protect Your PII with Microsoft Foundry & Presidio**

PII Shield is a comprehensive library for detecting and masking Personally Identifiable Information (PII) in text data. Powered by **Microsoft Foundry (Azure Language Service)** and **[Microsoft Presidio](https://github.com/microsoft/presidio)**, it provides maximum PII detection coverage through dual-engine detection with intelligent result merging.

## 🤖 AI-Powered PII Detection

PII Shield leverages **dual AI engines** for maximum PII detection coverage:

- **Microsoft Foundry (Azure Language Service)**: Cloud-based AI service with continuously updated models
- **Microsoft Presidio**: Local NER models powered by spaCy with custom pattern matching

By combining both engines and intelligently merging results, PII Shield can identify:

- **Person Names** - Detected using NER models trained on large datasets
- **Email Addresses, Phone Numbers** - Pattern-based detection with ML validation
- **Credit Cards, SSN, Bank Accounts** - Intelligent pattern recognition
- **Dates, Locations, Organizations** - Context-aware entity extraction

This makes PII Shield ideal for enterprises looking to **automate PII compliance**, **protect customer data**, and **ensure GDPR/CCPA compliance** without manual review.

> **💡 Important**: The underlying Presidio models are continuously being improved by Microsoft and the open-source community. For production deployments, **fine-tuning the models for your specific language and domain** can significantly improve detection accuracy. Custom training with your organization's data patterns is recommended for optimal performance.

## ✨ Features

- **🔄 Dual Detection**: Combines Microsoft Foundry and Presidio for maximum coverage
- **🎯 Strict Merge Rule**: Automatically selects wider entity coverage when overlaps occur
- **🎭 Flexible Masking**: Multiple strategies - asterisk-only (`***`), labels (`<PERSON>`), redact, hash
- **🌐 Multi-language Support**: Built-in support for English and Korean
- **☁️ Cloud + Local**: Works with Azure cloud or fully offline with Presidio
- **🔧 Custom Recognizers**: Easily extend with custom PII recognizers
- **📊 Evaluation Tools**: Comprehensive metrics for evaluating detection performance
- **🚀 REST API**: Ready-to-use API server for integration
- **⚡ CLI Tool**: Command-line interface for quick operations

## 📁 Project Structure

```
pii-shield/
├── core/                    # Core PII detection and masking module
│   ├── __init__.py
│   ├── detector.py          # Local PII detection using Presidio Analyzer
│   ├── masker.py            # PII masking with multiple strategies
│   ├── shield.py            # High-level unified interface (dual detection)
│   ├── azure_pii.py         # Azure Foundry integration
│   └── recognizers/         # Custom PII recognizers
│       ├── __init__.py
│       └── korean.py        # Korean-specific recognizers (SSN, phone, etc.)
├── eval/                    # Evaluation module
│   ├── __init__.py
│   ├── evaluator.py         # PII detection evaluator
│   ├── metrics.py           # Evaluation metrics (precision, recall, F1)
│   └── dataset.py           # Evaluation dataset handling
├── bench/                   # Validation & Benchmarking
│   ├── __init__.py
│   ├── validation.py        # Multi-language validation runner
│   ├── en/
│   │   ├── dataset.csv      # English test dataset (15 cases)
│   │   └── validation.py    # English-specific validation
│   ├── ko/
│   │   ├── dataset.csv      # Korean test dataset (15 cases)
│   │   └── validation.py    # Korean-specific validation
│   └── report/              # Generated validation reports
│       └── *.md             # Timestamped validation reports
├── app/                     # Application module
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   └── api.py               # REST API server (FastAPI)
├── samples/                 # Sample code and examples
│   ├── basic_usage.py       # Basic usage examples
│   ├── custom_recognizer.py # Custom recognizer examples
│   ├── evaluation_example.py# Evaluation examples
│   ├── azure_pii_example.py # Azure Foundry integration examples
│   ├── strict_merge_demo.py # Strict merge rule demonstration
│   └── mask_only_demo.py    # Mask-only strategy demonstration
├── tests/                   # Unit tests
├── docs/                    # Additional documentation
│   ├── ENVIRONMENT.md       # Environment configuration guide
│   ├── STRICT_MERGE_RULE.md # Dual detection merge logic
│   └── MASK_ONLY_STRATEGY.md# Masking strategy guide
├── .env.sample              # Environment variables template
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

### Install with Azure/Foundry support

```bash
# Install with Azure dependencies for dual detection
pip install pii-shield[azure]

# Or if using uv (recommended)
uv sync --extra azure
```

### Install from source

```bash
git clone https://github.com/MSFT-AI-BUILD-INTERNAL/pii-shield.git
cd pii-shield
pip install -e .

# For Azure support
pip install -e ".[azure]"
```

### Download Language Models

After installation, download the required spaCy language models:

```bash
# English model (required)
python -m spacy download en_core_web_lg

# Korean model (optional, for Korean language support)
python -m spacy download ko_core_news_lg
```

### Environment Configuration

PII Shield supports `.env` files for easy configuration management:

```bash
# 1. Copy the sample environment file
cp .env.sample .env

# 2. Edit .env with your settings (optional)
# Leave AZURE_FOUNDRY_ENDPOINT empty to use local Presidio only
# Set AZURE_FOUNDRY_ENDPOINT to enable cloud-based Azure detection

# For Presidio-only (local detection):
# AZURE_FOUNDRY_ENDPOINT=

# For Azure Language Service (cloud detection with Presidio fallback):
# AZURE_FOUNDRY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

For detailed environment configuration, see [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

## 📖 How to Use

### Basic Usage

```python
from core import PIIShield, MaskingStrategy

# Initialize PII Shield
# Automatically uses DUAL DETECTION (Foundry + Presidio) if AZURE_FOUNDRY_ENDPOINT is set
# Otherwise uses Presidio only (local detection)
shield = PIIShield()

# Detect and mask PII with asterisks (privacy-focused)
text = "Contact John Doe at john.doe@example.com or call 555-123-4567."
result = shield.protect(text, strategy=MaskingStrategy.MASK)

print(f"Original: {result.original_text}")
print(f"Masked:   {result.masked_text}")
print(f"Detected: {result.entity_count}")
```

Output:
```
Original: Contact John Doe at john.doe@example.com or call 555-123-4567.
Masked:   Contact ******** at ******************** or call ************.
Detected: {'PERSON': 1, 'EMAIL_ADDRESS': 1, 'PHONE_NUMBER': 1}
```

### Dual Detection with Microsoft Foundry

PII Shield uses **dual detection** to maximize PII coverage by running both engines simultaneously:

**How Dual Detection Works:**
1. **Parallel Detection**: Both Foundry and Presidio analyze the text
2. **Result Merging**: Combines entities from both engines
3. **Strict Merge Rule**: When entities overlap, selects the one with wider coverage
4. **Maximum Coverage**: Any PII found by either engine is masked

**Example - Strict Merge Rule:**
```python
# Input: "세종대왕은 위대한 왕입니다"
# Foundry detects: "세종" (partial)
# Presidio detects: "세종대왕" (full)
# Result: "세종대왕" is selected (wider coverage)
```

**Automatic Mode (Recommended):**
```python
from core import PIIShield

# If AZURE_FOUNDRY_ENDPOINT is set:
#   - Azure SDK installed → Uses BOTH Foundry AND Presidio (dual detection)
#   - Azure SDK NOT installed → Raises ImportError
# If AZURE_FOUNDRY_ENDPOINT is not set:
#   - Uses Presidio only (local detection)
shield = PIIShield()

result = shield.protect("My email is john@example.com")
# Automatically uses dual detection if Azure is configured
```

**Azure-Only Mode (No Fallback):**
```python
from core import PIIShield

# Uses Azure only, no Presidio fallback
# Requires AZURE_FOUNDRY_ENDPOINT to be set
# If Azure fails, raises RuntimeError instead of falling back
shield = PIIShield(azure_only=True)

result = shield.protect("My email is john@example.com")
```

**Presidio-Only Mode:**
```python
from core import PIIShield

# Force Presidio-only, even if Azure is configured
shield = PIIShield(use_azure=False)

result = shield.protect("My email is john@example.com")
```

**Azure Setup:**
```bash
# 1. Install Azure dependencies
pip install pii-shield[azure]

# 2. Login with Azure CLI
az login

# 3. Set environment variable
export AZURE_FOUNDRY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/

# 4. Use PIIShield normally - Azure integration is automatic!
python samples/basic_usage.py
```

**Important:** If you set `AZURE_FOUNDRY_ENDPOINT` but haven't installed Azure SDK, you'll get a clear error message:
```
ImportError: AZURE_FOUNDRY_ENDPOINT is set but Azure SDK is not installed.
Please install with: pip install pii-shield[azure]
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

### Masking Strategies

```python
from core import PIIShield, MaskingStrategy

text = "Email: alice@example.com"

# MASK strategy (recommended - privacy-focused)
# Replaces PII with asterisks, no entity type labels
shield = PIIShield(default_strategy=MaskingStrategy.MASK)
result = shield.protect(text)
print(result.masked_text)  # Email: *****************

# REPLACE strategy
# Replaces PII with entity type labels
shield = PIIShield(default_strategy=MaskingStrategy.REPLACE)
result = shield.protect(text)
print(result.masked_text)  # Email: <EMAIL_ADDRESS>

# REDACT strategy
# Completely removes PII
shield = PIIShield(default_strategy=MaskingStrategy.REDACT)
result = shield.protect(text)
print(result.masked_text)  # Email: 

# HASH strategy
# Replaces with consistent hash
shield = PIIShield(default_strategy=MaskingStrategy.HASH)
result = shield.protect(text)
print(result.masked_text)  # Email: a1b2c3d4...
```

**Strategy Comparison:**

| Strategy | Output Example | Privacy Level | Use Case |
|----------|---------------|---------------|----------|
| `MASK` | `********` | ⭐⭐⭐⭐⭐ Highest | Maximum privacy, no entity info leakage |
| `REPLACE` | `<EMAIL>` | ⭐⭐⭐⭐ High | Clear indication of what was masked |
| `REDACT` | `` | ⭐⭐⭐⭐⭐ Highest | Complete removal, may break readability |
| `HASH` | `abc123...` | ⭐⭐⭐ Medium | Consistent anonymization for analytics |

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

## 📊 Validation & Benchmarking

PII Shield includes comprehensive validation tools to ensure detection accuracy across languages:

### Running Validation

```bash
# Run validation for all languages
python -m bench.validation

# Validate specific language
python -m bench.validation --lang en
python -m bench.validation --lang ko

# Quiet mode (summary only)
python -m bench.validation --quiet

# List available languages
python -m bench.validation --list
```

### Benchmark Results

Current validation results with **100% accuracy** across all languages:

| Language | Test Cases | Exact Match | Partial Match | Exact Accuracy | Status |
|----------|------------|-------------|---------------|----------------|--------|
| English  | 15         | 15          | 0             | 100.00%        | ✅ PASS |
| Korean   | 15         | 15          | 0             | 100.00%        | ✅ PASS |
| **Total**| **30**     | **30**      | **0**         | **100.00%**    | ✅ **PASS** |

### Test Coverage

**English Dataset** covers:
- Person names (John Doe, Alice Smith, etc.)
- Email addresses (john.doe@example.com)
- Phone numbers (555-123-4567, 1-800-555-0199)
- Credit card numbers (4111-1111-1111-1111)
- IP addresses (192.168.1.100)
- URLs (https://example.com)
- Dates and times (January 15, 2024, Friday)
- Locations (New York, Los Angeles)

**Korean Dataset** covers:
- Korean names (김철수, 홍길동, 세종대왕)
- Korean phone numbers (010-1234-5678)
- Korean SSN (주민등록번호: 900101-1234567)
- Korean bank accounts (123-456-789012)
- Email addresses in Korean context
- Mixed Korean-English text

### Validation Reports

Detailed validation reports are automatically generated in `bench/report/` with:
- Timestamp-based filenames
- Per-language accuracy metrics
- Failed case analysis (if any)
- Entity detection breakdown
- Masking comparison (expected vs. actual)

Example report: `bench/report/20260124_091739_ko_validation_report.md`

### Masking-Based Validation

Validation uses **mask-based comparison** instead of entity labels:

```python
# Input
"Contact John Doe at john.doe@example.com"

# Expected (mask-based)
"Contact ******** at ********************"

# Validation checks:
# 1. Exact match - masked text matches exactly
# 2. Partial match - at least one PII detected (30% tolerance)
```

This approach ensures:
- Privacy-first validation (no entity type leakage)
- Consistent masking verification
- Real-world usage simulation

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

- **[Microsoft Foundry](https://azure.microsoft.com/products/ai-services/ai-language)** - Azure Language Service for cloud-based PII detection
- **[Microsoft Presidio](https://github.com/microsoft/presidio)** - Local PII detection and anonymization engine
- **[spaCy](https://spacy.io/)** - NLP library used for named entity recognition
- **[Azure Identity](https://docs.microsoft.com/python/api/azure-identity)** - Microsoft Entra ID authentication