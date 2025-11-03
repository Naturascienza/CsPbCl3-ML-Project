#!/usr/bin/env python3
"""
자동 DOI 검색 및 대규모 수집 시스템
CrossRef API로 CsPbCl3 관련 논문 자동 검색 → PDF 다운로드 → 데이터 추출
"""

import requests
import time
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoDOICollector:
    """자동 DOI 검색 및 수집"""
    
    def __init__(self):
        self.crossref_api = "https://api.crossref.org/works"
        self.email = "your_email@example.com"  # CrossRef 정책: 이메일 추가
        
    def search_crossref(
        self, 
        query: str, 
        limit: int = 50,
        filter_params: Dict = None
    ) -> List[Dict]:
        """
        CrossRef API로 논문 검색
        
        Args:
            query: 검색 키워드
            limit: 최대 결과 수
            filter_params: 필터 (예: has-full-text, type:journal-article)
        
        Returns:
            논문 메타데이터 리스트
        """
        results = []
        params = {
            'query': query,
            'rows': min(limit, 100),  # API 제한
            'mailto': self.email,
            'select': 'DOI,title,author,published-print,container-title',
        }
        
        # 필터 추가
        if filter_params:
            filters = []
            for key, value in filter_params.items():
                filters.append(f"{key}:{value}")
            params['filter'] = ','.join(filters)
        
        logger.info(f"🔍 CrossRef 검색: '{query}' (최대 {limit}개)")
        
        try:
            response = requests.get(
                self.crossref_api,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            for item in items:
                doi = item.get('DOI')
                title = item.get('title', ['No title'])[0]
                
                results.append({
                    'doi': doi,
                    'title': title,
                    'authors': self._format_authors(item.get('author', [])),
                    'journal': item.get('container-title', [''])[0],
                    'year': self._extract_year(item),
                })
            
            logger.info(f"✅ {len(results)}개 논문 발견")
            return results
            
        except Exception as e:
            logger.error(f"❌ CrossRef 검색 실패: {str(e)}")
            return []
    
    def _format_authors(self, authors: List[Dict]) -> str:
        """저자 이름 포맷팅"""
        if not authors:
            return ""
        
        names = []
        for author in authors[:3]:  # 처음 3명만
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                names.append(f"{given} {family}".strip())
        
        if len(authors) > 3:
            names.append("et al.")
        
        return ", ".join(names)
    
    def _extract_year(self, item: Dict) -> int:
        """출판 연도 추출"""
        pub_date = item.get('published-print', item.get('published-online', {}))
        date_parts = pub_date.get('date-parts', [[]])[0]
        return date_parts[0] if date_parts else 0
    
    def filter_relevant_papers(
        self, 
        papers: List[Dict],
        keywords: List[str] = None
    ) -> List[Dict]:
        """
        관련 논문 필터링
        
        Args:
            papers: 논문 리스트
            keywords: 필수 키워드 (제목에 포함되어야 함)
        
        Returns:
            필터링된 논문 리스트
        """
        if not keywords:
            keywords = ['cspbcl3', 'quantum dot', 'perovskite', 'synthesis']
        
        filtered = []
        for paper in papers:
            title_lower = paper['title'].lower()
            
            # 키워드 중 하나라도 포함
            if any(kw.lower() in title_lower for kw in keywords):
                filtered.append(paper)
        
        logger.info(f"🔍 필터링: {len(filtered)}/{len(papers)} 논문 선택")
        return filtered
    
    def save_to_queue(self, papers: List[Dict], queue_file: Path):
        """DOI 큐에 저장"""
        existing_dois = set()
        
        # 기존 DOI 읽기
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                existing_dois = {line.strip() for line in f if line.strip()}
        
        # 새 DOI 추가
        new_dois = []
        for paper in papers:
            doi = paper['doi']
            if doi and doi not in existing_dois:
                new_dois.append(doi)
                existing_dois.add(doi)
        
        # 파일에 추가
        if new_dois:
            with open(queue_file, 'a') as f:
                for doi in new_dois:
                    f.write(f"{doi}\n")
            
            logger.info(f"✅ {len(new_dois)}개 새 DOI를 큐에 추가")
        else:
            logger.info("⚠️ 추가할 새 DOI 없음 (모두 중복)")

def main():
    """자동 DOI 검색 및 수집"""
    
    print("="*80)
    print("🔍 CsPbCl3 논문 자동 검색 시스템")
    print("="*80)
    
    # 프로젝트 경로
    project_root = Path(__file__).parent.parent
    queue_file = project_root / "data" / "papers_queue.txt"
    
    # 수집기 초기화
    collector = AutoDOICollector()
    
    # 검색 쿼리 (여러 변형)
    queries = [
        "CsPbCl3 quantum dots synthesis",
        "cesium lead chloride QDs",
        "CsPbCl3 perovskite nanocrystals",
        "all-inorganic perovskite CsPbCl3",
        "hot injection CsPbCl3",
    ]
    
    all_papers = []
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"🔍 검색: '{query}'")
        print("="*80)
        
        papers = collector.search_crossref(
            query=query,
            limit=20,  # 각 쿼리당 20개
            filter_params={
                'type': 'journal-article',
                'has-full-text': 'true'
            }
        )
        
        all_papers.extend(papers)
        time.sleep(1)  # API 제한 준수
    
    # 중복 제거 (DOI 기준)
    unique_papers = {}
    for paper in all_papers:
        doi = paper['doi']
        if doi and doi not in unique_papers:
            unique_papers[doi] = paper
    
    papers_list = list(unique_papers.values())
    
    print(f"\n{'='*80}")
    print(f"📊 검색 결과")
    print("="*80)
    print(f"   - 총 논문 수: {len(all_papers)}")
    print(f"   - 중복 제거 후: {len(papers_list)}")
    
    # 관련 논문 필터링
    filtered = collector.filter_relevant_papers(
        papers_list,
        keywords=['cspbcl3', 'quantum dot', 'perovskite']
    )
    
    # 큐에 저장
    print(f"\n{'='*80}")
    print(f"💾 DOI 큐에 저장")
    print("="*80)
    collector.save_to_queue(filtered, queue_file)
    
    # 결과 요약
    print(f"\n{'='*80}")
    print(f"✅ 완료!")
    print("="*80)
    print(f"   - 새 DOI: {len(filtered)}개")
    print(f"   - 큐 파일: {queue_file}")
    print(f"\n💡 다음 단계:")
    print(f"   python scripts/auto_data_collector.py")
    print("="*80)

if __name__ == "__main__":
    main()
