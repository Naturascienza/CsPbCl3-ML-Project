#!/usr/bin/env python3
"""
DOI 검증 및 CrossRef 검색 스크립트
실제 존재하는 CsPbCl3 관련 논문 DOI를 찾습니다.
"""

import requests
import time
from typing import List, Dict
import json

def validate_doi(doi: str) -> bool:
    """DOI가 실제로 존재하는지 확인"""
    try:
        response = requests.head(f"https://doi.org/{doi}", timeout=5, allow_redirects=True)
        return response.status_code in [200, 302]
    except:
        return False

def search_crossref(query: str, rows: int = 20) -> List[Dict]:
    """CrossRef API로 논문 검색"""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": rows,
        "select": "DOI,title,published,container-title,author",
        "filter": "type:journal-article"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('message', {}).get('items', [])
    except Exception as e:
        print(f"Error searching CrossRef: {e}")
    
    return []

def validate_existing_dois(csv_file: str) -> Dict[str, bool]:
    """CSV 파일의 DOI들을 검증"""
    import pandas as pd
    
    print("📋 기존 DOI 검증 중...")
    df = pd.read_csv(csv_file)
    unique_dois = df['doi'].unique()
    
    results = {}
    valid_count = 0
    invalid_count = 0
    
    for i, doi in enumerate(unique_dois, 1):
        is_valid = validate_doi(doi)
        results[doi] = is_valid
        
        if is_valid:
            print(f"  ✅ [{i}/{len(unique_dois)}] {doi}")
            valid_count += 1
        else:
            print(f"  ❌ [{i}/{len(unique_dois)}] {doi}")
            invalid_count += 1
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n📊 검증 결과:")
    print(f"  - 유효: {valid_count}개 ({valid_count/len(unique_dois)*100:.1f}%)")
    print(f"  - 무효: {invalid_count}개 ({invalid_count/len(unique_dois)*100:.1f}%)")
    
    return results

def search_cspbcl3_papers() -> List[Dict]:
    """CsPbCl3 관련 논문 검색"""
    print("\n🔍 CsPbCl3 논문 검색 중...\n")
    
    search_queries = [
        "CsPbCl3 perovskite quantum dots",
        "cesium lead chloride quantum dots",
        "CsPbCl3 nanocrystals synthesis",
        "CsPbCl3 colloidal quantum dots",
        "cesium lead halide perovskite CsPbCl3"
    ]
    
    all_papers = []
    seen_dois = set()
    
    for query in search_queries:
        print(f"  검색어: '{query}'")
        papers = search_crossref(query, rows=15)
        
        for paper in papers:
            doi = paper.get('DOI', '')
            if doi and doi not in seen_dois:
                # CsPbCl3 관련성 확인
                title = paper.get('title', [''])[0].lower()
                if any(keyword in title for keyword in ['cspbcl3', 'cesium lead chloride', 'perovskite', 'quantum dot']):
                    seen_dois.add(doi)
                    all_papers.append(paper)
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n  ✅ 총 {len(all_papers)}개의 고유 논문 발견\n")
    return all_papers

def save_validated_dois(papers: List[Dict], output_file: str):
    """검증된 DOI를 파일로 저장"""
    print("💾 검증된 DOI 저장 중...")
    
    validated_papers = []
    
    for i, paper in enumerate(papers, 1):
        doi = paper.get('DOI', '')
        if validate_doi(doi):
            title = paper.get('title', ['Unknown'])[0]
            year = paper.get('published', {}).get('date-parts', [[0]])[0][0]
            journal = paper.get('container-title', ['Unknown'])[0]
            
            validated_papers.append({
                'doi': doi,
                'title': title[:100],
                'year': year,
                'journal': journal[:50]
            })
            
            print(f"  ✅ [{i}/{len(papers)}] {doi}")
            print(f"      {title[:80]}")
        else:
            print(f"  ❌ [{i}/{len(papers)}] {doi} (무효)")
        
        time.sleep(0.5)
    
    # JSON으로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validated_papers, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ {len(validated_papers)}개의 유효한 논문을 {output_file}에 저장했습니다.")
    
    return validated_papers

def main():
    print("=" * 70)
    print("🔬 CsPbCl3 논문 DOI 검증 및 검색")
    print("=" * 70)
    
    # 1. 기존 DOI 검증
    csv_file = "data/literature_data_collected.csv"
    existing_validation = validate_existing_dois(csv_file)
    
    # 2. 새로운 논문 검색
    new_papers = search_cspbcl3_papers()
    
    # 3. 검증 및 저장
    output_file = "data/validated_dois.json"
    validated = save_validated_dois(new_papers, output_file)
    
    # 4. papers_queue.txt 업데이트용 DOI 리스트 생성
    print("\n📝 papers_queue.txt 업데이트용 DOI:")
    print("-" * 70)
    for paper in validated[:30]:  # 상위 30개만
        print(paper['doi'])
    
    print("\n" + "=" * 70)
    print("✅ 완료!")
    print(f"   검증된 DOI: {len(validated)}개")
    print(f"   저장 위치: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
