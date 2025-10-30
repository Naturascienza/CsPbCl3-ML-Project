#!/usr/bin/env python3
"""
자동 데이터 수집 스크립트 (무한 루프)
백그라운드에서 실행하면서 문헌 데이터를 지속적으로 수집
"""

import time
import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'data_collector_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoDataCollector:
    """자동 데이터 수집기"""
    
    def __init__(self, data_dir: Path, interval: int = 300):
        """
        Args:
            data_dir: 데이터 저장 디렉토리
            interval: 수집 주기 (초) - 기본 5분
        """
        self.data_dir = data_dir
        self.interval = interval
        self.template_path = data_dir / "literature_data_template.csv"
        self.collected_path = data_dir / "literature_data_collected.csv"
        self.queue_path = data_dir / "papers_queue.txt"
        
        # 수집 통계
        self.stats = {
            'total_collected': 0,
            'success': 0,
            'failed': 0,
            'start_time': datetime.now()
        }
    
    def initialize(self):
        """초기화"""
        logger.info("=" * 80)
        logger.info("🚀 자동 데이터 수집기 시작")
        logger.info(f"📂 데이터 디렉토리: {self.data_dir}")
        logger.info(f"⏱️  수집 주기: {self.interval}초 ({self.interval/60:.1f}분)")
        logger.info("=" * 80)
        
        # 수집된 데이터 파일 초기화
        if not self.collected_path.exists():
            # 템플릿 복사
            if self.template_path.exists():
                df_template = pd.read_csv(self.template_path)
                df_template.iloc[0:0].to_csv(self.collected_path, index=False)
                logger.info(f"✅ 수집 파일 초기화: {self.collected_path}")
        
        # 논문 큐 파일 생성
        if not self.queue_path.exists():
            self.queue_path.write_text("# Papers to collect (one DOI per line)\n")
            logger.info(f"✅ 논문 큐 파일 생성: {self.queue_path}")
    
    def check_queue(self):
        """큐에 새로운 논문이 있는지 확인"""
        if not self.queue_path.exists():
            return []
        
        lines = self.queue_path.read_text().strip().split('\n')
        papers = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        
        return papers
    
    def collect_from_doi(self, doi: str):
        """DOI로부터 데이터 수집 (시뮬레이션)"""
        logger.info(f"📥 수집 시작: {doi}")
        
        # 실제로는 여기서 CrossRef API, Web scraping 등 수행
        # 지금은 시뮬레이션
        time.sleep(2)  # API 호출 시뮬레이션
        
        # 더미 데이터 생성
        data = {
            'paper_id': f"P{self.stats['total_collected'] + 1:03d}",
            'doi': doi,
            'year': 2024,
            'authors': 'Auto-collected',
            'journal': 'Automated Collection',
            # ... 나머지 필드들
        }
        
        return data
    
    def save_collected_data(self, data: dict):
        """수집한 데이터 저장"""
        df = pd.DataFrame([data])
        
        # 기존 데이터에 추가
        if self.collected_path.exists():
            df_existing = pd.read_csv(self.collected_path)
            df_combined = pd.concat([df_existing, df], ignore_index=True)
            df_combined.to_csv(self.collected_path, index=False)
        else:
            df.to_csv(self.collected_path, index=False)
        
        logger.info(f"💾 데이터 저장 완료: {data['paper_id']}")
    
    def remove_from_queue(self, doi: str):
        """큐에서 처리된 논문 제거"""
        if not self.queue_path.exists():
            return
        
        lines = self.queue_path.read_text().strip().split('\n')
        remaining = [line for line in lines if line.strip() != doi]
        
        self.queue_path.write_text('\n'.join(remaining))
        logger.info(f"✅ 큐에서 제거: {doi}")
    
    def print_stats(self):
        """통계 출력"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        logger.info("=" * 80)
        logger.info("📊 수집 통계")
        logger.info(f"  총 수집: {self.stats['total_collected']}개")
        logger.info(f"  성공: {self.stats['success']}개")
        logger.info(f"  실패: {self.stats['failed']}개")
        logger.info(f"  실행 시간: {elapsed/3600:.2f}시간")
        logger.info(f"  평균 속도: {self.stats['total_collected']/(elapsed/3600):.1f}개/시간")
        logger.info("=" * 80)
    
    def run_once(self):
        """1회 수집 실행"""
        papers = self.check_queue()
        
        if not papers:
            logger.info("⏸️  큐가 비어있습니다. 새 논문을 papers_queue.txt에 추가하세요.")
            return False
        
        logger.info(f"📋 큐에 {len(papers)}개 논문 대기 중")
        
        # 첫 번째 논문 처리
        doi = papers[0]
        
        try:
            # 데이터 수집
            data = self.collect_from_doi(doi)
            
            # 저장
            self.save_collected_data(data)
            
            # 큐에서 제거
            self.remove_from_queue(doi)
            
            # 통계 업데이트
            self.stats['total_collected'] += 1
            self.stats['success'] += 1
            
            logger.info(f"✅ 수집 완료: {doi}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 수집 실패: {doi} - {e}")
            self.stats['failed'] += 1
            return False
    
    def run_forever(self):
        """무한 루프 실행"""
        self.initialize()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                logger.info(f"\n🔄 Cycle {cycle} 시작")
                
                # 1회 수집
                success = self.run_once()
                
                # 통계 출력 (10회마다)
                if cycle % 10 == 0:
                    self.print_stats()
                
                # 대기
                if success:
                    logger.info(f"⏳ {self.interval}초 대기 중...")
                    time.sleep(self.interval)
                else:
                    # 큐가 비었을 때는 더 길게 대기
                    wait_time = self.interval * 3
                    logger.info(f"⏳ {wait_time}초 대기 중...")
                    time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("\n\n⛔ 사용자에 의해 중단됨")
            self.print_stats()
            logger.info("👋 수집기 종료")
        
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {e}")
            self.print_stats()
            raise


def main():
    """메인 함수"""
    # 설정
    data_dir = project_root / "data"
    interval = int(os.getenv("COLLECTION_INTERVAL", "300"))  # 기본 5분
    
    # 수집기 생성 및 실행
    collector = AutoDataCollector(data_dir, interval)
    collector.run_forever()


if __name__ == "__main__":
    main()
