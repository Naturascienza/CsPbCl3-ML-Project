#!/usr/bin/env python3
"""
참고 논문 Supplementary Information 자동 다운로드
Selenium을 사용하여 Nature 웹사이트에서 SI 파일 다운로드
"""

import sys
from pathlib import Path
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 프로젝트 경로
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_supplementary_info():
    """참고 논문 SI 다운로드"""
    
    print("\n" + "="*80)
    print("📥 Supplementary Information 자동 다운로드")
    print("="*80)
    
    # 다운로드 경로
    si_dir = project_root / "pdf" / "supplementary"
    si_dir.mkdir(exist_ok=True)
    
    logger.info(f"📂 저장 경로: {si_dir}")
    
    # Chrome 옵션 설정
    chrome_options = Options()
    
    # 백그라운드 실행 최우선 설정
    chrome_options.add_argument('--headless=new')  # Headless 모드 (창 안 보임)
    # 또는 일반 모드로 하되 포커스 안 가져가기
    # chrome_options.add_argument('--disable-gpu')
    
    # 창 설정
    chrome_options.add_argument('--window-size=1200,900')
    chrome_options.add_argument('--window-position=2000,0')  # 화면 밖
    
    # 알림 차단
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    # 자동화 감지 방지
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    prefs = {
        "download.default_directory": str(si_dir.absolute()),
        "download.prompt_for_download": False,  # 다운로드 확인 안 함
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": False,  # PDF는 다운로드
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,  # 안전 검사 활성화
        "profile.default_content_setting_values.automatic_downloads": 1  # 자동 다운로드 허용
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        # WebDriver 초기화
        logger.info("🔧 Chrome WebDriver 초기화 중...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Headless 모드가 아니면 최소화
        # driver.minimize_window()  # Headless에서는 필요 없음
        logger.info("📦 브라우저를 headless 모드로 실행 (화면에 안 보임)")
        
        # 참고 논문 페이지 열기
        doi_url = "https://doi.org/10.1038/s41598-025-08110-2"
        logger.info(f"🌐 논문 페이지 접속: {doi_url}")
        
        driver.get(doi_url)
        time.sleep(5)  # 페이지 로드 대기
        
        # 쿠키 배너 처리 (Nature 웹사이트)
        print("\n🍪 쿠키 배너 처리 중...")
        cookie_selectors = [
            # Nature 쿠키 배너
            "button#onetrust-accept-btn-handler",
            "button.onetrust-close-btn-handler",
            "button[aria-label='허용']",
            "button[aria-label='동의']",
            "button[aria-label='Accept']",
            "button.cc-dismiss",
            "//button[contains(text(), '허용')]",
            "//button[contains(text(), '동의')]",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Agree')]",
            "//button[contains(text(), 'Close')]"
        ]
        
        for selector in cookie_selectors:
            try:
                if selector.startswith("//"):
                    # XPath
                    btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    # CSS Selector
                    btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                driver.execute_script("arguments[0].click();", btn)
                logger.info(f"✅ 쿠키 배너 닫기 성공: {selector}")
                time.sleep(1)
                break
            except:
                continue
        
        # 브라우저 다운로드 승인 처리 (Chrome 자동 다운로드 팝업)
        # Chrome의 "여러 파일 다운로드" 승인은 설정으로 해결됨
        
        print("\n" + "="*80)
        print("📄 논문 페이지가 열렸습니다")
        print("="*80)
        print("\n🔍 Supplementary Information을 찾는 중...")
        
        # Supplementary Information 링크 찾기
        si_patterns = [
            "Supplementary information",
            "Supplementary Information", 
            "Supplementary material",
            "Supplementary data",
            "Additional files"
        ]
        
        si_link = None
        for pattern in si_patterns:
            try:
                logger.info(f"   시도: '{pattern}'")
                si_link = driver.find_element(By.PARTIAL_LINK_TEXT, pattern)
                logger.info(f"✅ SI 링크 발견: '{pattern}'")
                break
            except:
                continue
        
        if not si_link:
            # CSS selector로 시도
            try:
                si_link = driver.find_element(By.CSS_SELECTOR, "a[href*='supplementary']")
                logger.info("✅ SI 링크 발견 (CSS)")
            except:
                pass
        
        if si_link:
            print(f"\n✅ Supplementary Information 링크를 찾았습니다!")
            
            # 링크 클릭
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", si_link)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", si_link)
                logger.info("📥 SI 섹션으로 이동...")
                time.sleep(3)
            except Exception as e:
                logger.warning(f"클릭 실패 (시도 2): {e}")
                try:
                    si_link.click()
                    time.sleep(3)
                except Exception as e2:
                    logger.error(f"클릭 완전 실패: {e2}")
                    print("\n⚠️ 자동 클릭 실패 - 수동 클릭이 필요합니다")
                    print("   브라우저에서 'Supplementary information' 링크를 클릭하세요")
                    input("   클릭 완료 후 Enter를 누르세요...\n")
            
            # 다운로드 승인 대기 (사용자 개입)
            print("\n💡 브라우저 팝업 안내:")
            print("   - '여러 파일 다운로드' 팝업이 나타나면 '허용'을 클릭하세요")
            print("   - PDF 다운로드 승인을 요청하면 '허용'을 클릭하세요")
            print("   - 쿠키/프라이버시 팝업이 나타나면 '동의' 또는 '닫기'를 클릭하세요\n")
            
            # PDF 다운로드 링크 찾기
            print("🔍 PDF 다운로드 링크를 찾는 중...")
            
            pdf_patterns = [
                "Download PDF",
                "Download",
                "PDF",
                "View PDF",
                "Get PDF"
            ]
            
            pdf_downloaded = False
            for pattern in pdf_patterns:
                try:
                    # 여러 개 링크 찾기
                    pdf_links = driver.find_elements(By.PARTIAL_LINK_TEXT, pattern)
                    
                    for pdf_link in pdf_links:
                        if pdf_link.is_displayed():
                            logger.info(f"✅ PDF 링크 발견: '{pattern}'")
                            
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", pdf_link)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", pdf_link)
                                logger.info("📥 PDF 다운로드 중...")
                                pdf_downloaded = True
                                break
                            except Exception as e:
                                logger.warning(f"PDF 링크 클릭 실패: {e}")
                                try:
                                    pdf_link.click()
                                    pdf_downloaded = True
                                    break
                                except:
                                    continue
                    
                    if pdf_downloaded:
                        break
                except:
                    continue
            
            if not pdf_downloaded:
                print("\n⚠️ PDF 다운로드 링크 자동 클릭 실패")
                print("💡 수동 다운로드:")
                print("   1. 브라우저에서 'Download PDF' 또는 'PDF' 링크 찾기")
                print("   2. 링크 클릭하여 다운로드")
                print("   3. 다운로드 완료까지 대기\n")
                input("   준비되면 Enter를 누르세요...\n")
            
            # 다운로드 완료 대기 (최대 60초)
            print("\n⏳ 다운로드 완료 대기 중 (최대 60초)...")
            
            for i in range(60):
                time.sleep(1)
                si_files = list(si_dir.glob("*.pdf")) + \
                          list(si_dir.glob("*.xlsx")) + \
                          list(si_dir.glob("*.csv"))
                
                # .gitkeep 제외
                si_files = [f for f in si_files if f.name != '.gitkeep']
                
                if si_files:
                    print(f"\n✅ 다운로드 완료! ({i+1}초)")
                    for f in si_files:
                        size_kb = f.stat().st_size / 1024
                        print(f"   📄 {f.name} ({size_kb:.1f} KB)")
                    
                    driver.quit()
                    return True
                
                if (i+1) % 10 == 0:
                    print(f"   {i+1}초 경과...")
            
            print("\n⚠️ 다운로드 타임아웃 (60초)")
            print("\n💡 수동 다운로드가 필요할 수 있습니다:")
            print("   1. 브라우저 창에서 SI 파일 확인")
            print("   2. 다운로드 버튼 클릭")
            print(f"   3. {si_dir} 폴더에 저장")
            
            # 브라우저 창 유지 (수동 다운로드 위해)
            print("\n⏸️  브라우저 창을 열어둡니다 (수동 다운로드용)")
            print("   다운로드 완료 후 Ctrl+C로 종료하세요\n")
            
            try:
                while True:
                    time.sleep(5)
                    # 파일 체크
                    si_files = list(si_dir.glob("*.pdf")) + \
                              list(si_dir.glob("*.xlsx")) + \
                              list(si_dir.glob("*.csv"))
                    si_files = [f for f in si_files if f.name != '.gitkeep']
                    
                    if si_files:
                        print(f"\n✅ 파일 감지! 다운로드 완료")
                        for f in si_files:
                            size_kb = f.stat().st_size / 1024
                            print(f"   📄 {f.name} ({size_kb:.1f} KB)")
                        break
            except KeyboardInterrupt:
                print("\n\n👋 종료합니다")
            
            driver.quit()
            return bool(si_files)
            
        else:
            print("\n❌ Supplementary Information 링크를 찾을 수 없습니다")
            print("\n💡 수동 다운로드:")
            print(f"   1. 브라우저에서 {doi_url} 방문")
            print("   2. 'Supplementary information' 섹션 찾기")
            print("   3. PDF/Excel 파일 다운로드")
            print(f"   4. {si_dir} 폴더에 저장")
            
            input("\n계속하려면 Enter를 누르세요...")
            driver.quit()
            return False
    
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        return False


def main():
    """메인 실행"""
    
    success = download_supplementary_info()
    
    if success:
        print("\n" + "="*80)
        print("🎉 Supplementary Information 다운로드 완료!")
        print("="*80)
        print("\n🚀 다음 단계:")
        print("   python scripts/extract_si_tables.py")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("⚠️ 자동 다운로드 실패")
        print("="*80)
        print("\n💡 수동 다운로드 가이드:")
        print("   docs/SUPPLEMENTARY_INFO_DOWNLOAD_GUIDE.md 참조")
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
