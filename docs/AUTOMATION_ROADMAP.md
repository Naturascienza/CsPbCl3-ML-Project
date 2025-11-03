# CsPbCl3 데이터 마이닝 자동화 로드맵

## 📌 프로젝트 목표
**자동으로 논문에서 CsPbCl3 합성 데이터를 추출하는 완전 자동화 시스템 구축**

---

## 🎯 Phase 1: 기반 시스템 (✅ 완료)

### 1.1 PDF 자동 다운로드
- [x] CrossRef API로 DOI 검색
- [x] Unpaywall API로 오픈 액세스 확인
- [x] **Selenium 기관 구독 활용** (80% 성공률)
- [x] Headless 모드로 백그라운드 실행

### 1.2 데이터 추출 기반
- [x] pdfplumber로 텍스트 추출
- [x] 정규표현식 기반 파싱
- [x] **표 우선 추출** (pdfplumber)
- [x] **문맥 인식** (hot-injection 섹션)
- [x] 범위 검증 (온도 100-250°C)

### 1.3 참고 데이터
- [x] GitHub에서 101 샘플 확보
- [x] 고품질 벤치마크 데이터

---

## 🚀 Phase 2: 추출 정확도 개선 (진행 중)

### 2.1 현재 문제점
| 항목 | 현재 상태 | 목표 |
|------|-----------|------|
| Injection Temp | ⚠️ 누락 많음 | ✅ 80%+ |
| Pb/Cs source | ⚠️ 누락 많음 | ✅ 90%+ |
| Size | ✅ 66% | ✅ 80%+ |
| 1S abs/PL | ⚠️ 33% | ✅ 70%+ |

### 2.2 개선 전략

#### A. 표 추출 강화
```python
# 1. tabula-py로 복잡한 표 추출
- Multi-row/col 헤더
- Spanning cells
- 네스팅된 표

# 2. camelot-py로 보완
- 레이아웃 기반 추출
- 표 경계 자동 감지
```

#### B. 문맥 인식 개선
```python
# 1. 섹션별 가중치
- "Experimental" > "Introduction"
- "Synthesis" > "Discussion"

# 2. 키워드 패턴 확장
- "hot injection" → ["hot-injection", "hot injection", "injection method"]
- "CsPbCl3" → ["CsPbCl3", "CsPbCl₃", "cesium lead chloride"]

# 3. 문장 구조 분석
- "We synthesized CsPbCl3 QDs at 180°C" → injection_temp_C = 180
- "PbCl2 (0.2 mmol) and Cs-oleate (0.4 mmol)" → Pb_source = PbCl2
```

#### C. ML 기반 추출
```python
# NER (Named Entity Recognition)
- spaCy custom model
- 화학 물질명 인식
- 수치 + 단위 쌍 추출

# 문맥 임베딩
- BERT fine-tuning
- "inject at 180°C" vs "synthesized in 2024"
```

---

## 🔄 Phase 3: 대규모 자동 수집 (다음 단계)

### 3.1 DOI 소스 확장
```python
# 현재: 수동 큐 (papers_queue.txt)
# 목표: 자동 검색

sources = [
    "CrossRef API",           # 키워드 검색
    "PubMed API",             # 생명과학
    "arXiv API",              # 프리프린트
    "Semantic Scholar API",   # 인용 네트워크
]

keywords = [
    "CsPbCl3 quantum dots",
    "cesium lead chloride QDs",
    "all-inorganic perovskite",
    "hot injection synthesis",
]
```

### 3.2 병렬 처리
```python
# 현재: 순차 처리 (느림)
# 목표: 병렬 처리 (10배 속도)

with multiprocessing.Pool(4) as pool:
    results = pool.map(extract_data, pdf_list)
```

### 3.3 자동 품질 검증
```python
def validate_data(sample):
    checks = [
        100 <= sample['injection_temp_C'] <= 250,  # 온도 범위
        2 <= sample['size_nm'] <= 50,              # 크기 범위
        sample['Cl_source'] in ['PbCl2', 'CsCl'],  # 유효한 source
        sample['abs_1S_peak_nm'] > sample['size_nm'] * 30,  # 물리적 일관성
    ]
    return all(checks)
```

---

## 📊 Phase 4: 데이터 통합 및 ML (최종 목표)

### 4.1 데이터 통합
```python
# 1. 참고 데이터 101 샘플
# 2. 자동 수집 50-100 샘플
# 3. 수동 검증 10-20 샘플
# 총: 160-220 샘플
```

### 4.2 Feature Engineering
```python
features = [
    # 합성 조건 (15개)
    'injection_temp_C',
    'Cl_mmol', 'Pb_mmol', 'Cs_mmol',
    'Cs_to_Pb_ratio', 'Cl_to_Pb_ratio',
    'OA_volume_ml', 'OLA_volume_ml', 'ODE_volume_ml',
    
    # 파생 특징 (10개)
    'total_ligand_volume',
    'Cl_to_ligand_ratio',
    'Pb_concentration',
    'reaction_time_min',
    ...
    
    # 다항식 확장 (100+개)
    PolynomialFeatures(degree=2)
]
```

### 4.3 ML 모델
```python
models = [
    'Support Vector Regression',  # 참고 논문 베스트
    'Random Forest',
    'Gradient Boosting',
    'Neural Network',
]

targets = ['size_nm', 'abs_1S_peak_nm', 'PL_peak_nm']
```

---

## 🎯 단기 목표 (이번 주)

1. **표 추출 강화**: tabula-py + camelot-py 통합
2. **문맥 인식 개선**: 키워드 패턴 3배 확장
3. **자동 수집 테스트**: 20-30개 논문 처리
4. **품질 검증**: 추출 정확도 측정

---

## 📈 성공 지표

| 지표 | 현재 | 1주 후 | 1개월 후 |
|------|------|--------|----------|
| 자동 수집 샘플 수 | 3 | 30 | 100 |
| 추출 정확도 (Injection Temp) | 0% | 60% | 80% |
| 추출 정확도 (Size) | 66% | 80% | 90% |
| 처리 속도 (논문/분) | 0.5 | 2 | 5 |
| ML R² Score | - | 0.70 | 0.85 |

---

## 🛠️ 다음 작업

### 즉시 (오늘)
- [ ] tabula-py 통합 테스트
- [ ] 키워드 패턴 확장 (hot-injection 변형)
- [ ] 10개 논문 수동 검증 (정답 데이터)

### 이번 주
- [ ] 자동 DOI 검색 구현
- [ ] 병렬 처리 시스템 구축
- [ ] 30개 논문 자동 수집 테스트

### 다음 주
- [ ] 100개 논문 목표 달성
- [ ] 데이터 통합 및 정제
- [ ] ML 모델 학습 시작

---

**🎉 최종 목표: "논문 DOI만 입력하면 자동으로 데이터 추출 → ML 학습 → 특성 예측"**
