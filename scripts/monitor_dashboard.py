#!/usr/bin/env python3
"""
실시간 모니터링 대시보드
수집 진행 상황을 실시간으로 모니터링
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def clear_screen():
    """화면 지우기"""
    import os
    os.system('clear' if os.name == 'posix' else 'cls')


def monitor_collection(data_dir: Path, interval: int = 5):
    """
    수집 진행 상황 모니터링
    
    Args:
        data_dir: 데이터 디렉토리
        interval: 갱신 주기 (초)
    """
    collected_path = data_dir / "literature_data_collected.csv"
    queue_path = data_dir / "papers_queue.txt"
    log_dir = project_root / "logs"
    
    print("🚀 실시간 모니터링 시작...")
    print("(Ctrl+C로 종료)\n")
    
    try:
        while True:
            clear_screen()
            
            # 헤더
            print("=" * 80)
            print(f"📊 CsPbCl3 데이터 수집 모니터링 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            print()
            
            # 수집된 데이터 통계
            if collected_path.exists():
                df = pd.read_csv(collected_path)
                n_collected = len(df)
                
                print(f"✅ 수집 완료: {n_collected}개")
                
                if n_collected > 0:
                    # 최근 수집 항목
                    recent = df.tail(5)
                    print(f"\n📋 최근 수집 (최근 5개):")
                    for _, row in recent.iterrows():
                        print(f"   - {row.get('paper_id', 'N/A')}: {row.get('doi', 'N/A')}")
            else:
                print("⏳ 수집된 데이터 없음")
            
            print()
            
            # 큐 상태
            if queue_path.exists():
                lines = queue_path.read_text().strip().split('\n')
                papers = [line for line in lines if line.strip() and not line.startswith('#')]
                n_queue = len(papers)
                
                print(f"📥 대기 중: {n_queue}개")
                
                if n_queue > 0:
                    print(f"\n📝 다음 수집 예정 (최대 5개):")
                    for i, paper in enumerate(papers[:5], 1):
                        print(f"   {i}. {paper}")
                else:
                    print("   ℹ️  큐가 비어있습니다. papers_queue.txt에 DOI 추가하세요.")
            else:
                print("⚠️  큐 파일 없음")
            
            print()
            
            # 로그 파일 확인
            if log_dir.exists():
                log_files = sorted(log_dir.glob("data_collector_*.log"), reverse=True)
                if log_files:
                    latest_log = log_files[0]
                    log_lines = latest_log.read_text().strip().split('\n')
                    
                    print(f"📄 최근 로그 ({latest_log.name}):")
                    for line in log_lines[-5:]:
                        if line.strip():
                            print(f"   {line[:100]}")
            
            print()
            print("=" * 80)
            print(f"⏱️  {interval}초 후 갱신... (Ctrl+C로 종료)")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n👋 모니터링 종료")


def main():
    data_dir = project_root / "data"
    monitor_collection(data_dir, interval=5)


if __name__ == "__main__":
    main()
