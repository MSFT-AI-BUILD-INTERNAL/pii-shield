# 🛡️ PII Shield

**Microsoft Foundry & Presidio로 개인정보 보호**

PII Shield는 텍스트 데이터에서 개인식별정보(PII)를 탐지하고 마스킹하는 종합 라이브러리입니다. **Microsoft Foundry (Azure Language Service)**와 **[Microsoft Presidio](https://github.com/microsoft/presidio)**를 결합하여 듀얼 엔진 탐지와 지능형 결과 병합을 통해 최대한의 PII 탐지 커버리지를 제공합니다.

## 🤖 AI 기반 개인정보 탐지

PII Shield는 최대 PII 탐지 커버리지를 위해 **듀얼 AI 엔진**을 활용합니다:

- **Microsoft Foundry (Azure Language Service)**: 지속적으로 업데이트되는 모델을 갖춘 클라우드 기반 AI 서비스
- **Microsoft Presidio**: spaCy 기반의 로컬 NER 모델과 커스텀 패턴 매칭

두 엔진을 결합하고 결과를 지능적으로 병합하여 다음을 식별할 수 있습니다:

- **사람 이름** - 대규모 데이터셋으로 학습된 NER 모델로 탐지
- **이메일, 전화번호** - ML 검증을 통한 패턴 기반 탐지
- **신용카드, 주민등록번호, 계좌번호** - 지능형 패턴 인식
- **날짜, 위치, 조직** - 컨텍스트 인식 엔티티 추출

이를 통해 PII Shield는 **PII 컴플라이언스 자동화**, **고객 데이터 보호**, **GDPR/개인정보보호법 준수**가 필요한 기업에 이상적인 솔루션입니다.

> **💡 중요**: 기반이 되는 Presidio 모델은 Microsoft와 오픈소스 커뮤니티에 의해 지속적으로 개선되고 있습니다. 프로덕션 배포 시, **특정 언어와 도메인에 맞게 모델을 파인튜닝**하면 탐지 정확도를 크게 향상시킬 수 있습니다. 최적의 성능을 위해 조직의 데이터 패턴에 맞는 커스텀 학습을 권장합니다.

## ✨ 주요 기능

- **🔄 듀얼 탐지**: Microsoft Foundry와 Presidio를 결합하여 최대 커버리지
- **🎯 엄격한 병합 규칙**: 겹칠 때 자동으로 더 넓은 범위의 엔티티 선택
- **🎭 유연한 마스킹**: 다양한 전략 - 별표 전용 (`***`), 레이블 (`<PERSON>`), 삭제, 해시
- **🌐 다국어 지원**: 영어와 한국어 기본 지원
- **☁️ 클라우드 + 로컬**: Azure 클라우드 또는 Presidio로 완전 오프라인 동작
- **🔧 커스텀 인식기**: 커스텀 PII 인식기로 쉽게 확장 가능
- **📊 평가 도구**: 탐지 성능 평가를 위한 종합 메트릭
- **🚀 REST API**: 통합을 위한 즉시 사용 가능한 API 서버
- **⚡ CLI 도구**: 빠른 작업을 위한 명령줄 인터페이스

## 📁 프로젝트 구조

```
pii-shield/
├── core/                    # 핵심 PII 탐지 및 마스킹 모듈
│   ├── __init__.py
│   ├── detector.py          # Presidio Analyzer를 사용한 로컬 PII 탐지
│   ├── masker.py            # 다양한 전략을 사용한 PII 마스킹
│   ├── shield.py            # 고수준 통합 인터페이스 (듀얼 탐지)
│   ├── azure_pii.py         # Azure Foundry 통합
│   └── recognizers/         # 커스텀 PII 인식기
│       ├── __init__.py
│       └── korean.py        # 한국어 전용 인식기 (주민번호, 전화번호 등)
├── eval/                    # 평가 모듈
│   ├── __init__.py
│   ├── evaluator.py         # PII 탐지 평가기
│   ├── metrics.py           # 평가 메트릭 (정밀도, 재현율, F1)
│   └── dataset.py           # 평가 데이터셋 처리
├── bench/                   # 검증 및 벤치마킹
│   ├── __init__.py
│   ├── validation.py        # 다국어 검증 실행기
│   ├── en/
│   │   ├── dataset.csv      # 영어 테스트 데이터셋 (15개 케이스)
│   │   └── validation.py    # 영어 전용 검증
│   ├── ko/
│   │   ├── dataset.csv      # 한국어 테스트 데이터셋 (15개 케이스)
│   │   └── validation.py    # 한국어 전용 검증
│   └── report/              # 생성된 검증 보고서
│       └── *.md             # 타임스탬프 기반 검증 보고서
├── app/                     # 애플리케이션 모듈
│   ├── __init__.py
│   ├── cli.py               # 명령줄 인터페이스
│   └── api.py               # REST API 서버 (FastAPI)
├── samples/                 # 샘플 코드 및 예제
│   ├── basic_usage.py       # 기본 사용 예제
│   ├── custom_recognizer.py # 커스텀 인식기 예제
│   ├── evaluation_example.py# 평가 예제
│   ├── azure_pii_example.py # Azure Foundry 통합 예제
│   ├── strict_merge_demo.py # 엄격한 병합 규칙 데모
│   └── mask_only_demo.py    # 마스크 전용 전략 데모
├── tests/                   # 단위 테스트
├── docs/                    # 추가 문서
│   ├── ENVIRONMENT.md       # 환경 설정 가이드
│   ├── STRICT_MERGE_RULE.md # 듀얼 탐지 병합 로직
│   └── MASK_ONLY_STRATEGY.md# 마스킹 전략 가이드
├── .env.sample              # 환경 변수 템플릿
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

### Azure/Foundry 지원 포함 설치

```bash
# 듀얼 탐지를 위한 Azure 종속성 설치
pip install pii-shield[azure]

# 또는 uv 사용 시 (권장)
uv sync --extra azure
```

### 소스에서 설치

```bash
git clone https://github.com/MSFT-AI-BUILD-INTERNAL/pii-shield.git
cd pii-shield
pip install -e .

# Azure 지원 포함
pip install -e ".[azure]"
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
from core import PIIShield, MaskingStrategy

# PII Shield 초기화
# AZURE_FOUNDRY_ENDPOINT가 설정되어 있으면 자동으로 듀얼 탐지 (Foundry + Presidio)
# 설정되어 있지 않으면 Presidio만 사용 (로컬 탐지)
shield = PIIShield()

# 별표로 PII 탐지 및 마스킹 (프라이버시 최우선)
text = "안녕하세요, 김철수입니다. 연락처는 010-1234-5678입니다."
result = shield.protect(text, language="ko", strategy=MaskingStrategy.MASK)

print(f"원본: {result.original_text}")
print(f"마스킹: {result.masked_text}")
print(f"탐지됨: {result.entity_count}")
```

출력:
```
원본: 안녕하세요, 김철수입니다. 연락처는 010-1234-5678입니다.
마스킹: 안녕하세요, ***입니다. 연락처는 *************입니다.
탐지됨: {'PERSON': 1, 'PHONE_NUMBER': 1}
```

### Microsoft Foundry와의 듀얼 탐지

PII Shield는 **듀얼 탐지**를 사용하여 두 엔진을 동시에 실행하여 PII 커버리지를 최대화합니다:

**듀얼 탐지 동작 방식:**
1. **병렬 탐지**: Foundry와 Presidio가 동시에 텍스트 분석
2. **결과 병합**: 두 엔진의 엔티티를 결합
3. **엄격한 병합 규칙**: 엔티티가 겹칠 때 더 넓은 범위를 선택
4. **최대 커버리지**: 어느 엔진에서든 발견된 PII는 모두 마스킹

**예시 - 엄격한 병합 규칙:**
```python
# 입력: "세종대왕은 위대한 왕입니다"
# Foundry 탐지: "세종" (부분)
# Presidio 탐지: "세종대왕" (전체)
# 결과: "세종대왕" 선택 (더 넓은 범위)
```

**자동 모드 (권장):**
```python
from core import PIIShield

# AZURE_FOUNDRY_ENDPOINT가 설정된 경우:
#   - Azure SDK 설치됨 → Foundry와 Presidio 모두 사용 (듀얼 탐지)
#   - Azure SDK 미설치 → ImportError 발생
# AZURE_FOUNDRY_ENDPOINT가 설정되지 않은 경우:
#   - Presidio만 사용 (로컬 탐지)
shield = PIIShield()

result = shield.protect("내 이메일은 john@example.com입니다")
# Azure가 구성되어 있으면 자동으로 듀얼 탐지 사용
```

**Azure 전용 모드:**
```python
from core import PIIShield

# Azure만 사용, Presidio 폴백 없음
# AZURE_FOUNDRY_ENDPOINT 설정 필요
shield = PIIShield(azure_only=True)

result = shield.protect("내 이메일은 john@example.com입니다")
```

**Presidio 전용 모드:**
```python
from core import PIIShield

# Azure가 구성되어 있어도 Presidio만 강제 사용
shield = PIIShield(use_azure=False)

result = shield.protect("내 이메일은 john@example.com입니다")
```

**Azure 설정:**
```bash
# 1. Azure 종속성 설치
pip install pii-shield[azure]

# 2. Azure CLI로 로그인
az login

# 3. 환경 변수 설정
export AZURE_FOUNDRY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/

# 4. PIIShield를 평소처럼 사용 - Azure 통합은 자동!
python samples/basic_usage.py
```



```python
from core import PIIShield, MaskingStrategy

text = "이메일: alice@example.com"

# MASK 전략 (권장 - 프라이버시 최우선)
# PII를 별표로 치환, 엔티티 타입 레이블 없음
shield = PIIShield(default_strategy=MaskingStrategy.MASK)
result = shield.protect(text)
print(result.masked_text)  # 이메일: *****************

# REPLACE 전략
# PII를 엔티티 타입 레이블로 치환
shield = PIIShield(default_strategy=MaskingStrategy.REPLACE)
result = shield.protect(text)
print(result.masked_text)  # 이메일: <EMAIL_ADDRESS>

# REDACT 전략
# PII를 완전히 제거
shield = PIIShield(default_strategy=MaskingStrategy.REDACT)
result = shield.protect(text)
print(result.masked_text)  # 이메일: 

# HASH 전략
# 일관된 해시로 치환
shield = PIIShield(default_strategy=MaskingStrategy.HASH)
result = shield.protect(text)
print(result.masked_text)  # 이메일: a1b2c3d4...
```

**전략 비교:**

| 전략 | 출력 예시 | 프라이버시 레벨 | 사용 사례 |
|----------|---------------|---------------|----------|
| `MASK` | `********` | ⭐⭐⭐⭐⭐ 최고 | 최대 프라이버시, 엔티티 정보 누출 없음 |
| `REPLACE` | `<EMAIL>` | ⭐⭐⭐⭐ 높음 | 무엇이 마스킹되었는지 명확히 표시 |
| `REDACT` | `` | ⭐⭐⭐⭐⭐ 최고 | 완전 제거, 가독성 저하 가능 |
| `HASH` | `abc123...` | ⭐⭐⭐ 보통 | 분석을 위한 일관된 익명화 |

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

## 📊 검증 및 벤치마킹

PII Shield는 언어별 탐지 정확도를 보장하기 위한 종합적인 검증 도구를 포함합니다:

### 검증 실행

```bash
# 모든 언어에 대한 검증 실행
python -m bench.validation

# 특정 언어만 검증
python -m bench.validation --lang en
python -m bench.validation --lang ko

# 간략 모드 (요약만)
python -m bench.validation --quiet

# 사용 가능한 언어 목록
python -m bench.validation --list
```

### 벤치마크 결과

모든 언어에서 **100% 정확도** 달성:

| 언어 | 테스트 케이스 | 정확히 일치 | 부분 일치 | 정확도 | 상태 |
|------|------------|-----------|---------|--------|------|
| 영어 | 15         | 15        | 0       | 100.00% | ✅ 통과 |
| 한국어 | 15         | 15        | 0       | 100.00% | ✅ 통과 |
| **합계**| **30**     | **30**    | **0**   | **100.00%** | ✅ **통과** |

### 테스트 커버리지

**영어 데이터셋** 포함 항목:
- 사람 이름 (John Doe, Alice Smith 등)
- 이메일 주소 (john.doe@example.com)
- 전화번호 (555-123-4567, 1-800-555-0199)
- 신용카드 번호 (4111-1111-1111-1111)
- IP 주소 (192.168.1.100)
- URL (https://example.com)
- 날짜 및 시간 (January 15, 2024, Friday)
- 위치 (New York, Los Angeles)

**한국어 데이터셋** 포함 항목:
- 한국 이름 (김철수, 홍길동, 세종대왕)
- 한국 전화번호 (010-1234-5678)
- 주민등록번호 (900101-1234567)
- 은행 계좌번호 (123-456-789012)
- 한국어 컨텍스트의 이메일 주소
- 한국어-영어 혼합 텍스트

### 검증 보고서

상세한 검증 보고서가 `bench/report/`에 자동 생성됩니다:
- 타임스탬프 기반 파일명
- 언어별 정확도 메트릭
- 실패 케이스 분석 (있는 경우)
- 엔티티 탐지 상세 정보
- 마스킹 비교 (예상 vs. 실제)

예시 보고서: `bench/report/20260124_091739_ko_validation_report.md`

### 마스킹 기반 검증

검증은 엔티티 레이블 대신 **마스크 기반 비교**를 사용합니다:

```python
# 입력
"연락처: 김철수 010-1234-5678"

# 예상 (마스크 기반)
"연락처: *** *************"

# 검증 확인 사항:
# 1. 정확히 일치 - 마스킹된 텍스트가 정확히 일치
# 2. 부분 일치 - 최소 하나의 PII가 탐지됨 (30% 허용 오차)
```

이 접근 방식은 다음을 보장합니다:
- 프라이버시 우선 검증 (엔티티 타입 정보 노출 없음)
- 일관된 마스킹 검증
- 실제 사용 시나리오 시뮬레이션

## 🧪 테스트 실행

이 프로젝트는 MIT 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- **[Microsoft Foundry](https://azure.microsoft.com/products/ai-services/ai-language)** - 클라우드 기반 PII 탐지를 위한 Azure Language Service
- **[Microsoft Presidio](https://github.com/microsoft/presidio)** - 로컬 PII 탐지 및 익명화 엔진
- **[spaCy](https://spacy.io/)** - 개체명 인식에 사용되는 NLP 라이브러리
- **[Azure Identity](https://docs.microsoft.com/python/api/azure-identity)** - Microsoft Entra ID 인증
