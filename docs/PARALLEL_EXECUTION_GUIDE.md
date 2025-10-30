# 🔄 병렬 자동화 실행 가이드

CsPbCl3 ML 프로젝트에서 **데이터 수집**과 **분석 작업**을 동시에 실행하는 방법

---

## 📋 목차
1. [개요](#개요)
2. [방법 1: Bash 스크립트 (추천!)](#방법-1-bash-스크립트-추천)
3. [방법 2: Python Multiprocessing](#방법-2-python-multiprocessing)
4. [방법 3: tmux 사용](#방법-3-tmux-사용)
5. [FAQ](#faq)

---

## 🎯 개요

### 병렬 작업 구조
```
┌─────────────────────────────────────────────────────┐
│  Terminal 1 (백그라운드)                             │
│  📥 자동 데이터 수집 (무한 루프)                      │
│  - 5분마다 DOI 큐에서 논문 수집                       │
│  - CSV 파일에 자동 저장                               │
│  - 로그 기록                                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Terminal 2 (모니터링)                                │
│  📊 실시간 대시보드                                    │
│  - 수집 진행 상황 모니터링                            │
│  - 5초마다 갱신                                       │
│  - 통계 및 로그 표시                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Terminal 3 (분석)                                    │
│  🔬 Jupyter Lab / Python                             │
│  - Feature engineering 개발                           │
│  - 모델 학습 및 평가                                  │
│  - 결과 시각화                                        │
└─────────────────────────────────────────────────────┘
```

---

## 방법 1: Bash 스크립트 (추천!)

### 🚀 빠른 시작

```bash
# 1. 프로젝트 디렉토리로 이동
cd /Users/sungwookpark/Library/CloudStorage/OneDrive-개인/Tools_Coding/CsPbCl3-ML-Project

# 2. 병렬 실행 스크립트 실행
./scripts/run_parallel.sh
```

### 📋 메뉴 설명

```
====================================================================
메뉴
====================================================================
  1) 데이터 수집기 시작 (백그라운드)
  2) 모니터링 대시보드 시작 (새 터미널)
  3) Jupyter Lab 시작 (새 터미널)
  4) 모두 시작 (추천!)
  5) 상태 확인
  6) 모두 중지
  7) 종료
```

### 💡 사용 예시

#### 1. 모든 프로세스 시작 (추천)
```bash
./scripts/run_parallel.sh
# 메뉴에서 4번 선택
```

**결과**:
- ✅ 백그라운드에서 데이터 자동 수집 시작
- ✅ 새 터미널 탭: 실시간 모니터링 대시보드
- ✅ 새 터미널 탭: Jupyter Lab

#### 2. 개별 실행
```bash
# 데이터 수집만 시작
./scripts/run_parallel.sh
# 메뉴에서 1번 선택

# 모니터링만 시작
python scripts/monitor_dashboard.py

# Jupyter만 시작
jupyter lab
```

### 📊 수집 설정

#### DOI 큐 파일 작성
```bash
# data/papers_queue.txt 파일 편집
nano data/papers_queue.txt
```

**형식**:
```
# Papers to collect (one DOI per line)
10.1038/s41598-025-08110-2
10.1021/acs.chemmater.2024xxxxx
10.1002/adma.202400xxxx
```

#### 수집 주기 변경
```bash
# 환경 변수로 설정 (초 단위)
export COLLECTION_INTERVAL=180  # 3분마다

# 또는 스크립트 수정
nano scripts/auto_data_collector.py
# interval = 300 → 180으로 변경
```

### 📈 모니터링 화면 예시

```
================================================================================
📊 CsPbCl3 데이터 수집 모니터링 - 2025-10-30 14:35:22
================================================================================

✅ 수집 완료: 15개

📋 최근 수집 (최근 5개):
   - P011: 10.1038/s41598-2024-12345
   - P012: 10.1021/acs.chemmater.2024-67890
   - P013: 10.1002/adma.202400111
   - P014: 10.1039/D4TC00222
   - P015: 10.1016/j.nanoen.2024.03.333

📥 대기 중: 8개

📝 다음 수집 예정 (최대 5개):
   1. 10.1021/acs.nanolett.3c04444
   2. 10.1038/s41467-024-55555-x
   ...

📄 최근 로그 (data_collector_20251030.log):
   2025-10-30 14:35:10 - INFO - 📥 수집 시작: 10.1038/s41598...
   2025-10-30 14:35:12 - INFO - 💾 데이터 저장 완료: P015
   2025-10-30 14:35:12 - INFO - ✅ 큐에서 제거: 10.1038/...

================================================================================
⏱️  5초 후 갱신... (Ctrl+C로 종료)
```

---

## 방법 2: Python Multiprocessing

### 🚀 실행

```bash
python scripts/parallel_processing.py
```

### 특징
- ✅ 3개 워커 프로세스 자동 생성
  1. **DataCollector**: 데이터 수집
  2. **FeatureEngineering**: 특성 계산
  3. **ModelTraining**: 모델 학습
- ✅ 메인 프로세스: 실시간 모니터링
- ✅ 프로세스 간 통신 (Queue)
- ✅ Ctrl+C로 안전하게 모든 프로세스 종료

### 출력 예시
```
================================================================================
🚀 CsPbCl3 ML Project - 병렬 자동화 시작
================================================================================

🚀 워커 프로세스 시작 중...
   ✅ DataCollector 시작 (PID: 12345)
   ✅ FeatureEngineering 시작 (PID: 12346)
   ✅ ModelTraining 시작 (PID: 12347)

✅ 모든 워커 시작 완료

💡 Ctrl+C로 모든 프로세스 중지
================================================================================

2025-10-30 14:40:01 - [DataCollector] - INFO - 🚀 데이터 수집 프로세스 시작
2025-10-30 14:40:01 - [FeatureEngineering] - INFO - 🚀 Feature Engineering 프로세스 시작
2025-10-30 14:40:01 - [ModelTraining] - INFO - 🚀 모델 학습 프로세스 시작

================================================================================
📊 실시간 통계
  📥 수집: 5개
  🔧 Feature Engineering: 3개
  🤖 모델 학습: 1회
================================================================================
```

---

## 방법 3: tmux 사용

### 설치
```bash
# Homebrew (macOS)
brew install tmux
```

### 🚀 사용법

#### 1. 새 세션 생성
```bash
cd /Users/sungwookpark/Library/CloudStorage/OneDrive-개인/Tools_Coding/CsPbCl3-ML-Project
tmux new -s cspbcl3
```

#### 2. 패널 분할
```bash
# 가로 분할 (위/아래)
Ctrl+b "

# 세로 분할 (좌/우)
Ctrl+b %

# 패널 이동
Ctrl+b 방향키
```

#### 3. 각 패널에서 실행
```bash
# 패널 1 (좌상): 데이터 수집
source .venv/bin/activate
python scripts/auto_data_collector.py

# 패널 2 (우상): 모니터링
source .venv/bin/activate
python scripts/monitor_dashboard.py

# 패널 3 (하단): Jupyter Lab
source .venv/bin/activate
jupyter lab
```

#### 4. 레이아웃 예시
```
┌──────────────────────┬──────────────────────┐
│                      │                      │
│  데이터 수집          │  모니터링             │
│  (auto_collector)    │  (dashboard)         │
│                      │                      │
├──────────────────────┴──────────────────────┤
│                                             │
│  Jupyter Lab                                │
│  (분석 작업)                                 │
│                                             │
└─────────────────────────────────────────────┘
```

#### 5. tmux 단축키
```bash
# Detach (백그라운드로)
Ctrl+b d

# Attach (다시 연결)
tmux attach -t cspbcl3

# 세션 목록
tmux ls

# 세션 종료
exit  # 각 패널에서
```

---

## 📊 로그 및 데이터 확인

### 로그 위치
```
logs/
├── collector_output.log         # 수집기 전체 로그
├── monitor_output.log           # 모니터링 로그
├── data_collector_20251030.log  # 날짜별 수집 로그
├── feature_engineering_*.log    # Feature engineering 로그
└── model_training_*.log         # 모델 학습 로그
```

### 데이터 파일
```
data/
├── literature_data_template.csv   # 템플릿 (변경 금지)
├── literature_data_collected.csv  # 수집된 데이터 (자동 업데이트)
└── papers_queue.txt               # 수집 대기 큐
```

### 실시간 로그 확인
```bash
# 수집 로그 tail
tail -f logs/data_collector_$(date +%Y%m%d).log

# 수집된 데이터 개수 확인
tail -n +2 data/literature_data_collected.csv | wc -l

# 큐 대기 개수
grep -v '^#' data/papers_queue.txt | grep -v '^$' | wc -l
```

---

## 🛠️ 커스터마이징

### 1. 수집 주기 변경
```python
# scripts/auto_data_collector.py
interval = 300  # 초 단위 (5분)
```

### 2. 모니터링 갱신 주기
```python
# scripts/monitor_dashboard.py
interval = 5  # 초 단위
```

### 3. 수집 로직 커스터마이징
```python
# scripts/auto_data_collector.py
def collect_from_doi(self, doi: str):
    # 여기에 실제 수집 로직 구현
    # - CrossRef API
    # - Web scraping
    # - PDF parsing
    pass
```

---

## ❓ FAQ

### Q1: 백그라운드 프로세스가 실행 중인지 확인하려면?
```bash
# PID 파일 확인
cat .pids/collector.pid

# 프로세스 확인
ps -p $(cat .pids/collector.pid)

# 또는 스크립트 메뉴에서
./scripts/run_parallel.sh
# → 5번 선택 (상태 확인)
```

### Q2: 백그라운드 프로세스를 중지하려면?
```bash
# 스크립트 사용
./scripts/run_parallel.sh
# → 6번 선택 (모두 중지)

# 또는 수동으로
kill $(cat .pids/collector.pid)
```

### Q3: 로그가 너무 많이 쌓이면?
```bash
# 7일 이상 된 로그 삭제
find logs/ -name "*.log" -mtime +7 -delete

# 로그 압축
gzip logs/*.log
```

### Q4: 수집 중 오류가 발생하면?
```bash
# 로그 확인
tail -100 logs/data_collector_$(date +%Y%m%d).log | grep ERROR

# 큐 파일 확인 (잘못된 DOI 제거)
nano data/papers_queue.txt
```

### Q5: 여러 머신에서 병렬 수집하려면?
```bash
# 각 머신에서 다른 큐 파일 사용
# Machine 1
python scripts/auto_data_collector.py --queue papers_queue_1.txt

# Machine 2
python scripts/auto_data_collector.py --queue papers_queue_2.txt

# 나중에 데이터 병합
pandas.concat([df1, df2]).to_csv('merged.csv')
```

---

## 🎯 권장 워크플로우

### Phase 1: 초기 설정 (한 번만)
```bash
1. DOI 리스트 준비 (50-100개)
2. papers_queue.txt에 추가
3. ./scripts/run_parallel.sh 실행 → 4번 선택 (모두 시작)
```

### Phase 2: 병렬 작업 (매일)
```
Terminal 1: 데이터 수집 (자동 실행 중)
Terminal 2: 모니터링 (5초마다 갱신)
Terminal 3: Jupyter Lab (분석 작업)
  - Feature engineering 개발
  - 모델 학습
  - 결과 시각화
```

### Phase 3: 주기적 점검 (주 1회)
```bash
1. 수집 통계 확인 (모니터링 대시보드)
2. 로그 오류 체크
3. 데이터 품질 검증
4. 큐에 새 논문 추가
```

---

## 📝 요약

| 방법 | 장점 | 단점 | 추천도 |
|------|------|------|--------|
| **Bash 스크립트** | 간편, 자동화, GUI | macOS 전용 | ⭐⭐⭐⭐⭐ |
| **Python MP** | 크로스 플랫폼, 통합 | 터미널 1개만 | ⭐⭐⭐⭐ |
| **tmux** | 유연성, 세션 유지 | 학습 곡선 | ⭐⭐⭐ |

**추천**: 먼저 Bash 스크립트로 시작, 나중에 tmux로 고급 활용!

---

**다음**: [Feature Engineering 가이드](../notebooks/03_research_upgrade_strategy.ipynb)
