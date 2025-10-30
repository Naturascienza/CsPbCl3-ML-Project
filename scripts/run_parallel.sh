#!/bin/bash
# 병렬 실행 스크립트 - 데이터 수집과 분석을 동시에 실행

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}🚀 CsPbCl3 ML Project - 병렬 자동화 시작${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

# 프로젝트 루트 디렉토리
PROJECT_DIR="/Users/sungwookpark/Library/CloudStorage/OneDrive-개인/Tools_Coding/CsPbCl3-ML-Project"
cd "$PROJECT_DIR" || exit

# 가상환경 활성화
source .venv/bin/activate

# 로그 디렉토리 생성
mkdir -p logs

# PID 파일 디렉토리
mkdir -p .pids

echo -e "${GREEN}✅ 환경 설정 완료${NC}"
echo ""

# 기능 1: 데이터 수집기 (백그라운드)
function start_collector() {
    echo -e "${YELLOW}📥 데이터 수집기 시작...${NC}"
    
    # 백그라운드 실행
    python scripts/auto_data_collector.py > logs/collector_output.log 2>&1 &
    COLLECTOR_PID=$!
    echo $COLLECTOR_PID > .pids/collector.pid
    
    echo -e "${GREEN}   ✅ 데이터 수집기 실행 (PID: $COLLECTOR_PID)${NC}"
    echo -e "      로그: logs/collector_output.log"
    echo ""
}

# 기능 2: 모니터링 대시보드 (별도 터미널)
function start_monitor() {
    echo -e "${YELLOW}📊 모니터링 대시보드 시작...${NC}"
    
    # macOS에서 새 터미널 탭 열기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell application \"Terminal\"
            do script \"cd '$PROJECT_DIR' && source .venv/bin/activate && python scripts/monitor_dashboard.py\"
        end tell"
        echo -e "${GREEN}   ✅ 모니터링 새 터미널 탭에서 실행${NC}"
    else
        # Linux/Unix
        python scripts/monitor_dashboard.py > logs/monitor_output.log 2>&1 &
        MONITOR_PID=$!
        echo $MONITOR_PID > .pids/monitor.pid
        echo -e "${GREEN}   ✅ 모니터링 백그라운드 실행 (PID: $MONITOR_PID)${NC}"
    fi
    echo ""
}

# 기능 3: Jupyter Lab (별도 터미널)
function start_jupyter() {
    echo -e "${YELLOW}📓 Jupyter Lab 시작...${NC}"
    
    # macOS에서 새 터미널 탭 열기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell application \"Terminal\"
            do script \"cd '$PROJECT_DIR' && source .venv/bin/activate && jupyter lab\"
        end tell"
        echo -e "${GREEN}   ✅ Jupyter Lab 새 터미널 탭에서 실행${NC}"
    else
        jupyter lab > logs/jupyter_output.log 2>&1 &
        JUPYTER_PID=$!
        echo $JUPYTER_PID > .pids/jupyter.pid
        echo -e "${GREEN}   ✅ Jupyter Lab 백그라운드 실행 (PID: $JUPYTER_PID)${NC}"
    fi
    echo ""
}

# 중지 함수
function stop_all() {
    echo -e "${RED}⛔ 모든 프로세스 중지 중...${NC}"
    
    if [ -f .pids/collector.pid ]; then
        COLLECTOR_PID=$(cat .pids/collector.pid)
        kill $COLLECTOR_PID 2>/dev/null
        echo -e "${GREEN}   ✅ 데이터 수집기 중지 (PID: $COLLECTOR_PID)${NC}"
        rm .pids/collector.pid
    fi
    
    if [ -f .pids/monitor.pid ]; then
        MONITOR_PID=$(cat .pids/monitor.pid)
        kill $MONITOR_PID 2>/dev/null
        echo -e "${GREEN}   ✅ 모니터링 중지 (PID: $MONITOR_PID)${NC}"
        rm .pids/monitor.pid
    fi
    
    if [ -f .pids/jupyter.pid ]; then
        JUPYTER_PID=$(cat .pids/jupyter.pid)
        kill $JUPYTER_PID 2>/dev/null
        echo -e "${GREEN}   ✅ Jupyter Lab 중지 (PID: $JUPYTER_PID)${NC}"
        rm .pids/jupyter.pid
    fi
    
    echo ""
    echo -e "${GREEN}✅ 모든 프로세스 중지 완료${NC}"
}

# 상태 확인
function show_status() {
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${BLUE}📊 프로세스 상태${NC}"
    echo -e "${BLUE}=====================================================================${NC}"
    echo ""
    
    if [ -f .pids/collector.pid ]; then
        COLLECTOR_PID=$(cat .pids/collector.pid)
        if ps -p $COLLECTOR_PID > /dev/null; then
            echo -e "${GREEN}✅ 데이터 수집기: 실행 중 (PID: $COLLECTOR_PID)${NC}"
        else
            echo -e "${RED}❌ 데이터 수집기: 중지됨${NC}"
        fi
    else
        echo -e "${YELLOW}⏸️  데이터 수집기: 시작 안 됨${NC}"
    fi
    
    echo ""
    
    # 수집 통계
    if [ -f data/literature_data_collected.csv ]; then
        N_COLLECTED=$(tail -n +2 data/literature_data_collected.csv | wc -l | xargs)
        echo -e "   📥 수집된 데이터: ${GREEN}${N_COLLECTED}개${NC}"
    fi
    
    if [ -f data/papers_queue.txt ]; then
        N_QUEUE=$(grep -v '^#' data/papers_queue.txt | grep -v '^$' | wc -l | xargs)
        echo -e "   📋 대기 중: ${YELLOW}${N_QUEUE}개${NC}"
    fi
    
    echo ""
}

# 메인 메뉴
function main_menu() {
    while true; do
        echo ""
        echo -e "${BLUE}=====================================================================${NC}"
        echo -e "${BLUE}메뉴${NC}"
        echo -e "${BLUE}=====================================================================${NC}"
        echo "  1) 데이터 수집기 시작 (백그라운드)"
        echo "  2) 모니터링 대시보드 시작 (새 터미널)"
        echo "  3) Jupyter Lab 시작 (새 터미널)"
        echo "  4) 모두 시작 (추천!)"
        echo "  5) 상태 확인"
        echo "  6) 모두 중지"
        echo "  7) 종료"
        echo ""
        read -p "선택 (1-7): " choice
        
        case $choice in
            1) start_collector ;;
            2) start_monitor ;;
            3) start_jupyter ;;
            4)
                start_collector
                sleep 2
                start_monitor
                sleep 2
                start_jupyter
                echo ""
                echo -e "${GREEN}🎉 모든 프로세스 시작 완료!${NC}"
                echo ""
                echo -e "${YELLOW}📌 작업 방법:${NC}"
                echo "  - 터미널 1 (현재): 이 스크립트 실행 중"
                echo "  - 터미널 2: 모니터링 대시보드 (실시간 통계)"
                echo "  - 터미널 3: Jupyter Lab (분석 작업)"
                echo "  - 백그라운드: 데이터 수집기 (자동 수집)"
                echo ""
                ;;
            5) show_status ;;
            6) stop_all ;;
            7)
                echo -e "${YELLOW}종료 전 실행 중인 프로세스를 중지할까요? (y/n)${NC}"
                read -p "> " confirm
                if [ "$confirm" = "y" ]; then
                    stop_all
                fi
                echo -e "${BLUE}👋 종료합니다${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 잘못된 선택입니다${NC}"
                ;;
        esac
    done
}

# 트랩 설정 (Ctrl+C)
trap 'echo ""; echo "⚠️  Ctrl+C 감지. 메뉴로 돌아갑니다..."; echo ""' INT

# 시작
main_menu
