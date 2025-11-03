#!/usr/bin/env python3
"""
병렬 데이터 수집 시스템
4개의 워커가 동시에 PDF 다운로드 + 데이터 추출
완전 headless 모드로 화면 방해 없음
자동 큐 재충전 기능 포함
"""

import multiprocessing as mp
from multiprocessing import Queue, Process, Manager
import time
from pathlib import Path
import logging
from datetime import datetime
import sys
import subprocess

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.pdf_data_extractor import PDFDataExtractor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Worker-%(process)d] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParallelCollector:
    """병렬 데이터 수집기"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.project_root = Path(__file__).parent.parent
        self.queue_file = self.project_root / "data" / "papers_queue.txt"
        self.pdf_dir = self.project_root / "pdf" / "downloaded"
        self.results_dir = self.project_root / "data"
        
    def load_queue(self):
        """큐에서 DOI 로드"""
        if not self.queue_file.exists():
            return []
        
        lines = self.queue_file.read_text().strip().split('\n')
        dois = [line.strip() for line in lines 
                if line.strip() and not line.startswith('#')]
        
        return dois
    
    def worker(self, worker_id: int, task_queue: Queue, result_queue: Queue):
        """
        워커 프로세스
        
        Args:
            worker_id: 워커 ID
            task_queue: 작업 큐 (DOI 입력)
            result_queue: 결과 큐 (성공/실패 출력)
        """
        logger.info(f"🚀 워커 {worker_id} 시작")
        
        # 각 워커마다 별도의 PDF 디렉토리
        worker_pdf_dir = self.pdf_dir / f"worker_{worker_id}"
        worker_pdf_dir.mkdir(exist_ok=True, parents=True)
        
        # PDF 추출기 초기화 (Selenium headless)
        try:
            extractor = PDFDataExtractor(worker_pdf_dir, use_selenium=True)
            logger.info(f"✅ 워커 {worker_id}: PDF 추출기 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 워커 {worker_id}: 초기화 실패 - {str(e)}")
            return
        
        processed = 0
        
        while True:
            try:
                # 큐에서 DOI 가져오기 (타임아웃 5초)
                doi = task_queue.get(timeout=5)
                
                if doi is None:  # 종료 신호
                    logger.info(f"🛑 워커 {worker_id} 종료 (처리: {processed}개)")
                    break
                
                logger.info(f"📥 워커 {worker_id}: {doi} 처리 시작")
                
                # PDF 다운로드 + 데이터 추출
                paper_id = f"W{worker_id}_P{processed+1:03d}"
                
                try:
                    data = extractor.extract_all_data(doi, paper_id)
                    
                    if data:
                        logger.info(f"✅ 워커 {worker_id}: {doi} 성공")
                        result_queue.put({
                            'worker_id': worker_id,
                            'doi': doi,
                            'status': 'success',
                            'data': data
                        })
                    else:
                        logger.warning(f"⚠️ 워커 {worker_id}: {doi} 데이터 없음")
                        result_queue.put({
                            'worker_id': worker_id,
                            'doi': doi,
                            'status': 'no_data',
                            'data': None
                        })
                    
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"❌ 워커 {worker_id}: {doi} 실패 - {str(e)}")
                    result_queue.put({
                        'worker_id': worker_id,
                        'doi': doi,
                        'status': 'error',
                        'error': str(e)
                    })
                
            except Queue.Empty:
                # 큐가 비어있음 - 더 기다림
                continue
            except KeyboardInterrupt:
                logger.info(f"⚠️ 워커 {worker_id} 중단됨")
                break
            except Exception as e:
                logger.error(f"❌ 워커 {worker_id} 오류: {str(e)}")
                break
        
        # 정리
        try:
            extractor.cleanup()
        except:
            pass
    
    def run(self):
        """병렬 수집 실행"""
        print("=" * 80)
        print("🚀 병렬 데이터 수집 시스템")
        print("=" * 80)
        
        # DOI 큐 로드
        dois = self.load_queue()
        
        if not dois:
            print("❌ 큐에 DOI가 없습니다.")
            return
        
        print(f"📝 큐: {len(dois)}개 DOI")
        print(f"👷 워커: {self.num_workers}개")
        print(f"⏱️  예상 시간: {len(dois) / self.num_workers * 2:.0f}분")
        print("=" * 80)
        
        # 멀티프로세싱 큐
        manager = Manager()
        task_queue = manager.Queue()
        result_queue = manager.Queue()
        
        # DOI를 작업 큐에 추가
        for doi in dois:
            task_queue.put(doi)
        
        # 종료 신호 추가 (워커 수만큼)
        for _ in range(self.num_workers):
            task_queue.put(None)
        
        # 워커 프로세스 시작
        workers = []
        for i in range(self.num_workers):
            p = Process(
                target=self.worker,
                args=(i+1, task_queue, result_queue)
            )
            p.start()
            workers.append(p)
        
        # 결과 수집
        results = {
            'success': [],
            'no_data': [],
            'error': []
        }
        
        start_time = time.time()
        
        # 진행 상황 모니터링
        while any(w.is_alive() for w in workers):
            # 결과 큐에서 가져오기
            while not result_queue.empty():
                result = result_queue.get()
                status = result['status']
                results[status].append(result)
                
                # 진행 상황 출력
                total_processed = sum(len(v) for v in results.values())
                elapsed = time.time() - start_time
                rate = total_processed / elapsed if elapsed > 0 else 0
                
                print(f"\r📊 진행: {total_processed}/{len(dois)} "
                      f"(성공: {len(results['success'])}, "
                      f"데이터없음: {len(results['no_data'])}, "
                      f"실패: {len(results['error'])}) "
                      f"| 속도: {rate:.2f}개/분", end='')
            
            time.sleep(1)
        
        # 모든 워커 종료 대기
        for w in workers:
            w.join()
        
        # 남은 결과 수집
        while not result_queue.empty():
            result = result_queue.get()
            results[result['status']].append(result)
        
        # 최종 결과
        print(f"\n\n{'=' * 80}")
        print("✅ 수집 완료!")
        print("=" * 80)
        print(f"📊 총 처리: {len(dois)}개")
        print(f"   ✅ 성공: {len(results['success'])}개")
        print(f"   ⚠️ 데이터 없음: {len(results['no_data'])}개")
        print(f"   ❌ 실패: {len(results['error'])}개")
        print(f"⏱️  소요 시간: {(time.time() - start_time)/60:.1f}분")
        print("=" * 80)
        
        # 데이터 저장
        if results['success']:
            self.save_results(results['success'])
    
    
    def auto_refill_queue(self, min_dois: int = 10):
        """
        큐가 부족하면 자동으로 새 DOI 검색
        
        Args:
            min_dois: 최소 필요 DOI 개수
        
        Returns:
            bool: 성공 여부
        """
        logger.info(f"🔍 자동 DOI 검색 시작...")
        print("\n" + "=" * 80)
        print("🔍 큐가 부족합니다. 새 DOI 자동 검색 중...")
        print("=" * 80)
        
        try:
            # auto_doi_search.py 실행
            auto_search_script = self.project_root / "scripts" / "auto_doi_search.py"
            
            if not auto_search_script.exists():
                logger.error("❌ auto_doi_search.py 파일을 찾을 수 없습니다.")
                return False
            
            # Python 스크립트 실행
            result = subprocess.run(
                [sys.executable, str(auto_search_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120  # 2분 타임아웃
            )
            
            if result.returncode == 0:
                logger.info("✅ 새 DOI 검색 완료")
                print("\n✅ 새 DOI가 큐에 추가되었습니다!")
                
                # 새로 추가된 DOI 개수 확인
                new_dois = self.load_queue()
                print(f"📋 현재 큐: {len(new_dois)}개 DOI")
                return True
            else:
                logger.error(f"❌ DOI 검색 실패: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ DOI 검색 타임아웃 (2분 초과)")
            return False
        except Exception as e:
            logger.error(f"❌ DOI 검색 중 오류: {str(e)}")
            return False
    
    
    def run_continuous(self, batch_size: int = 20, max_batches: int = None):
        """
        무한 병렬 수집 (자동 큐 재충전)
        
        Args:
            batch_size: 배치당 처리할 DOI 개수
            max_batches: 최대 배치 수 (None이면 무한)
        """
        print("=" * 80)
        print("🚀 무한 병렬 데이터 수집 시스템 (자동 큐 재충전)")
        print("=" * 80)
        print(f"📦 배치 크기: {batch_size}개")
        print(f"👷 워커: {self.num_workers}개")
        if max_batches:
            print(f"🔢 최대 배치: {max_batches}개")
        else:
            print(f"♾️  무한 반복 (Ctrl+C로 중단)")
        print("=" * 80)
        
        batch_count = 0
        total_collected = 0
        
        try:
            while True:
                batch_count += 1
                
                print(f"\n{'='*80}")
                print(f"📦 배치 #{batch_count} 시작")
                print("="*80)
                
                # 1. 큐 확인
                dois = self.load_queue()
                
                # 2. 큐가 부족하면 자동 재충전
                if not dois or len(dois) < 10:
                    print(f"⚠️ 큐 부족 (현재: {len(dois)}개)")
                    
                    # 자동 DOI 검색
                    if self.auto_refill_queue():
                        dois = self.load_queue()
                    else:
                        print("❌ 새 DOI 검색 실패")
                
                # 3. 여전히 비었으면 종료
                if not dois:
                    print("\n" + "="*80)
                    print("✅ 모든 논문 수집 완료!")
                    print(f"📊 총 배치: {batch_count-1}개")
                    print(f"📚 총 수집: {total_collected}개")
                    print("="*80)
                    break
                
                # 4. 배치 크기만큼만 처리
                batch_dois = dois[:batch_size]
                print(f"📝 이번 배치: {len(batch_dois)}개 DOI 처리")
                
                # 5. 병렬 수집 실행
                self.run_batch(batch_dois)
                total_collected += len(batch_dois)
                
                # 6. 처리된 DOI는 큐에서 제거
                self.remove_processed_dois(batch_dois)
                
                # 7. 최대 배치 수 확인
                if max_batches and batch_count >= max_batches:
                    print(f"\n✅ 최대 배치 수({max_batches})에 도달했습니다.")
                    break
                
                # 8. 다음 배치 전 대기
                print(f"\n⏸️  5초 후 다음 배치 시작...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ 사용자가 중단했습니다.")
            print(f"📊 총 배치: {batch_count}개")
            print(f"📚 총 수집: {total_collected}개")
    
    
    def run_batch(self, dois: list):
        """배치 처리 (run() 메서드 분리)"""
        print(f"⏱️  예상 시간: {len(dois) / self.num_workers * 2:.0f}분")
        
        # 멀티프로세싱 큐
        manager = Manager()
        task_queue = manager.Queue()
        result_queue = manager.Queue()
        
        # DOI를 작업 큐에 추가
        for doi in dois:
            task_queue.put(doi)
        
        # 종료 신호 추가
        for _ in range(self.num_workers):
            task_queue.put(None)
        
        # 워커 프로세스 시작
        workers = []
        for i in range(self.num_workers):
            p = Process(
                target=self.worker,
                args=(i+1, task_queue, result_queue)
            )
            p.start()
            workers.append(p)
        
        # 결과 수집
        results = {
            'success': [],
            'no_data': [],
            'error': []
        }
        
        start_time = time.time()
        
        # 진행 상황 모니터링
        while any(w.is_alive() for w in workers):
            while not result_queue.empty():
                result = result_queue.get()
                status = result['status']
                results[status].append(result)
                
                total_processed = sum(len(v) for v in results.values())
                elapsed = time.time() - start_time
                rate = total_processed / elapsed if elapsed > 0 else 0
                
                print(f"\r📊 진행: {total_processed}/{len(dois)} "
                      f"(성공: {len(results['success'])}, "
                      f"데이터없음: {len(results['no_data'])}, "
                      f"실패: {len(results['error'])}) "
                      f"| 속도: {rate:.2f}개/분", end='')
            
            time.sleep(1)
        
        # 모든 워커 종료 대기
        for w in workers:
            w.join()
        
        # 남은 결과 수집
        while not result_queue.empty():
            result = result_queue.get()
            results[result['status']].append(result)
        
        print(f"\n\n{'=' * 80}")
        print("✅ 배치 완료!")
        print(f"   ✅ 성공: {len(results['success'])}개")
        print(f"   ⚠️ 데이터 없음: {len(results['no_data'])}개")
        print(f"   ❌ 실패: {len(results['error'])}개")
        print(f"⏱️  소요 시간: {(time.time() - start_time)/60:.1f}분")
        
        # 데이터 저장
        if results['success']:
            self.save_results(results['success'])
    
    
    def remove_processed_dois(self, processed_dois: list):
        """
        처리된 DOI를 큐에서 제거
        
        Args:
            processed_dois: 처리 완료된 DOI 리스트
        """
        if not self.queue_file.exists():
            return
        
        # 기존 큐 읽기
        lines = self.queue_file.read_text().strip().split('\n')
        
        # 주석과 빈 줄 유지, 처리된 DOI만 제거
        new_lines = []
        processed_set = set(processed_dois)
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                new_lines.append(line)
            elif line not in processed_set:
                new_lines.append(line)
        
        # 큐 파일 업데이트
        self.queue_file.write_text('\n'.join(new_lines) + '\n')
        logger.info(f"🗑️ {len(processed_dois)}개 DOI를 큐에서 제거")


    def save_results(self, success_results):
        """결과를 CSV로 저장"""
        import pandas as pd
        
        data_list = []
        for result in success_results:
            data_list.append(result['data'])
        
        df = pd.DataFrame(data_list)
        output_file = self.results_dir / f"parallel_collected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"💾 결과 저장: {output_file}")


def show_menu():
    """대화형 메뉴 표시"""
    print("\n" + "="*80)
    print("🚀 CsPbCl3 데이터 마이닝 자동화 시스템")
    print("="*80)
    print("\n📊 현재 상태:")
    
    # 큐 상태
    queue_file = Path(__file__).parent.parent / "data" / "papers_queue.txt"
    if queue_file.exists():
        lines = queue_file.read_text().strip().split('\n')
        dois = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        print(f"   📋 대기 중인 논문: {len(dois)}개")
    else:
        print(f"   ⚠️  큐 파일 없음")
    
    # 수집 파일 상태
    data_dir = Path(__file__).parent.parent / "data"
    collected_files = list(data_dir.glob("parallel_collected_*.csv"))
    if collected_files:
        print(f"   ✅ 수집 완료 배치: {len(collected_files)}개")
    
    # 참고 데이터
    ref_file = data_dir / "reference_dataset.xlsx"
    if ref_file.exists():
        print(f"   📚 참고 데이터: 101 샘플")
    
    print("\n" + "-"*80)
    print("\n어떤 작업을 수행할까요?\n")
    print("   1️⃣  병렬 데이터 수집 (1회, 큐 소진 시 종료)")
    print("   2️⃣  무한 데이터 수집 (자동 큐 재충전) 🔥")
    print("   3️⃣  실시간 모니터링 대시보드")
    print("   4️⃣  웹 대시보드 열기 (브라우저)")
    print("   5️⃣  수집 결과 확인")
    print("   6️⃣  DOI 큐 관리")
    print("   0️⃣  종료")
    print("\n" + "-"*80)
    
    try:
        choice = input("\n👉 선택: ").strip()
        return choice
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 종료합니다.")
        sys.exit(0)


def handle_choice(choice: str):
    """메뉴 선택 처리"""
    import subprocess
    import os
    
    project_root = Path(__file__).parent.parent
    
    if choice == "1":
        print("\n🚀 병렬 데이터 수집을 시작합니다 (1회)...\n")
        num_workers = min(4, mp.cpu_count())
        collector = ParallelCollector(num_workers=num_workers)
        collector.run()
    
    elif choice == "2":
        print("\n🔥 무한 데이터 수집을 시작합니다 (자동 큐 재충전)...\n")
        print("💡 큐가 부족하면 자동으로 새 DOI를 검색합니다.")
        print("⏸️  Ctrl+C로 중단 가능\n")
        
        num_workers = min(4, mp.cpu_count())
        collector = ParallelCollector(num_workers=num_workers)
        
        # 배치 크기 설정
        try:
            batch_size = input("📦 배치 크기 (기본 20개, Enter=기본값): ").strip()
            batch_size = int(batch_size) if batch_size else 20
        except:
            batch_size = 20
        
        # 최대 배치 수 설정
        try:
            max_batches = input("🔢 최대 배치 수 (Enter=무한): ").strip()
            max_batches = int(max_batches) if max_batches else None
        except:
            max_batches = None
        
        collector.run_continuous(batch_size=batch_size, max_batches=max_batches)
        
    elif choice == "3":
        print("\n📊 실시간 모니터링 대시보드를 시작합니다...")
        print("   (Ctrl+C로 종료)\n")
        time.sleep(1)
        
        # Python 실행 파일 경로 (venv 활용)
        python_exe = sys.executable
        monitor_script = project_root / "scripts" / "monitor_dashboard.py"
        
        if monitor_script.exists():
            subprocess.run([python_exe, str(monitor_script)])
        else:
            print("❌ monitor_dashboard.py 파일을 찾을 수 없습니다.")
    
    elif choice == "4":
        print("\n🌐 웹 대시보드를 생성합니다...\n")
        
        # 웹 대시보드 HTML 생성
        html_file = project_root / "dashboard.html"
        create_web_dashboard(html_file)
        
        print(f"✅ 대시보드 생성: {html_file}")
        print("🌐 VS Code Simple Browser에서 자동으로 열기...\n")
        
        # 파일 URI 생성
        file_uri = html_file.as_uri()
        
        # open_simple_browser 도구 사용 안내
        print(f"� 생성된 파일: {html_file}")
        print(f"📍 URL: {file_uri}\n")
        
        # 사용자에게 URL 제공
        print("=" * 80)
        print("💡 아래 URL을 복사해서 브라우저에 붙여넣으세요:")
        print(f"   {file_uri}")
        print("=" * 80)
    
    elif choice == "4":
        print("\n📊 수집 결과를 확인합니다...\n")
        show_collection_results()
    
    elif choice == "5":
        print("\n📋 DOI 큐 관리...\n")
        manage_queue()
    
    elif choice == "0":
        print("\n👋 프로그램을 종료합니다.\n")
        sys.exit(0)
    
    else:
        print("\n❌ 잘못된 선택입니다. 다시 선택해주세요.")


def create_web_dashboard(output_file: Path):
    """웹 대시보드 HTML 생성"""
    import pandas as pd
    
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    # 데이터 수집
    collected_files = sorted(data_dir.glob("parallel_collected_*.csv"), reverse=True)
    
    total_papers = 0
    total_pdf = 0
    total_data = 0
    batch_info = []
    
    for file in collected_files[:5]:  # 최근 5개
        try:
            df = pd.read_csv(file)
            has_pdf = sum(df.get('Cl_source', pd.Series()).notna())
            has_data = sum(df.get('size_nm', pd.Series()).notna())
            
            total_papers += len(df)
            total_pdf += has_pdf
            total_data += has_data
            
            batch_info.append({
                'file': file.name,
                'papers': len(df),
                'pdf': has_pdf,
                'data': has_data
            })
        except:
            pass
    
    # HTML 생성
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CsPbCl3 데이터 마이닝 대시보드</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #999;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .batch-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .batch-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        .batch-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .batch-table tr:hover {{
            background: #f8f9ff;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #eee;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .section {{
            margin-top: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 CsPbCl3 데이터 마이닝 대시보드</h1>
        <div class="subtitle">자동화된 문헌 데이터 수집 시스템</div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_papers}</div>
                <div class="stat-label">총 논문 수</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_pdf}</div>
                <div class="stat-label">PDF 확보</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_data}</div>
                <div class="stat-label">데이터 추출</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">101</div>
                <div class="stat-label">참고 데이터</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {(total_papers/60*100):.1f}%">
                {(total_papers/60*100):.1f}% 완료
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 배치별 수집 결과</div>
            <table class="batch-table">
                <thead>
                    <tr>
                        <th>파일명</th>
                        <th>논문 수</th>
                        <th>PDF 확보</th>
                        <th>데이터 추출</th>
                        <th>성공률</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for batch in batch_info:
        success_rate = (batch['data'] / batch['papers'] * 100) if batch['papers'] > 0 else 0
        html_content += f"""
                    <tr>
                        <td>{batch['file']}</td>
                        <td>{batch['papers']}개</td>
                        <td>{batch['pdf']}개</td>
                        <td>{batch['data']}개</td>
                        <td>{success_rate:.1f}%</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">🎯 프로젝트 목표</div>
            <ul style="font-size: 1.1em; line-height: 2em; margin-left: 20px;">
                <li>✅ 참고 데이터: 101 샘플 확보</li>
                <li>✅ 병렬 처리 시스템 구축 (4개 워커)</li>
                <li>🔄 자동 데이터 수집 (60개 논문 목표)</li>
                <li>📊 Feature Engineering (30+ 변수)</li>
                <li>🤖 ML 모델 학습 (SVR, RF, GBM)</li>
                <li>🎯 특성 예측 시스템 완성</li>
            </ul>
        </div>
    </div>
    
    <script>
        // 자동 새로고침 (5초마다)
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
"""
    
    output_file.write_text(html_content, encoding='utf-8')


def show_collection_results():
    """수집 결과 표시"""
    import pandas as pd
    
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    collected_files = sorted(data_dir.glob("parallel_collected_*.csv"), reverse=True)
    
    if not collected_files:
        print("❌ 수집된 데이터가 없습니다.")
        return
    
    print(f"📊 총 {len(collected_files)}개 배치 발견\n")
    
    for i, file in enumerate(collected_files, 1):
        try:
            df = pd.read_csv(file)
            has_pdf = sum(df.get('Cl_source', pd.Series()).notna())
            has_data = sum(df.get('size_nm', pd.Series()).notna())
            
            print(f"{i}. {file.name}")
            print(f"   논문: {len(df)}개 | PDF: {has_pdf}개 | 데이터: {has_data}개")
            print()
        except Exception as e:
            print(f"   ❌ 오류: {e}\n")


def manage_queue():
    """DOI 큐 관리"""
    project_root = Path(__file__).parent.parent
    queue_file = project_root / "data" / "papers_queue.txt"
    
    if not queue_file.exists():
        print("❌ papers_queue.txt 파일이 없습니다.")
        return
    
    lines = queue_file.read_text().strip().split('\n')
    dois = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    
    print(f"📋 현재 큐에 {len(dois)}개 DOI가 있습니다.\n")
    print("최근 10개:")
    for i, doi in enumerate(dois[:10], 1):
        print(f"   {i}. {doi}")
    
    if len(dois) > 10:
        print(f"   ... 외 {len(dois)-10}개")


def main():
    """메인 함수 - 대화형 메뉴"""
    while True:
        choice = show_menu()
        handle_choice(choice)
        
        if choice in ["1", "4", "5"]:
            input("\n\n⏸️  Enter를 눌러 메뉴로 돌아가기...")


if __name__ == "__main__":
    main()
