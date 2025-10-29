# 📊 Reference Paper 상세 분석
## Machine learning models for accurately predicting properties of CsPbCl3 Perovskite quantum dots

**저자**: Mehmet Sıddık Çadırcı & Musa Çadırcı  
**출판**: Scientific Reports (2025) 15:30924  
**DOI**: 10.1038/s41598-025-08110-2

---

## 🎯 1. 연구 목적
- CsPbCl3 Perovskite Quantum Dots (PQDs)의 **Size, 1S abs, PL** 특성 예측
- 문헌 기반 데이터 수집 (59개 peer-reviewed papers)
- 6개 ML 알고리즘 성능 비교

---

## 📦 2. 데이터셋 상세

### 2.1 데이터 규모
- **총 데이터 포인트**: 708개 (531 input, 177 output)
- **데이터 소스**: 59개 peer-reviewed papers
- **Train/Test 비율**: 80% / 20% (Stratified sampling)

### 2.2 입력 특성 (Input Features) - 총 15개
1. **Injection Temperature** (°C)
2. **Chlorine (Cl) source** (categorical)
3. **Cl amount** (mmol)
4. **Lead (Pb) source** (categorical)
5. **Pb amount** (mmol)
6. **Cesium (Cs) source** (categorical)
7. **Cs amount** (mmol)
8. **Molar ratio**: Cs-to-Pb
9. **Molar ratio**: Cl-to-Pb
10. **ODE volume** (ml) - Octadecene
11. **OA volume** (ml) - Oleic Acid
12. **OLA volume** (ml) - Oleylamine
13. **Total ligand volume** (OA+OLA) (ml)
14. **Ratio**: Cl amount / Total ligand volume
15. **Ratio**: Pb / Total ligand volume

### 2.3 출력 특성 (Output Targets) - 3개
1. **Size** (nm) - Median: ~9.5 nm
2. **1S abs** (nm) - Range: 395-402 nm (First excitonic absorption peak)
3. **PL** (nm) - Range: 405-412 nm (Photoluminescence)

### 2.4 데이터 전처리
- **Outlier 제거**: Z-score > 3 or < -3인 데이터 제외 (residual analysis)
- **Missing value 처리**: Median imputation
- **Feature Engineering**: Polynomial & Logarithmic transformations
- **차원 축소**: PCA (95% variance 유지)

---

## 🤖 3. 사용된 ML 알고리즘

### 3.1 Support Vector Regression (SVR)
- **Kernel**: Radial Basis Function (RBF)
- **Hyperparameter Tuning**: Grid Search
- **Library**: scikit-learn

### 3.2 Nearest Neighbor Distance (NND)
- **Algorithm**: k-Nearest Neighbor (k-NN) 기반
- **Library**: scikit-learn

### 3.3 Decision Tree (DT)
- **Hyperparameter**: max_depth (cross-validation)
- **Library**: scikit-learn

### 3.4 Random Forest (RF)
- **Number of trees**: 500
- **Hyperparameter**: max_features (cross-validation)
- **Library**: scikit-learn

### 3.5 Gradient Boosting Machine (GBM)
- **Hyperparameters**: learning rate, number of boosting rounds, max_depth
- **Tuning**: Cross-validation
- **Library**: scikit-learn

### 3.6 Deep Learning (DL)
- **Type**: Neural Networks
- **Library**: scikit-learn
- **특징**: Non-linear transformation 학습

---

## 📈 4. 성능 결과 (Performance Metrics)

### 4.1 종합 성능 표

| Target | Model | Train R² | Train RMSE | Train MAE | **Test R²** | **Test RMSE** | **Test MAE** |
|--------|-------|----------|------------|-----------|-------------|---------------|--------------|
| **Size** | **SVR** | 0.99 | 0.009 | 0.009 | **0.80** | **0.34** | **0.16** |
| | **NND** | 0.99 | 0.012 | 0.008 | **0.62** | 0.47 | 0.30 |
| | DL | 0.77 | 0.49 | 0.38 | 0.10 | 0.74 | 0.56 |
| | **DT** | 0.94 | 0.23 | 0.17 | **0.94** | **0.23** | **0.16** |
| | RF | 0.93 | 0.26 | 0.20 | 0.51 | 0.66 | 0.54 |
| | GBM | 0.97 | 0.14 | 0.13 | 0.48 | 0.56 | 0.38 |
| **1S abs** | **SVR** | 0.99 | 0.009 | 0.008 | **0.84** | **0.34** | **0.19** |
| | **NND** | 0.99 | 0.009 | 0.005 | 0.55 | 0.59 | 0.34 |
| | DL | 0.66 | 0.59 | 0.39 | 0.44 | 0.66 | 0.49 |
| | **DT** | 0.96 | 0.19 | 0.13 | **0.96** | **0.19** | **0.13** |
| | RF | 0.94 | 0.23 | 0.17 | 0.64 | 0.53 | 0.37 |
| | GBM | 0.98 | 0.11 | 0.09 | 0.66 | 0.51 | 0.30 |
| **PL** | **SVR** | 0.99 | 0.009 | 0.009 | 0.66 | 0.58 | 0.28 |
| | **NND** | 0.99 | 0.005 | 0.002 | **0.78** | **0.46** | **0.29** |
| | DL | 0.73 | 0.51 | 0.38 | 0.53 | 0.68 | 0.56 |
| | **DT** | 0.97 | 0.16 | 0.11 | **0.97** | **0.16** | **0.11** |
| | RF | 0.94 | 0.23 | 0.16 | 0.70 | 0.54 | 0.39 |
| | GBM | 0.99 | 0.09 | 0.07 | 0.71 | 0.53 | 0.34 |

### 4.2 최고 성능 모델 (Test Data 기준)
1. **SVR**: 1S abs 예측에서 R²=0.84, Size 예측에서 R²=0.80
2. **NND**: PL 예측에서 R²=0.78
3. **DT**: 모든 타겟에서 일관되게 높은 성능 (R²=0.94~0.97)

### 4.3 성능 순위 (Test R² 기준)
- **Best**: SVR, NND, DT
- **Moderate**: GBM, RF
- **Worst**: DL (Deep Learning은 작은 데이터셋에서 성능 저하)

---

## 🔍 5. Feature Importance (특성 중요도)

### 5.1 1S abs 예측에 중요한 특성 (SVR 기준)
1. **Cs amount** (가장 중요)
2. **OA amount** (중요)
3. Cl amount (덜 중요)
4. ODE amount (덜 중요)

### 5.2 Size 예측에 중요한 특성
- **Pb amount** (가장 중요)

### 5.3 PL 예측에 중요한 특성
- **Cs amount** (가장 중요)

### 5.4 Cs ratio의 중요성
- CsPbCl3 PQDs의 광학·전자적 특성에 **가장 큰 영향**
- Morphological & crystal structure 변화 → Stability 영향
- 실험 데이터와도 일치하는 결과

---

## 📊 6. Pearson Correlation (상관관계 분석)

| Feature Pair | Correlation |
|-------------|-------------|
| **1S abs - PL** | **+0.66** (Strong positive) |
| **Size - PL** | **+0.081** (Weak) |
| **Size - 1S abs** | Weak |

### 6.1 해석
- **1S abs와 PL의 강한 상관관계**: 양자 구속 효과 (Quantum confinement)
- **Size와 PL의 약한 상관관계**: 다른 메커니즘 영향
  - Exciton recombination mechanisms
  - Trap state dynamics
  - Ligand-related effects

---

## ⚠️ 7. 논문의 한계점 (Limitations)

### 7.1 데이터 관련 한계
- **데이터 규모**: 708개 (중간 규모)
- **Edge cases**: 드문 합성 조건 미반영 가능성
- **Labelled data 의존**: Supervised learning만 사용
- **데이터 수집 비용**: 실험 데이터 라벨링 시간·비용 소요

### 7.2 방법론 한계
- **선형 상관관계 분석**: Pearson correlation으로 비선형 관계 포착 불가
- **단일 재료 시스템**: CsPbCl3만 다룸 (다른 perovskite는 미검증)
- **해석 가능성 부족**: ML 모델의 물리적 의미 검증 부족
- **Feature importance만**: SHAP, LIME 같은 고급 XAI 미사용

### 7.3 모델 한계
- **Overfitting 위험**: 작은 데이터셋에서 DL, RF 성능 저하
- **Generalization**: 다른 합성 조건에 대한 일반화 불확실
- **Multi-task learning 부재**: Size, 1S abs, PL을 개별 예측

### 7.4 합성 조건 복잡성
- **Temperature 의존성**: 시간에 따른 온도 변화 미고려
- **Chemical input 복잡성**: 다양한 precursor 조합 미탐색
- **Dynamic process**: 합성 시간, 냉각 속도 등 미포함

---

## ✅ 8. 논문의 강점

1. **체계적인 비교**: 6개 ML 알고리즘 동시 평가
2. **문헌 기반 데이터**: 59개 논문에서 신뢰성 있는 데이터 수집
3. **적절한 전처리**: Outlier 제거, PCA, Feature engineering
4. **성능 우수**: SVR, DT에서 R²=0.8~0.97 달성
5. **Feature importance 분석**: Cs, Pb, OA의 중요성 규명
6. **오픈소스**: GitHub에 데이터·코드 공개

---

## 🚀 9. 우리 프로젝트의 업그레이드 방향

### 9.1 데이터 측면
- ✅ **더 큰 데이터셋**: 100+ papers (vs. 59 papers)
- ✅ **더 많은 특성**: Dynamic features (시간, 냉각 속도) 추가
- ✅ **Physics-informed features**: Band gap, lattice constant 등

### 9.2 모델 측면
- ✅ **Multi-Task Learning**: Size, 1S abs, PL 동시 예측 (공유 특성 학습)
- ✅ **Hybrid Ensemble-DL**: XGBoost + LightGBM + Neural Network
- ✅ **Transfer Learning**: 다른 perovskite 데이터 활용

### 9.3 해석 측면
- ✅ **Advanced XAI**: SHAP, LIME, Partial Dependence Plots
- ✅ **Physical validation**: 예측 결과의 물리적 타당성 검증
- ✅ **Interaction analysis**: 특성 간 상호작용 분석

### 9.4 최적화 측면
- ✅ **Bayesian Optimization**: 최적 합성 조건 탐색
- ✅ **Active Learning**: 효율적인 실험 설계
- ✅ **Uncertainty Quantification**: 예측 불확실성 정량화

---

## 📚 10. GitHub Repository
**URL**: https://github.mehmetsiddik/Machine-Learning-Models-CsPbCI3_QDs.git

---

## 📝 11. 추가 참고사항

### 11.1 비교 대상 (InP QDs)
- 이전 연구 (Ref. 19)의 InP QDs 예측:
  - Test MAE: Size 0.33, 1S abs 20.29, PL 11.46
- 현재 CsPbCl3 PQDs 예측 (DT 모델):
  - Test MAE: Size 0.16, 1S abs 0.13, PL 0.11
- **성능 향상**: CsPbCl3가 InP보다 예측 정확도 훨씬 높음

### 11.2 물리적 의미
- **1S abs**: Lowest optical energy transition (첫 번째 exciton 흡수)
- **PL**: Radiative emission between conduction-valance bands
- **Quantum confinement**: Size ↓ → Band gap ↑ → 1S abs/PL 변화

---

## 🎯 12. 결론

이 논문은 **CsPbCl3 PQDs의 ML 기반 특성 예측**에서 우수한 성능을 보였으나,  
아래 영역에서 **명확한 업그레이드 기회**가 존재합니다:

1. ❌ **Multi-task learning 부재** → 우리: MTL로 공유 특성 학습
2. ❌ **Physics-informed features 부족** → 우리: 물리 기반 특성 추가
3. ❌ **단순 feature importance** → 우리: SHAP, LIME으로 심화 분석
4. ❌ **Optimization 전략 부재** → 우리: Bayesian + Active Learning
5. ❌ **작은 데이터셋 (59 papers)** → 우리: 100+ papers 수집

**우리의 차별화된 접근법으로 기존 논문보다 한 단계 발전된 연구 가능! 🚀**
