#!/usr/bin/env python3
"""
Supplementary Information에서 표 자동 추출
tabula-py 사용하여 PDF 표 → pandas DataFrame
"""

import sys
from pathlib import Path
import pandas as pd
import logging
import tabula

# 프로젝트 경로
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_tables_from_pdf(pdf_path: Path) -> list:
    """PDF에서 모든 표 추출"""
    
    logger.info(f"📄 PDF 처리 중: {pdf_path.name}")
    
    try:
        # 모든 페이지에서 표 추출
        tables = tabula.read_pdf(
            str(pdf_path),
            pages='all',
            multiple_tables=True,
            lattice=True,  # 격자선이 있는 표
            stream=True    # 격자선 없는 표도 시도
        )
        
        logger.info(f"✅ {len(tables)}개 표 발견")
        
        return tables
        
    except Exception as e:
        logger.error(f"❌ 표 추출 실패: {e}")
        return []


def identify_data_table(df: pd.DataFrame) -> bool:
    """데이터 표인지 판단"""
    
    # CsPbCl3 관련 키워드
    keywords = ['temp', 'pbcl2', 'cs', 'oleate', 'oa', 'ola', 'ode', 
                'size', 'pl', 'plqy', 'fwhm', 'injection']
    
    # 컬럼명에 키워드가 있는지 확인
    columns_str = ' '.join([str(c).lower() for c in df.columns])
    
    matches = sum(1 for kw in keywords if kw in columns_str)
    
    return matches >= 3  # 3개 이상 키워드 매치


def clean_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """표 데이터 정리 및 표준화"""
    
    # 컬럼명 정리
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    
    # 빈 행 제거
    df = df.dropna(how='all')
    
    # 숫자 컬럼 변환
    for col in df.columns:
        if any(kw in col for kw in ['temp', 'mmol', 'ml', 'size', 'nm', 'plqy', 'fwhm']):
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def main():
    """메인 실행"""
    
    print("\n" + "="*80)
    print("📊 Supplementary Information 표 추출")
    print("="*80)
    
    # SI 디렉토리
    si_dir = project_root / "pdf" / "supplementary"
    
    # PDF 파일 찾기
    si_files = list(si_dir.glob("*.pdf"))
    
    if not si_files:
        logger.error("❌ Supplementary Information PDF 없음")
        logger.info("\n💡 다운로드 가이드:")
        logger.info("   docs/SUPPLEMENTARY_INFO_DOWNLOAD_GUIDE.md 참조")
        return
    
    logger.info(f"✅ {len(si_files)}개 PDF 파일 발견\n")
    
    all_data_tables = []
    
    # 각 PDF 처리
    for pdf_path in si_files:
        logger.info("="*80)
        logger.info(f"📄 {pdf_path.name}")
        logger.info("="*80)
        
        # 표 추출
        tables = extract_tables_from_pdf(pdf_path)
        
        # 각 표 분석
        for i, table in enumerate(tables, 1):
            logger.info(f"\n표 {i}:")
            logger.info(f"  크기: {table.shape[0]} 행 x {table.shape[1]} 열")
            logger.info(f"  컬럼: {list(table.columns)[:5]}...")
            
            # 데이터 표인지 확인
            if identify_data_table(table):
                logger.info(f"  ✅ CsPbCl3 데이터 표로 식별!")
                
                # 정리 및 표준화
                clean_table = clean_and_standardize(table)
                all_data_tables.append({
                    'source': pdf_path.name,
                    'table_num': i,
                    'data': clean_table
                })
            else:
                logger.info(f"  ⚠️  관련 데이터 아님")
    
    # 결과 저장
    if all_data_tables:
        logger.info("\n" + "="*80)
        logger.info(f"💾 데이터 저장")
        logger.info("="*80)
        
        for item in all_data_tables:
            output_name = f"reference_data_table{item['table_num']}.csv"
            output_path = project_root / "data" / output_name
            
            item['data'].to_csv(output_path, index=False)
            
            logger.info(f"✅ {output_name}")
            logger.info(f"   샘플 수: {len(item['data'])}")
            logger.info(f"   컬럼 수: {len(item['data'].columns)}")
        
        # 전체 통합
        combined = pd.concat([item['data'] for item in all_data_tables], 
                            ignore_index=True)
        
        combined_path = project_root / "data" / "reference_dataset_extracted.csv"
        combined.to_csv(combined_path, index=False)
        
        logger.info(f"\n✅ 통합 데이터: {combined_path.name}")
        logger.info(f"   총 샘플: {len(combined)}")
        logger.info(f"   총 컬럼: {len(combined.columns)}")
        
        print("\n" + "="*80)
        print("🎉 데이터 추출 완료!")
        print("="*80)
        print(f"📊 총 {len(combined)}개 샘플 확보")
        print(f"📁 저장 위치: data/reference_dataset_extracted.csv")
        print(f"\n🚀 다음 단계: ML 모델 학습 시작!")
        print("="*80 + "\n")
        
    else:
        logger.warning("\n⚠️  데이터 표를 찾지 못했습니다")
        logger.info("\n💡 대안:")
        logger.info("   1. Excel 파일(.xlsx)로 다운로드 시도")
        logger.info("   2. 논문 본문 표에서 수동 추출")
        logger.info("   3. 저자에게 데이터 요청")


if __name__ == "__main__":
    main()
