#!/usr/bin/env python3
"""
실시간 모니터링 대시보드 (업그레이드!)
병렬 수집 작업의 진행 상황을 시각적으로 표시
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import glob
import subprocess

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ANSI 색상 코드
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """화면 지우기"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_progress_bar(current, total, width=50):
    """프로그레스 바"""
    filled = int(width * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (width - filled)
    percentage = (current / total * 100) if total > 0 else 0
    return f"{bar} {percentage:.1f}%"

def format_time_ago(dt):
    """시간 차이를 인간 친화적으로 표시"""
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(seconds=60):
        return f"{int(diff.total_seconds())}초 전"
    elif diff < timedelta(minutes=60):
        return f"{int(diff.total_seconds() / 60)}분 전"
    else:
        return f"{int(diff.total_seconds() / 3600)}시간 전"

def get_running_processes():
    """실행 중인 병렬 수집 프로세스"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = []
        for line in result.stdout.split('\n'):
            if 'parallel_collector.py' in line and 'grep' not in line:
                processes.append(line)
        return processes
    except:
        return []

def get_collected_files(data_dir):
    """수집된 파일 목록 (parallel_collected_*.csv)"""
    pattern = str(data_dir / "parallel_collected_*.csv")
    files = glob.glob(pattern)
    return sorted(files, key=os.path.getmtime, reverse=True)

def monitor_collection(data_dir: Path, interval: int = 5):
    """
    수집 진행 상황 모니터링 (업그레이드!)
    
    Args:
        data_dir: 데이터 디렉토리
        interval: 갱신 주기 (초)
    """
    collected_path = data_dir / "literature_data_collected.csv"
    queue_path = data_dir / "papers_queue.txt"
    log_dir = project_root / "logs"
    
    print(f"{Colors.OKGREEN}🚀 실시간 모니터링 시작...{Colors.ENDC}")
    print(f"{Colors.OKCYAN}(Ctrl+C로 종료){Colors.ENDC}\n")
    
    try:
        while True:
            clear_screen()
            
            # 헤더
            print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}🚀 병렬 데이터 수집 시스템 - 실시간 모니터링{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
            print()
            
            # 프로세스 상태
            processes = get_running_processes()
            print(f"{Colors.BOLD}📊 프로세스 상태{Colors.ENDC}")
            print("─" * 80)
            
            if processes:
                print(f"{Colors.OKGREEN}✅ 실행 중: {len(processes)}개 프로세스{Colors.ENDC}")
                for proc in processes[:2]:
                    parts = proc.split()
                    if len(parts) > 10:
                        print(f"   PID: {parts[1]}, CPU: {parts[2]}%, MEM: {parts[3]}%")
            else:
                print(f"{Colors.WARNING}⚠️  실행 중인 프로세스 없음{Colors.ENDC}")
            print()
            
            # 병렬 수집 파일 상태
            collected_files = get_collected_files(data_dir)
            print(f"{Colors.BOLD}📂 병렬 수집 결과{Colors.ENDC}")
            print("─" * 80)
            
            total_papers = 0
            total_pdf = 0
            total_data = 0
            
            if collected_files:
                print(f"   총 {len(collected_files)}개 배치\n")
                
                for file_path in collected_files[:3]:  # 최신 3개
                    try:
                        df = pd.read_csv(file_path)
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        time_ago = format_time_ago(mtime)
                        
                        has_pdf = sum(df.get('Cl_source', pd.Series()).notna())
                        has_data = sum(df.get('size_nm', pd.Series()).notna())
                        
                        total_papers += len(df)
                        total_pdf += has_pdf
                        total_data += has_data
                        
                        print(f"   {Colors.OKGREEN}✓{Colors.ENDC} {Path(file_path).name}")
                        print(f"     논문: {len(df)}개 | PDF: {has_pdf}개 | 데이터: {has_data}개 | {time_ago}")
                    except:
                        pass
                
                print()
                print(f"{Colors.BOLD}📊 누적 통계{Colors.ENDC}")
                print("─" * 80)
                print(f"   총 논문: {Colors.OKGREEN}{total_papers}개{Colors.ENDC}")
                print(f"   PDF 확보: {Colors.OKGREEN}{total_pdf}개{Colors.ENDC} ({total_pdf/total_papers*100 if total_papers > 0 else 0:.1f}%)")
                print(f"   데이터 추출: {Colors.OKGREEN}{total_data}개{Colors.ENDC} ({total_data/total_papers*100 if total_papers > 0 else 0:.1f}%)")
                print()
                print(f"   진행률: {print_progress_bar(total_papers, 60, 60)}")
            else:
                print(f"   {Colors.WARNING}아직 수집된 배치가 없습니다.{Colors.ENDC}")
            
            print()
            
            # 큐 상태
            if queue_path.exists():
                lines = queue_path.read_text().strip().split('\n')
                papers = [line for line in lines if line.strip() and not line.startswith('#')]
                n_queue = len(papers)
                
                print(f"{Colors.BOLD}📋 작업 큐{Colors.ENDC}")
                print("─" * 80)
                print(f"   대기 중: {Colors.OKCYAN}{n_queue}개 DOI{Colors.ENDC}")
                
                if n_queue > 0 and n_queue <= 5:
                    print(f"\n   다음 수집 예정:")
                    for i, paper in enumerate(papers[:5], 1):
                        print(f"      {i}. {paper}")
            
            print()
            
            # 참고 데이터
            ref_file = data_dir / "reference_dataset.xlsx"
            if ref_file.exists():
                print(f"{Colors.BOLD}📚 참고 데이터{Colors.ENDC}")
                print("─" * 80)
                print(f"   {Colors.OKGREEN}✓{Colors.ENDC} reference_dataset.xlsx: 101 샘플")
                print()
            
            # 하단
            print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}💡 {interval}초마다 자동 새로고침 | Ctrl+C로 종료{Colors.ENDC}")
            print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.OKGREEN}✅ 모니터링 종료{Colors.ENDC}\n")


def main():
    data_dir = project_root / "data"
    monitor_collection(data_dir, interval=5)


if __name__ == "__main__":
    main()
