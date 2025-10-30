#!/usr/bin/env python3
"""
Python multiprocessing을 사용한 병렬 실행
데이터 수집과 분석을 별도 프로세스로 실행
"""

import multiprocessing as mp
import time
import sys
from pathlib import Path
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_logging(name: str):
    """로깅 설정"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러
    fh = logging.FileHandler(
        log_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    fh.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - [%(processName)s] - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def data_collector_worker(queue: mp.Queue, stop_event: mp.Event):
    """
    데이터 수집 워커 (별도 프로세스)
    
    Args:
        queue: 메시지 큐 (수집 통계 전송)
        stop_event: 종료 이벤트
    """
    logger = setup_logging("collector")
    logger.info("🚀 데이터 수집 프로세스 시작")
    
    collected_count = 0
    
    try:
        while not stop_event.is_set():
            # 수집 작업 시뮬레이션
            logger.info(f"📥 데이터 수집 중... (총 {collected_count}개)")
            
            # 실제로는 여기서 CrossRef API, Web scraping 등 수행
            time.sleep(5)  # 5초마다 수집
            
            collected_count += 1
            
            # 통계를 큐로 전송
            queue.put({
                'type': 'collection',
                'count': collected_count,
                'timestamp': datetime.now()
            })
            
            # 10개마다 요약
            if collected_count % 10 == 0:
                logger.info(f"✅ {collected_count}개 수집 완료")
    
    except KeyboardInterrupt:
        logger.info("⛔ 수집 프로세스 중단")
    
    finally:
        logger.info(f"👋 수집 프로세스 종료 (총 {collected_count}개 수집)")


def feature_engineering_worker(queue: mp.Queue, stop_event: mp.Event):
    """
    Feature engineering 워커 (별도 프로세스)
    
    Args:
        queue: 메시지 큐
        stop_event: 종료 이벤트
    """
    logger = setup_logging("feature_engineering")
    logger.info("🚀 Feature Engineering 프로세스 시작")
    
    processed_count = 0
    
    try:
        while not stop_event.is_set():
            logger.info(f"🔧 Feature engineering 중... (총 {processed_count}개)")
            
            # 실제로는 여기서 physics-informed features 계산
            time.sleep(10)  # 10초마다 처리
            
            processed_count += 1
            
            # 통계 전송
            queue.put({
                'type': 'feature_engineering',
                'count': processed_count,
                'timestamp': datetime.now()
            })
            
            if processed_count % 5 == 0:
                logger.info(f"✅ {processed_count}개 처리 완료")
    
    except KeyboardInterrupt:
        logger.info("⛔ Feature engineering 프로세스 중단")
    
    finally:
        logger.info(f"👋 Feature engineering 종료 (총 {processed_count}개 처리)")


def model_training_worker(queue: mp.Queue, stop_event: mp.Event):
    """
    모델 학습 워커 (별도 프로세스)
    
    Args:
        queue: 메시지 큐
        stop_event: 종료 이벤트
    """
    logger = setup_logging("model_training")
    logger.info("🚀 모델 학습 프로세스 시작")
    
    training_iterations = 0
    
    try:
        while not stop_event.is_set():
            logger.info(f"🤖 모델 학습 중... (반복 {training_iterations}회)")
            
            # 실제로는 여기서 모델 학습
            time.sleep(30)  # 30초마다 재학습
            
            training_iterations += 1
            
            # 통계 전송
            queue.put({
                'type': 'model_training',
                'iterations': training_iterations,
                'timestamp': datetime.now()
            })
            
            logger.info(f"✅ 학습 반복 {training_iterations}회 완료")
    
    except KeyboardInterrupt:
        logger.info("⛔ 모델 학습 프로세스 중단")
    
    finally:
        logger.info(f"👋 모델 학습 종료 (총 {training_iterations}회)")


def monitoring_worker(queue: mp.Queue, stop_event: mp.Event):
    """
    모니터링 워커 (메인 프로세스)
    
    Args:
        queue: 메시지 큐 (다른 워커들의 통계 수신)
        stop_event: 종료 이벤트
    """
    logger = setup_logging("monitor")
    logger.info("🚀 모니터링 프로세스 시작")
    
    stats = {
        'collection': 0,
        'feature_engineering': 0,
        'model_training': 0
    }
    
    try:
        while not stop_event.is_set():
            # 큐에서 메시지 수신
            if not queue.empty():
                msg = queue.get()
                
                if msg['type'] == 'collection':
                    stats['collection'] = msg['count']
                elif msg['type'] == 'feature_engineering':
                    stats['feature_engineering'] = msg['count']
                elif msg['type'] == 'model_training':
                    stats['model_training'] = msg['iterations']
                
                # 통계 출력
                logger.info("=" * 80)
                logger.info("📊 실시간 통계")
                logger.info(f"  📥 수집: {stats['collection']}개")
                logger.info(f"  🔧 Feature Engineering: {stats['feature_engineering']}개")
                logger.info(f"  🤖 모델 학습: {stats['model_training']}회")
                logger.info("=" * 80)
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("⛔ 모니터링 중단")
    
    finally:
        logger.info("👋 모니터링 종료")


def main():
    """메인 함수"""
    print("=" * 80)
    print("🚀 CsPbCl3 ML Project - 병렬 자동화 시작")
    print("=" * 80)
    print()
    
    # 멀티프로세싱 설정
    mp.set_start_method('spawn', force=True)
    
    # 공유 큐 및 이벤트
    queue = mp.Queue()
    stop_event = mp.Event()
    
    # 프로세스 생성
    processes = [
        mp.Process(target=data_collector_worker, args=(queue, stop_event), name="DataCollector"),
        mp.Process(target=feature_engineering_worker, args=(queue, stop_event), name="FeatureEngineering"),
        mp.Process(target=model_training_worker, args=(queue, stop_event), name="ModelTraining"),
    ]
    
    # 프로세스 시작
    print("🚀 워커 프로세스 시작 중...")
    for p in processes:
        p.start()
        print(f"   ✅ {p.name} 시작 (PID: {p.pid})")
    
    print()
    print("✅ 모든 워커 시작 완료")
    print()
    print("💡 Ctrl+C로 모든 프로세스 중지")
    print("=" * 80)
    print()
    
    try:
        # 모니터링 (메인 프로세스)
        monitoring_worker(queue, stop_event)
    
    except KeyboardInterrupt:
        print("\n\n⛔ 종료 신호 감지")
        print("📌 모든 워커 프로세스 중지 중...")
        
        # 종료 이벤트 설정
        stop_event.set()
        
        # 프로세스 종료 대기
        for p in processes:
            p.join(timeout=5)
            if p.is_alive():
                print(f"   ⚠️  {p.name} 강제 종료")
                p.terminate()
            else:
                print(f"   ✅ {p.name} 정상 종료")
        
        print()
        print("👋 모든 프로세스 종료 완료")


if __name__ == "__main__":
    main()
