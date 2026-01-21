# 🛡️ PII Shield

**Microsoft Presidio를 활용한 개인정보 보호 라이브러리**

PII Shield는 텍스트 데이터에서 개인식별정보(PII)를 탐지하고 마스킹하는 종합 라이브러리입니다. [Microsoft Presidio](https://github.com/microsoft/presidio)를 기반으로 구축되어, 다국어 지원과 함께 사용하기 쉬운 PII 보호 인터페이스를 제공합니다.

## 🤖 AI 기반 개인정보 탐지

PII Shield는 **AI 및 머신러닝 모델**을 활용하여 일반 텍스트(Plain Text)에서 민감한 개인정보를 자동으로 탐지합니다. spaCy 기반의 개체명 인식(NER) 모델과 커스텀 패턴 매칭을 사용하여 다음을 식별할 수 있습니다:

- **사람 이름** - 대규모 데이터셋으로 학습된 NER 모델로 탐지
- **이메일, 전화번호** - ML 검증을 통한 패턴 기반 탐지
- **신용카드, 주민등록번호, 계좌번호** - 지능형 패턴 인식
- **날짜, 위치, 조직** - 컨텍스트 인식 엔티티 추출

이를 통해 PII Shield는 **PII 컴플라이언스 자동화**, **고객 데이터 보호**, **GDPR/개인정보보호법 준수**가 필요한 기업에 이상적인 솔루션입니다.

> **💡 중요**: 기반이 되는 Presidio 모델은 Microsoft와 오픈소스 커뮤니티에 의해 지속적으로 개선되고 있습니다. 프로덕션 배포 시, **특정 언어와 도메인에 맞게 모델을 파인튜닝**하면 탐지 정확도를 크게 향상시킬 수 있습니다. 최적의 성능을 위해 조직의 데이터 패턴에 맞는 커스텀 학습을 권장합니다.

## ✨ 주요 기능

- **PII 탐지**: 이름, 이메일, 전화번호, 신용카드 번호 등 다양한 유형의 PII 탐지
- **PII 마스킹**: 다양한 마스킹 전략 지원 (치환, 삭제, 해시, 마스크)
- **다국어 지원**: 영어와 한국어 기본 지원
- **커스텀 인식기**: 커스텀 PII 인식기로 쉽게 확장 가능
- **평가 도구**: 탐지 성능 평가를 위한 종합 메트릭
- **REST API**: 통합을 위한 즉시 사용 가능한 API 서버
- **CLI 도구**: 빠른 작업을 위한 명령줄 인터페이스

## 📁 프로젝트 구조

```
pii-shield/
├── core/                    # 핵심 PII 탐지 및 마스킹 모듈
│   ├── __init__.py
│   ├── detector.py          # Presidio Analyzer를 사용한 PII 탐지
│   ├── masker.py            # Presidio Anonymizer를 사용한 PII 마스킹
│   ├── shield.py            # 고수준 통합 인터페이스
│   └── recognizers/         # 커스텀 PII 인식기
│       ├── __init__.py
│       └── korean.py        # 한국어 전용 인식기
├── eval/                    # 평가 모듈
│   ├── __init__.py
│   ├── evaluator.py         # PII 탐지 평가기
│   ├── metrics.py           # 평가 메트릭 (정밀도, 재현율, F1)
│   └── dataset.py           # 평가 데이터셋 처리
├── app/                     # 애플리케이션 모듈
│   ├── __init__.py
│   ├── cli.py               # 명령줄 인터페이스
│   └── api.py               # REST API 서버
├── samples/                 # 샘플 코드 및 예제
│   ├── basic_usage.py       # 기본 사용 예제
│   ├── custom_recognizer.py # 커스텀 인식기 예제
│   └── evaluation_example.py# 평가 예제
├── tests/                   # 단위 테스트
├── pyproject.toml           # 프로젝트 설정
└── README.md
```

## 🚀 설치

### 기본 설치

```bash
pip install pii-shield
```

### API 지원 포함 설치

```bash
pip install pii-shield[api]
```

### 소스에서 설치

```bash
git clone https://github.com/MSFT-AI-BUILD-INTERNAL/pii-shield.git
cd pii-shield
pip install -e .
```

### 언어 모델 다운로드

설치 후, 필요한 spaCy 언어 모델을 다운로드하세요:

```bash
# 영어 모델 (필수)
python -m spacy download en_core_web_lg

# 한국어 모델 (선택, 한국어 지원 시 필요)
python -m spacy download ko_core_news_lg
```

## 📖 사용 방법

### 기본 사용법

```python
from core import PIIShield

# PII Shield 초기화 (한국어 지원)
shield = PIIShield(languages=["en", "ko"], default_language="ko")

# PII 탐지 및 마스킹
text = "안녕하세요, 김철수입니다. 연락처는 010-1234-5678입니다."
result = shield.protect(text, language="ko")

print(f"원본: {result.original_text}")
print(f"마스킹: {result.masked_text}")
print(f"탐지됨: {result.entity_count}")
```

출력:
```
원본: 안녕하세요, 김철수입니다. 연락처는 010-1234-5678입니다.
마스킹: 안녕하세요, <KR_NAME>입니다. 연락처는 <KR_PHONE_NUMBER>입니다.
탐지됨: {'KR_NAME': 1, 'KR_PHONE_NUMBER': 1}
```

### 탐지만 수행

```python
from core import PIIShield

shield = PIIShield(languages=["en", "ko"], default_language="ko")
text = "홍길동님의 주민등록번호는 900101-1234567입니다."

# 마스킹 없이 탐지만 수행
entities = shield.detect_only(text, language="ko")

for entity in entities:
    print(f"{entity.entity_type}: {text[entity.start:entity.end]} (점수: {entity.score:.2f})")
```

출력:
```
KR_NAME: 홍길동 (점수: 0.85)
KR_SSN: 900101-1234567 (점수: 0.85)
```

### 다양한 마스킹 전략

```python
from core import PIIShield
from core.masker import MaskingStrategy

text = "이메일: alice@example.com"

# 치환 전략 (기본값)
shield = PIIShield(languages=["en", "ko"], default_language="ko", default_strategy=MaskingStrategy.REPLACE)
result = shield.protect(text, language="ko")
print(result.masked_text)  # 이메일: <KR_EMAIL>

# 삭제 전략
shield = PIIShield(languages=["en", "ko"], default_language="ko", default_strategy=MaskingStrategy.REDACT)
result = shield.protect(text, language="ko")
print(result.masked_text)  # 이메일: 

# 해시 전략
shield = PIIShield(languages=["en", "ko"], default_language="ko", default_strategy=MaskingStrategy.HASH)
result = shield.protect(text, language="ko")
print(result.masked_text)  # 이메일: a1b2c3d4...

# 마스크 전략
shield = PIIShield(languages=["en", "ko"], default_language="ko", default_strategy=MaskingStrategy.MASK)
result = shield.protect(text, language="ko")
print(result.masked_text)  # 이메일: *****************
```

### 한국어 고급 사용법

```python
from core import PIIShield

# 한국어 지원으로 초기화
shield = PIIShield(languages=["en", "ko"], default_language="ko")

# 다양한 한국어 PII 탐지
text = "정약용 고객님의 계좌 987-654-321098로 환불 처리됩니다."
result = shield.protect(text, language="ko")

print(result.masked_text)
# 출력: <KR_NAME> 고객님의 계좌 <KR_BANK_ACCOUNT>로 환불 처리됩니다.
```

### CLI 사용법

```bash
# PII 탐지
pii-shield detect "홍길동님의 연락처는 010-1234-5678입니다"

# PII 마스킹
pii-shield mask "제 이메일은 hong@example.com입니다" --strategy replace

# 파일 처리
pii-shield file input.txt -o output.txt --strategy redact
```

### REST API

```bash
# API 서버 시작
python -m app.api

# 또는 uvicorn 사용
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

API 엔드포인트:
- `POST /detect` - 텍스트에서 PII 탐지
- `POST /mask` - PII 탐지 및 마스킹
- `GET /entities` - 지원되는 엔티티 타입 조회
- `GET /health` - 헬스 체크

## 🔧 커스터마이징

### 커스텀 인식기 추가

```python
from presidio_analyzer import Pattern, PatternRecognizer
from core import PIIDetector

# 커스텀 인식기 생성
class EmployeeIDRecognizer(PatternRecognizer):
    PATTERNS = [
        Pattern("사원 ID", r"\bEMP-\d{4}-\d{4}\b", 0.9),
    ]
    
    def __init__(self):
        super().__init__(
            supported_entity="EMPLOYEE_ID",
            patterns=self.PATTERNS,
            context=["직원", "사원", "id", "staff"],
            supported_language="en",
        )

# 인식기 등록
detector = PIIDetector()
detector.analyzer.registry.add_recognizer(EmployeeIDRecognizer())

# 탐지기 사용
text = "직원 EMP-1234-5678이 이슈를 보고했습니다."
results = detector.detect(text)
```

### 커스텀 마스킹 연산자

```python
from core import PIIShield, PIIMasker
from presidio_anonymizer.entities import OperatorConfig

shield = PIIShield()
text = "연락처: john@example.com"

# 먼저 탐지
entities = shield.detect_only(text)

# 커스텀 연산자 생성
custom_operators = {
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[이메일 숨김]"})
}

# 커스텀 연산자로 마스킹
masked = shield.masker.mask(text, entities, operators=custom_operators)
print(masked)  # 연락처: [이메일 숨김]
```

### 평가

```python
from core import PIIShield
from eval import PIIEvaluator, EvaluationDataset
from eval.dataset import LabeledSample, LabeledEntity

# 테스트 데이터셋 생성
samples = [
    LabeledSample(
        text="연락처: john@example.com",
        entities=[LabeledEntity(5, 21, "EMAIL_ADDRESS", "john@example.com")],
        language="en",
    ),
]
dataset = EvaluationDataset(samples)

# 평가
evaluator = PIIEvaluator()
results = evaluator.evaluate(dataset)

# 리포트 출력
evaluator.print_report(results)
```

## 📊 지원 엔티티 타입

| 엔티티 타입 | 설명 |
|------------|------|
| PERSON | 사람 이름 |
| EMAIL_ADDRESS | 이메일 주소 |
| PHONE_NUMBER | 전화번호 |
| CREDIT_CARD | 신용카드 번호 |
| IBAN_CODE | 국제 은행 계좌 번호 |
| IP_ADDRESS | IP 주소 |
| DATE_TIME | 날짜 및 시간 |
| LOCATION | 지리적 위치 |
| URL | 웹 URL |
| NRP | 국적, 종교, 정치 집단 |
| MEDICAL_LICENSE | 의료 면허 번호 |
| KR_SSN | 한국 주민등록번호 |
| KR_PHONE_NUMBER | 한국 전화번호 |
| KR_BANK_ACCOUNT | 한국 은행 계좌번호 |
| KR_EMAIL | 한국어 컨텍스트의 이메일 |
| KR_NAME | 한국 이름 |

## 🧪 테스트 실행

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 테스트 실행
pytest

# 커버리지와 함께 테스트 실행
pytest --cov=core --cov=eval --cov-report=term-missing
```

## 📊 벤치마크 검증

```bash
# 전체 언어 검증
python -m bench.validation

# 특정 언어만 검증
python -m bench.validation --lang en
python -m bench.validation --lang ko

# 간략 모드
python -m bench.validation --quiet

# 사용 가능한 언어 목록
python -m bench.validation --list
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [Microsoft Presidio](https://github.com/microsoft/presidio) - 기반이 되는 PII 탐지 및 익명화 엔진
- [spaCy](https://spacy.io/) - 개체명 인식에 사용되는 NLP 라이브러리
