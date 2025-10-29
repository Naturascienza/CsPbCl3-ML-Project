# 데이터 수집 가이드

## 📋 데이터 입력 필드 설명

### 메타데이터
- `paper_id`: 논문 고유 ID (예: paper_001, paper_002)
- `author`: 제1저자 또는 교신저자
- `year`: 발표 연도
- `doi`: Digital Object Identifier

### 합성 조건
- `temperature_C`: 합성 온도 (섭씨)
- `reaction_time_min`: 반응 시간 (분 단위)
- `cs_concentration_M`: Cs 전구체 농도 (Molarity)
- `pb_concentration_M`: Pb 전구체 농도
- `cl_concentration_M`: Cl 전구체 농도
- `cs_pb_ratio`: Cs:Pb 비율 (예: 1:1, 2:1)
- `cs_cl_ratio`: Cs:Cl 비율
- `pb_cl_ratio`: Pb:Cl 비율
- `ligand_type`: 리간드 종류 (OA=Oleic Acid, OAm=Oleylamine)
- `ligand_concentration_M`: 리간드 농도
- `solvent`: 용매 (ODE=1-Octadecene, toluene 등)
- `injection_rate`: 주입 속도 (fast/slow/dropwise)
- `synthesis_method`: 합성 방법 (hot-injection, room-temperature 등)

### 측정 결과 (Target Variables)
- `pl_peak_nm`: Photoluminescence 피크 위치 (나노미터)
- `plqy_percent`: Photoluminescence Quantum Yield (%)
- `fwhm_nm`: Full Width at Half Maximum (나노미터)
- `qd_size_nm`: 양자점 크기 (나노미터, TEM/DLS 측정)

### 기타
- `notes`: 추가 정보나 특이사항

## 📊 데이터 입력 팁

1. **단위 통일**: 모든 데이터는 위에 명시된 단위로 변환
2. **결측치 표기**: 데이터가 없으면 빈 칸 또는 'NA'
3. **범위 값**: 범위로 표기된 경우 중간값 사용 (예: 150-170°C → 160°C)
4. **정확도**: 원본 논문의 유효숫자 유지

## 🔍 문헌 검색 키워드

```
"CsPbCl3" AND ("quantum dot" OR "QD")
"CsPbCl3" AND "synthesis"
"CsPbCl3" AND "photoluminescence"
"all-inorganic perovskite" AND "quantum dot"
"cesium lead chloride" AND "nanocrystal"
```

## 📚 추천 데이터베이스
- Web of Science
- Scopus
- Google Scholar
- ACS Publications
- Nature
- Wiley Online Library
