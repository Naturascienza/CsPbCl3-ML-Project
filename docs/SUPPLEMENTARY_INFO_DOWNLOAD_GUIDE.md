# 참고 논문 Supplementary Information 다운로드 가이드

## 📚 논문 정보
- **제목**: Machine learning prediction of quantum dot synthesis and properties from reaction conditions
- **저자**: Çadırcı, Hasan Ferhun; Tavakoli, Elham; Arslantas, Ferhat
- **DOI**: 10.1038/s41598-025-08110-2
- **저널**: Scientific Reports (2025)
- **데이터**: 708 샘플 (59 papers)

## 🔗 다운로드 링크
https://doi.org/10.1038/s41598-025-08110-2

## 📥 다운로드 방법

### 방법 1: 수동 다운로드 헬퍼 (권장) ⭐
```bash
python scripts/download_si_manual.py
```

**특징**:
- ✅ 백그라운드에서 Chrome 새 탭 열기
- ✅ 현재 작업 방해 안 함 (포커스 유지)
- ✅ 명확한 단계별 안내
- ✅ 파일 자동 감지

### 방법 2: 자동 다운로드 (Selenium)
```bash
python scripts/download_si_auto.py
```

**특징**:
- ✅ 쿠키 배너 자동 처리
- ✅ PDF 링크 자동 클릭
- ✅ 백그라운드 창 (최소화)
- ⚠️ 일부 사이트에서 수동 개입 필요

### 방법 3: 직접 다운로드 (전통적)
1. 위 DOI 링크 클릭
2. 논문 페이지에서 "**Supplementary information**" 섹션 찾기
3. "Supplementary Information" PDF 다운로드
4. `pdf/supplementary/` 폴더에 저장

### 방법 2: 직접 검색
1. Google Scholar 또는 Nature 검색
2. "Machine learning prediction CsPbCl3 quantum dot 2025"
3. 논문 찾기 → SI 다운로드

## 📊 Supplementary Information 내용

논문에 따르면 다음 표들이 포함되어 있습니다:

- **Table S1**: 전체 708개 샘플 데이터
  - 합성 조건: 온도, 전구체, 양, 리간드
  - QD 특성: 크기, PL, PLQY, FWHM
  
- **Table S2**: 추가 분석 데이터

## 💾 저장 위치
```
CsPbCl3-ML-Project/
└── pdf/
    └── supplementary/
        ├── supplementary_information.pdf  ← 여기에 저장
        └── (또는 다른 파일명)
```

## 🚀 다운로드 후 실행

SI 파일을 다운로드한 후:

```bash
# 데이터 추출
python scripts/extract_reference_data.py

# 표 자동 추출
python scripts/extract_si_tables.py
```

## 📝 참고사항

- SI 파일은 보통 **Excel (.xlsx)** 또는 **PDF** 형식
- Excel이 가장 좋음 (바로 읽을 수 있음)
- PDF일 경우 tabula-py로 표 추출

## ❓ 문제 해결

### SI 파일을 찾을 수 없는 경우:
1. 논문이 Early Access 단계일 수 있음
2. 저자에게 직접 요청
3. 논문 본문의 Figure/Table에서 대표 샘플 수동 추출

### 기관 접근 없는 경우:
- 논문 본문에 요약된 데이터라도 활용 가능
- 50-100개 대표 샘플로 시작 가능

---

**다음 단계**: SI 다운로드 → 표 추출 → 708 샘플 확보 → ML 시작! 🚀
