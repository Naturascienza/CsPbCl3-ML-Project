#!/usr/bin/env python3
"""
간단한 수동 다운로드 헬퍼
브라우저만 열고 수동으로 다운로드하도록 안내
백그라운드에서 새 탭으로 열기 (작업 방해 안 함)
"""

import sys
from pathlib import Path
import time
import subprocess
import platform

project_root = Path(__file__).parent.parent
si_dir = project_root / "pdf" / "supplementary"

print("\n" + "="*80)
print("📥 Supplementary Information 수동 다운로드 가이드")
print("="*80)

# 브라우저 열기 (백그라운드, 새 탭)
doi_url = "https://doi.org/10.1038/s41598-025-08110-2"
print(f"\n🌐 브라우저에서 논문 페이지를 여는 중... (백그라운드)")
print(f"   URL: {doi_url}\n")

# macOS에서 백그라운드로 브라우저 열기
if platform.system() == "Darwin":  # macOS
    # Chrome을 백그라운드에서 새 탭으로 열기 (더 강력한 방법)
    try:
        # AppleScript로 백그라운드 제어
        applescript = f'''
        tell application "Google Chrome"
            set newTab to make new tab at end of tabs of window 1
            set URL of newTab to "{doi_url}"
        end tell
        '''
        subprocess.run(
            ['osascript', '-e', applescript],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Chrome 백그라운드 탭으로 열렸습니다 (현재 작업 유지)")
    except:
        # AppleScript 실패 시 대체 방법
        subprocess.Popen(
            ['open', '-g', '-a', 'Google Chrome', doi_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Chrome이 백그라운드에서 열렸습니다")
else:
    # 다른 OS는 기본 브라우저로
    import webbrowser
    webbrowser.open_new_tab(doi_url)
    print("✅ 브라우저가 열렸습니다")

time.sleep(2)

print("="*80)
print("📝 다운로드 단계")
print("="*80)
print("""
1. 브라우저에서 논문 페이지가 열립니다
   
2. 페이지를 아래로 스크롤하여 "Supplementary information" 섹션을 찾습니다
   
3. "Download PDF" 또는 "PDF" 링크를 클릭합니다
   
4. 다운로드된 파일을 다음 폴더로 이동:
   {si_dir}
   
5. 파일 형식:
   - PDF: supplementary_information.pdf (또는 유사한 이름)
   - Excel: supplementary_tables.xlsx (또는 유사한 이름)
   
6. 다운로드 완료 후:
   python scripts/extract_si_tables.py
""".format(si_dir=si_dir))

print("="*80)
print("\n💡 팁:")
print("   - Excel 파일(.xlsx)이 있으면 PDF보다 더 좋습니다")
print("   - Nature 논문은 보통 'Supplementary Information' 섹션이 페이지 하단에 있습니다")
print("   - 파일 이름은 무엇이든 상관없습니다 (pdf/supplementary/ 폴더에만 저장)")
print("\n" + "="*80)

# 다운로드 폴더 확인
print(f"\n📂 저장 경로: {si_dir}")
print("   (Finder에서 폴더를 열려면 아래 명령 사용)")
print(f"   open {si_dir}\n")

input("완료했으면 Enter를 누르세요...")

# 파일 확인
si_files = list(si_dir.glob("*.pdf")) + \
           list(si_dir.glob("*.xlsx")) + \
           list(si_dir.glob("*.csv"))
si_files = [f for f in si_files if f.name != '.gitkeep']

if si_files:
    print("\n✅ 다음 파일이 발견되었습니다:")
    for f in si_files:
        size_kb = f.stat().st_size / 1024
        print(f"   📄 {f.name} ({size_kb:.1f} KB)")
    
    print("\n🚀 다음 단계:")
    print("   python scripts/extract_si_tables.py")
else:
    print("\n⚠️ 파일이 발견되지 않았습니다")
    print(f"   파일을 {si_dir} 폴더에 저장했는지 확인하세요")
