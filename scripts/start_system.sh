#!/bin/bash

# CsPbCl3 데이터 마이닝 시스템 통합 런처
# 하나의 터미널에서 모든 작업 관리

PROJECT_ROOT="/Users/sungwookpark/Library/CloudStorage/OneDrive-개인/Tools_Coding/CsPbCl3-ML-Project"
cd "$PROJECT_ROOT"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

clear

echo "================================================================================"
echo "🚀 CsPbCl3 데이터 마이닝 자동화 시스템"
echo "================================================================================"
echo ""
echo "📊 현재 상태:"
echo ""

# 큐 상태 확인
if [ -f "data/papers_queue.txt" ]; then
    QUEUE_COUNT=$(grep -v '^#' data/papers_queue.txt | grep -v '^$' | wc -l | xargs)
    echo "   📋 대기 중인 논문: ${QUEUE_COUNT}개"
else
    echo "   ⚠️  큐 파일 없음"
fi

# 수집 배치 확인
BATCH_COUNT=$(ls -1 data/parallel_collected_*.csv 2>/dev/null | wc -l | xargs)
if [ "$BATCH_COUNT" -gt 0 ]; then
    echo "   ✅ 수집 완료 배치: ${BATCH_COUNT}개"
fi

# 참고 데이터
if [ -f "data/reference_dataset.xlsx" ]; then
    echo "   📚 참고 데이터: 101 샘플"
fi

echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "어떤 작업을 수행할까요?"
echo ""
echo "   1️⃣  병렬 데이터 수집 (1회, 백그라운드)"
echo "   2️⃣  무한 데이터 수집 (자동 큐 재충전) 🔥"
echo "   3️⃣  실시간 모니터링 대시보드"
echo "   4️⃣  웹 대시보드 생성 + 자동 열기"
echo "   5️⃣  Jupyter Lab 시작 (새 탭)"
echo "   6️⃣  대화형 Python 메뉴 (모든 기능)"
echo "   7️⃣  수집 결과 확인"
echo "   8️⃣  실행 중인 프로세스 확인"
echo "   9️⃣  모든 백그라운드 작업 종료"
echo "   0️⃣  종료"
echo ""
echo "────────────────────────────────────────────────────────────────────────────────"
echo ""
read -p "👉 선택: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 병렬 데이터 수집 (1회)을 백그라운드에서 시작합니다...${NC}"
        echo ""
        
        # 백그라운드 실행
        LOG_FILE="logs/parallel_collector_$(date +%Y%m%d_%H%M%S).log"
        nohup .venv/bin/python -c "
from scripts.parallel_collector import ParallelCollector
collector = ParallelCollector(num_workers=4)
collector.run()
" > "$LOG_FILE" 2>&1 &
        COLLECTOR_PID=$!
        
        echo "✅ 시작됨! PID: $COLLECTOR_PID"
        echo "📄 로그: $LOG_FILE"
        echo "💡 큐가 비면 자동 종료됩니다."
        echo ""
        ;;
    
    2)
        echo ""
        echo -e "${YELLOW}� 무한 데이터 수집 (자동 큐 재충전)을 시작합니다...${NC}"
        echo ""
        echo "�💡 큐가 부족하면 자동으로 새 DOI를 검색합니다."
        echo "⏸️  Ctrl+C로 중단 가능"
        echo ""
        
        # 배치 설정
        read -p "📦 배치 크기 (기본 20개, Enter=기본값): " BATCH_SIZE
        BATCH_SIZE=${BATCH_SIZE:-20}
        
        read -p "🔢 최대 배치 수 (Enter=무한): " MAX_BATCHES
        MAX_BATCHES=${MAX_BATCHES:-}
        
        # 백그라운드 실행
        LOG_FILE="logs/continuous_collector_$(date +%Y%m%d_%H%M%S).log"
        
        if [ -z "$MAX_BATCHES" ]; then
            nohup .venv/bin/python -c "
from scripts.parallel_collector import ParallelCollector
collector = ParallelCollector(num_workers=4)
collector.run_continuous(batch_size=$BATCH_SIZE, max_batches=None)
" > "$LOG_FILE" 2>&1 &
        else
            nohup .venv/bin/python -c "
from scripts.parallel_collector import ParallelCollector
collector = ParallelCollector(num_workers=4)
collector.run_continuous(batch_size=$BATCH_SIZE, max_batches=$MAX_BATCHES)
" > "$LOG_FILE" 2>&1 &
        fi
        
        COLLECTOR_PID=$!
        
        echo ""
        echo "✅ 무한 수집 시작! PID: $COLLECTOR_PID"
        echo "📄 로그: $LOG_FILE"
        echo "📦 배치 크기: $BATCH_SIZE"
        [ -n "$MAX_BATCHES" ] && echo "🔢 최대 배치: $MAX_BATCHES" || echo "♾️  무한 반복"
        echo ""
        echo "💡 모니터링: tail -f $LOG_FILE"
        echo "⏹️  중단: kill $COLLECTOR_PID"
        echo ""
        ;;
    
    3)
        echo ""
        echo -e "${BLUE}📊 실시간 모니터링 대시보드 시작...${NC}"
        echo "   (Ctrl+C로 종료)"
        echo ""
        sleep 1
        .venv/bin/python scripts/monitor_dashboard.py
        ;;
    
    4)
        echo ""
        echo -e "${BLUE}🌐 웹 대시보드 생성 및 자동 열기...${NC}"
        echo ""
        
        # Python으로 대시보드 생성
        .venv/bin/python << 'PYTHON_SCRIPT'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from scripts.parallel_collector import create_web_dashboard

project_root = Path.cwd()
html_file = project_root / "dashboard.html"
create_web_dashboard(html_file)
print(f"✅ 대시보드 생성: {html_file}")
print(f"📍 URL: {html_file.as_uri()}")
PYTHON_SCRIPT
        
        # macOS에서 기본 브라우저로 열기
        if [ -f "dashboard.html" ]; then
            echo ""
            echo -e "${GREEN}🚀 브라우저에서 대시보드를 엽니다...${NC}"
            open "dashboard.html"
            sleep 1
            echo ""
            echo "✅ 브라우저에서 예쁜 대시보드가 열렸습니다!"
            echo "   (5초마다 자동 새로고침)"
        fi
        ;;
    
    5)
        echo ""
        echo -e "${BLUE}📓 Jupyter Lab 시작...${NC}"
        echo ""
        
        # macOS에서 새 터미널 탭 열기
        if [[ "$OSTYPE" == "darwin"* ]]; then
            osascript -e "tell application \"Terminal\"
                do script \"cd '$PROJECT_ROOT' && source .venv/bin/activate && jupyter lab\"
            end tell"
            echo "✅ Jupyter Lab이 새 터미널 탭에서 실행되었습니다!"
            echo "   브라우저에서 http://localhost:8888 접속"
            echo "   (토큰은 터미널 탭에서 확인)"
        else
            # Linux/Unix
            nohup .venv/bin/jupyter lab > logs/jupyter_$(date +%Y%m%d_%H%M%S).log 2>&1 &
            JUPYTER_PID=$!
            echo "✅ Jupyter Lab 백그라운드 실행 (PID: $JUPYTER_PID)"
            echo "   브라우저에서 http://localhost:8888 접속"
        fi
        echo ""
        ;;
    
    6)
        echo ""
        echo -e "${BLUE}🎯 대화형 Python 메뉴...${NC}"
        echo ""
        .venv/bin/python scripts/parallel_collector.py
        ;;
    
    7)
        echo ""
        echo -e "${BLUE}📊 수집 결과 확인...${NC}"
        echo ""
        
        for file in data/parallel_collected_*.csv; do
            if [ -f "$file" ]; then
                echo "📄 $(basename "$file")"
                ROW_COUNT=$(tail -n +2 "$file" | wc -l | xargs)
                echo "   논문 수: ${ROW_COUNT}개"
                echo ""
            fi
        done
        ;;
    
    8)
        echo ""
        echo -e "${BLUE}🔍 실행 중인 프로세스...${NC}"
        echo ""
        
        echo "병렬 수집 프로세스:"
        ps aux | grep "parallel_collector.py" | grep -v grep || echo "   없음"
        echo ""
        
        echo "모니터링 프로세스:"
        ps aux | grep "monitor_dashboard.py" | grep -v grep || echo "   없음"
        echo ""
        
        echo "Jupyter Lab 프로세스:"
        ps aux | grep "jupyter-lab" | grep -v grep || echo "   없음"
        echo ""
        ;;
    
    9)
        echo ""
        echo -e "${YELLOW}⚠️  모든 백그라운드 작업 종료 중...${NC}"
        echo ""
        
        pkill -f "parallel_collector.py"
        pkill -f "monitor_dashboard.py"
        pkill -f "auto_data_collector.py"
        pkill -f "jupyter-lab"
        
        echo "✅ 종료 완료"
        echo ""
        ;;
    
    0)
        echo ""
        echo "👋 프로그램을 종료합니다."
        echo ""
        exit 0
        ;;
    
    *)
        echo ""
        echo "❌ 잘못된 선택입니다."
        echo ""
        ;;
esac

# 메뉴로 돌아가기
echo ""
read -p "⏸️  Enter를 눌러 메뉴로 돌아가기..."
exec "$0"
