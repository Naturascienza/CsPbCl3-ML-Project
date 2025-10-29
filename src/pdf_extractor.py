"""PDF를 텍스트로 추출하는 스크립트"""
import pdfplumber
from pathlib import Path

def extract_pdf_to_text(pdf_path, output_path=None):
    """
    PDF 파일에서 텍스트를 추출합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        output_path: 출력 텍스트 파일 경로 (None이면 자동 생성)
    """
    pdf_path = Path(pdf_path)
    
    if output_path is None:
        output_path = pdf_path.with_suffix('.txt')
    
    print(f"📄 PDF 파일 읽는 중: {pdf_path.name}")
    
    all_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"📊 총 페이지 수: {total_pages}")
        
        for i, page in enumerate(pdf.pages, 1):
            print(f"  처리 중: {i}/{total_pages} 페이지...", end='\r')
            
            # 텍스트 추출
            text = page.extract_text()
            if text:
                all_text.append(f"\n{'='*80}\n")
                all_text.append(f"PAGE {i}\n")
                all_text.append(f"{'='*80}\n\n")
                all_text.append(text)
                all_text.append("\n\n")
            
            # 표 추출
            tables = page.extract_tables()
            if tables:
                all_text.append(f"\n--- Tables on Page {i} ---\n")
                for j, table in enumerate(tables, 1):
                    all_text.append(f"\nTable {j}:\n")
                    for row in table:
                        all_text.append(" | ".join(str(cell) if cell else "" for cell in row))
                        all_text.append("\n")
                    all_text.append("\n")
    
    print(f"\n✅ 텍스트 추출 완료!")
    
    # 파일 저장
    full_text = "".join(all_text)
    output_path.write_text(full_text, encoding='utf-8')
    
    print(f"💾 저장 완료: {output_path}")
    print(f"📏 총 텍스트 길이: {len(full_text):,} 문자")
    
    # 미리보기
    print(f"\n{'='*80}")
    print("📖 텍스트 미리보기 (처음 1000자):")
    print(f"{'='*80}")
    print(full_text[:1000])
    print("...")
    
    return output_path


if __name__ == "__main__":
    # 메인 참고문헌 추출
    pdf_file = "pdf/references/main_reference.pdf"
    output_file = extract_pdf_to_text(pdf_file)
    
    print(f"\n🎉 완료! 다음 파일을 확인하세요: {output_file}")
