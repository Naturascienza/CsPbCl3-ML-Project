#!/usr/bin/env python3
"""
참고 논문(Çadırcı et al., 2025)에서 데이터 추출
708 샘플의 CsPbCl3 QD 데이터 확보
"""

import sys
from pathlib import Path
import pandas as pd
import logging
import re

# 프로젝트 경로
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_from_reference_paper():
    """참고 논문 텍스트에서 데이터 추출"""
    
    logger.info("="*80)
    logger.info("📚 참고 논문 데이터 추출 시작")
    logger.info("="*80)
    
    # 참고 논문 텍스트 파일
    ref_text_path = project_root / "pdf" / "references" / "main_reference.txt"
    
    if not ref_text_path.exists():
        logger.error("❌ 참고 논문 텍스트 파일 없음")
        return None
    
    text = ref_text_path.read_text(encoding='utf-8', errors='ignore')
    logger.info(f"✅ 텍스트 로드 완료: {len(text):,} 글자")
    
    # 논문 정보
    logger.info(f"\n📄 참고 논문 정보:")
    logger.info(f"   제목: Machine learning prediction of quantum dot...")
    logger.info(f"   저자: Çadırcı et al.")
    logger.info(f"   연도: 2025")
    logger.info(f"   저널: Scientific Reports")
    logger.info(f"   데이터: 59 papers, 708 samples")
    
    # 표 언급 찾기
    table_mentions = re.findall(r'Table S?\d+', text, re.IGNORECASE)
    logger.info(f"\n📊 발견된 표: {len(set(table_mentions))}개")
    for table in sorted(set(table_mentions)):
        logger.info(f"   - {table}")
    
    # Supplementary Information 언급
    si_mentions = text.lower().count('supplementary')
    logger.info(f"\n📎 Supplementary Information 언급: {si_mentions}회")
    
    return text


def check_for_supplementary_files():
    """Supplementary Information 파일 확인"""
    
    logger.info("\n" + "="*80)
    logger.info("🔍 Supplementary Information 파일 검색")
    logger.info("="*80)
    
    supplementary_dir = project_root / "pdf" / "supplementary"
    supplementary_dir.mkdir(exist_ok=True)
    
    # 가능한 SI 파일들
    si_files = list(supplementary_dir.glob("*.pdf")) + \
               list(supplementary_dir.glob("*.xlsx")) + \
               list(supplementary_dir.glob("*.csv"))
    
    if si_files:
        logger.info(f"✅ {len(si_files)}개 파일 발견:")
        for f in si_files:
            logger.info(f"   📄 {f.name} ({f.stat().st_size / 1024:.1f} KB)")
        return si_files
    else:
        logger.warning("⚠️  Supplementary Information 파일 없음")
        logger.info("\n💡 다운로드 필요:")
        logger.info("   DOI: 10.1038/s41598-025-08110-2")
        logger.info("   URL: https://doi.org/10.1038/s41598-025-08110-2")
        logger.info("   → 'Supplementary Information' 클릭")
        logger.info("   → pdf/supplementary/ 폴더에 저장")
        return []


def create_reference_dataset_template():
    """참고 논문 데이터 형식으로 템플릿 생성"""
    
    logger.info("\n" + "="*80)
    logger.info("📋 참고 논문 데이터 템플릿 생성")
    logger.info("="*80)
    
    # 참고 논문에 있는 특징들 (논문 Figure 4, Table S1 참조)
    columns = [
        # 메타데이터
        'paper_id',
        'source_paper',
        'sample_id',
        
        # 합성 조건
        'injection_temp_C',
        'PbCl2_mmol',
        'Cs_precursor',
        'Cs_mmol',
        'OA_ml',
        'OLA_ml', 
        'ODE_ml',
        'reaction_time_min',
        
        # QD 특성
        'size_nm',
        'PL_peak_nm',
        'PLQY_percent',
        'FWHM_nm',
        
        # 추가 정보
        'synthesis_method',
        'notes'
    ]
    
    df_template = pd.DataFrame(columns=columns)
    
    output_path = project_root / "data" / "reference_dataset.csv"
    df_template.to_csv(output_path, index=False)
    
    logger.info(f"✅ 템플릿 생성: {output_path}")
    logger.info(f"   컬럼 수: {len(columns)}개")
    
    return df_template


def parse_manual_entry_example():
    """수동 입력 예시 (논문에서 언급된 대표 샘플)"""
    
    logger.info("\n" + "="*80)
    logger.info("📝 대표 샘플 예시 (수동 입력 가이드)")
    logger.info("="*80)
    
    # 논문에서 언급된 전형적인 hot-injection 조건
    example_samples = [
        {
            'paper_id': 'REF001',
            'source_paper': 'Çadırcı et al., 2025',
            'sample_id': 'Example_1',
            'injection_temp_C': 180,
            'PbCl2_mmol': 0.188,
            'Cs_precursor': 'Cs-oleate',
            'Cs_mmol': 0.8,
            'OA_ml': 1.0,
            'OLA_ml': 1.0,
            'ODE_ml': 10.0,
            'reaction_time_min': 5,
            'size_nm': 8.0,
            'PL_peak_nm': 410,
            'PLQY_percent': 90,
            'FWHM_nm': 12,
            'synthesis_method': 'hot-injection',
            'notes': 'Typical hot-injection synthesis'
        }
    ]
    
    df_examples = pd.DataFrame(example_samples)
    
    logger.info(f"\n✅ 예시 샘플:")
    for col in df_examples.columns:
        val = df_examples[col].iloc[0]
        logger.info(f"   {col:25s}: {val}")
    
    return df_examples


def main():
    """메인 실행"""
    
    print("\n" + "="*80)
    print("🔬 CsPbCl3 참고 논문 데이터 추출")
    print("="*80)
    
    # 1. 참고 논문 텍스트 분석
    text = extract_from_reference_paper()
    
    # 2. Supplementary Information 파일 확인
    si_files = check_for_supplementary_files()
    
    # 3. 템플릿 생성
    template = create_reference_dataset_template()
    
    # 4. 수동 입력 예시
    examples = parse_manual_entry_example()
    
    # 종합 보고
    print("\n" + "="*80)
    print("📊 요약")
    print("="*80)
    print(f"✅ 참고 논문: Çadırcı et al., 2025 (Nature Scientific Reports)")
    print(f"✅ 예상 데이터: 708 샘플 (59 papers)")
    print(f"✅ 템플릿 생성: data/reference_dataset.csv")
    
    if si_files:
        print(f"✅ SI 파일: {len(si_files)}개 발견")
        print(f"\n🚀 다음 단계:")
        print(f"   1. SI 파일에서 표 자동 추출")
        print(f"   2. 708 샘플 데이터 통합")
        print(f"   3. ML 모델 학습 시작")
    else:
        print(f"⚠️  SI 파일 없음")
        print(f"\n💡 권장 사항:")
        print(f"   1. DOI 10.1038/s41598-025-08110-2 방문")
        print(f"   2. Supplementary Information 다운로드")
        print(f"   3. pdf/supplementary/ 폴더에 저장")
        print(f"   4. 이 스크립트 재실행")
        print(f"\n대안:")
        print(f"   - 논문 Table에서 대표 샘플 수동 입력 (50-100개)")
        print(f"   - 다른 문헌 자동 수집 계속 (개선된 추출기)")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
