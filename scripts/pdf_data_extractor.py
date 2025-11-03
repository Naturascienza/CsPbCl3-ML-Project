#!/usr/bin/env python3
"""
PDF 자동 데이터 추출 모듈
논문 PDF에서 합성 조건과 특성 데이터를 자동으로 추출
Selenium을 통한 기관 구독 활용 지원
"""

import re
import requests
import pdfplumber
from pathlib import Path
from typing import Dict, Optional, List
import logging
import time
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class PDFDataExtractor:
    """PDF에서 CsPbCl3 합성 데이터 추출"""
    
    def __init__(self, pdf_dir: Path, use_selenium: bool = True):
        self.pdf_dir = pdf_dir
        self.pdf_dir.mkdir(exist_ok=True)
        self.use_selenium = use_selenium
        self.driver = None
        
        if use_selenium:
            self._init_selenium()
    
    def _init_selenium(self):
        """Selenium 웹드라이버 초기화 (완전 headless)"""
        try:
            chrome_options = Options()
            
            # 완전 headless 모드 (화면에 절대 안 보임!)
            chrome_options.add_argument('--headless=new')  # 새로운 headless 모드
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            
            # 화면 밖으로 이동 (추가 안전장치)
            chrome_options.add_argument('--window-position=-2400,-2400')
            
            # 백그라운드 실행
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            
            # 다운로드 설정
            prefs = {
                "download.default_directory": str(self.pdf_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_setting_values.automatic_downloads": 1,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # ChromeDriver 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            service.log_path = '/dev/null'  # 로그 숨김
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Selenium 웹드라이버 초기화 완료 (완전 headless 모드 - 화면 방해 없음)")
        except Exception as e:
            logger.warning(f"⚠️ Selenium 초기화 실패: {e}")
            logger.warning("기본 requests 방식으로 전환합니다.")
            self.use_selenium = False
    
    def __del__(self):
        """소멸자: 웹드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def _download_with_selenium(self, doi: str, pdf_path: Path) -> bool:
        """Selenium을 통한 PDF 다운로드 (기관 구독 활용)"""
        if not self.driver:
            return False
        
        try:
            doi_url = f"https://doi.org/{doi}"
            logger.info(f"🌐 브라우저로 접근 중: {doi_url}")
            
            self.driver.get(doi_url)
            time.sleep(5)  # 페이지 로드 대기 (더 길게)
            
            # 쿠키 배너 닫기 시도 (여러 패턴)
            cookie_close_selectors = [
                "button.cc-dismiss",  # 일반적인 쿠키 닫기
                "button[aria-label='Close']",
                "button.cookie-consent-close",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Reject')]",
                "//button[contains(text(), 'Close')]"
            ]
            
            for selector in cookie_close_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath
                        btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        # CSS
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    btn.click()
                    logger.info("✅ 쿠키 배너 닫기 성공")
                    time.sleep(1)
                    break
                except:
                    continue
            
            # PDF 링크 찾기 (여러 방법 시도)
            pdf_link = None
            
            # 방법 1: 텍스트로 찾기
            pdf_link_texts = [
                "Download PDF", "PDF", "View PDF", "Full Text PDF",
                "Download Article", "Article PDF", "Full-text PDF",
                "Download", "Full Text", "Article"
            ]
            
            for link_text in pdf_link_texts:
                try:
                    links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, link_text)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and ('.pdf' in href or 'pdf' in href.lower()):
                            pdf_link = link
                            logger.info(f"✅ PDF 링크 발견 (텍스트): '{link_text}'")
                            break
                    if pdf_link:
                        break
                except:
                    continue
            
            # 방법 2: CSS Selector로 찾기
            if not pdf_link:
                pdf_selectors = [
                    "a[href*='.pdf']",
                    "a[data-article-pdf='true']",
                    "a.pdf-download",
                    "a.download-pdf",
                    "a[href*='pdf']",
                    "button[data-test='pdf-download']"
                ]
                
                for selector in pdf_selectors:
                    try:
                        pdf_link = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"✅ PDF 링크 발견 (CSS): {selector}")
                        break
                    except:
                        continue
            
            # 방법 3: XPath로 찾기
            if not pdf_link:
                pdf_xpaths = [
                    "//a[contains(@href, '.pdf')]",
                    "//a[contains(text(), 'PDF')]",
                    "//button[contains(text(), 'PDF')]",
                ]
                
                for xpath in pdf_xpaths:
                    try:
                        pdf_link = self.driver.find_element(By.XPATH, xpath)
                        logger.info(f"✅ PDF 링크 발견 (XPath): {xpath}")
                        break
                    except:
                        continue
            
            if pdf_link:
                # JavaScript로 클릭 (배너 우회)
                try:
                    self.driver.execute_script("arguments[0].click();", pdf_link)
                    logger.info("📥 PDF 다운로드 시작 (JavaScript 클릭)...")
                except:
                    # 일반 클릭 시도
                    try:
                        pdf_link.click()
                        logger.info("📥 PDF 다운로드 시작 (일반 클릭)...")
                    except:
                        # href 직접 접근
                        href = pdf_link.get_attribute('href')
                        if href:
                            self.driver.get(href)
                            logger.info("📥 PDF 다운로드 시작 (URL 직접 접근)...")
                
                # 다운로드 완료 대기 (최대 60초)
                before_files = set(glob.glob(str(self.pdf_dir / "*.pdf")))
                
                for i in range(60):
                    time.sleep(1)
                    after_files = set(glob.glob(str(self.pdf_dir / "*.pdf")))
                    new_files = after_files - before_files
                    
                    if new_files:
                        # 새 파일이 생성됨
                        downloaded_file = Path(list(new_files)[0])
                        
                        # 파일명 변경
                        downloaded_file.rename(pdf_path)
                        logger.info(f"✅ PDF 다운로드 완료: {pdf_path.name}")
                        return True
                
                logger.warning("⚠️ PDF 다운로드 타임아웃 (60초)")
                return False
            else:
                logger.warning("⚠️ PDF 링크를 찾을 수 없음")
                
                # 페이지 소스 분석 (디버깅)
                if 'pdf' in self.driver.page_source.lower():
                    logger.debug("💡 페이지에 'pdf' 텍스트 존재 - 다른 접근 방법 필요")
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Selenium 다운로드 실패: {e}")
            return False
    
    def download_pdf(self, doi: str) -> Optional[Path]:
        """PDF 다운로드 (여러 소스 시도)"""
        
        # 1. 이미 다운로드된 PDF 확인
        pdf_path = self.pdf_dir / f"{doi.replace('/', '_')}.pdf"
        if pdf_path.exists():
            logger.info(f"✅ 기존 PDF 사용: {pdf_path.name}")
            return pdf_path
        
        # 2. Selenium을 통한 다운로드 시도 (기관 구독 활용) ⭐ 신규!
        if self.use_selenium:
            logger.info(f"🔍 Selenium으로 PDF 다운로드 시도: {doi}")
            if self._download_with_selenium(doi, pdf_path):
                return pdf_path
        
        # 3. Unpaywall API 시도
        email = "research@example.com"
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        
        try:
            logger.info(f"🔍 Unpaywall PDF 검색 중: {doi}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 오픈액세스 PDF URL 찾기
                pdf_url = None
                if data.get('is_oa'):
                    best_oa = data.get('best_oa_location', {})
                    pdf_url = best_oa.get('url_for_pdf')
                
                if pdf_url:
                    logger.info(f"📥 PDF 다운로드 중: {pdf_url}")
                    pdf_response = requests.get(pdf_url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                    })
                    
                    if pdf_response.status_code == 200:
                        pdf_path.write_bytes(pdf_response.content)
                        logger.info(f"✅ PDF 저장: {pdf_path.name}")
                        return pdf_path
        
        except Exception as e:
            logger.debug(f"Unpaywall 실패: {e}")
        
        # 4. DOI.org 직접 접근 시도
        try:
            logger.info(f"🔗 DOI.org 접근 시도: {doi}")
            doi_url = f"https://doi.org/{doi}"
            response = requests.get(doi_url, timeout=10, allow_redirects=True, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Accept': 'application/pdf'
            })
            
            # PDF인지 확인
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                pdf_path.write_bytes(response.content)
                logger.info(f"✅ DOI.org에서 PDF 저장: {pdf_path.name}")
                return pdf_path
        
        except Exception as e:
            logger.debug(f"DOI.org 접근 실패: {e}")
        
        logger.warning(f"⚠️  PDF 다운로드 실패 (모든 소스): {doi}")
        return None
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """PDF에서 텍스트 추출"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"❌ PDF 텍스트 추출 실패: {e}")
            return ""
    
    def extract_tables_from_pdf(self, pdf_path: Path) -> list:
        """PDF에서 표 추출 (새로운 기능!)"""
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    if page_tables:
                        logger.info(f"   페이지 {page_num}: {len(page_tables)}개 표 발견")
                        tables.extend(page_tables)
            
            if tables:
                logger.info(f"✅ 총 {len(tables)}개 표 추출")
            return tables
        except Exception as e:
            logger.debug(f"표 추출 실패: {e}")
            return []
    
    def parse_synthesis_from_table(self, tables: list) -> Dict:
        """표에서 합성 조건 파싱"""
        data = {}
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # 표를 문자열로 변환하여 분석
            table_text = ' '.join([' '.join([str(cell) for cell in row if cell]) 
                                  for row in table]).lower()
            
            # CsPbCl3 합성 관련 표인지 확인
            if not ('cspbcl3' in table_text or 'perovskite' in table_text or 
                    'quantum dot' in table_text or 'pbcl2' in table_text):
                continue
            
            logger.info("   ✅ CsPbCl3 합성 관련 표 발견")
            
            # 표에서 값 추출 (행 기반)
            for row in table[1:]:  # 첫 행은 헤더
                if not row:
                    continue
                
                row_text = ' '.join([str(cell).lower() for cell in row if cell])
                
                # 온도 (100-250°C 범위)
                if 'temp' in row_text or 'injection' in row_text:
                    for cell in row:
                        if cell and str(cell).replace('.', '').isdigit():
                            temp = float(cell)
                            if 100 <= temp <= 250:
                                data['injection_temp_C'] = temp
                                break
                
                # 전구체 양
                if 'pbcl2' in row_text or 'lead' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 0.01 <= cell <= 10:  # mmol 범위
                                data['Pb_amount_mmol'] = cell
                
                # 리간드
                if 'oa' in row_text and 'oleic' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 0.1 <= cell <= 20:  # mL 범위
                                data['OA_volume_ml'] = cell
                
                if 'ola' in row_text or 'oleylamine' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 0.1 <= cell <= 20:
                                data['OLA_volume_ml'] = cell
                
                if 'ode' in row_text or 'octadecene' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 1 <= cell <= 50:
                                data['ODE_volume_ml'] = cell
        
        return data
    
    def parse_properties_from_table(self, tables: list) -> Dict:
        """표에서 QD 특성 파싱"""
        data = {}
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            table_text = ' '.join([' '.join([str(cell) for cell in row if cell]) 
                                  for row in table]).lower()
            
            # 특성 관련 표인지 확인
            if not ('pl' in table_text or 'plqy' in table_text or 
                    'size' in table_text or 'emission' in table_text):
                continue
            
            logger.info("   ✅ QD 특성 관련 표 발견")
            
            for row in table[1:]:
                if not row:
                    continue
                
                row_text = ' '.join([str(cell).lower() for cell in row if cell])
                
                # 크기
                if 'size' in row_text or 'diameter' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 2 <= cell <= 50:
                                data['size_nm'] = cell
                
                # PL peak
                if 'pl' in row_text or 'emission' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 350 <= cell <= 500:
                                data['PL_peak_nm'] = int(cell)
                
                # PLQY
                if 'plqy' in row_text or 'quantum yield' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 0 <= cell <= 100:
                                data['PLQY_percent'] = cell
                
                # FWHM
                if 'fwhm' in row_text or 'width' in row_text:
                    for cell in row:
                        if cell and isinstance(cell, (int, float)):
                            if 5 <= cell <= 100:
                                data['FWHM_nm'] = cell
        
        return data
    
    def extract_synthesis_conditions(self, text: str) -> Dict:
        """합성 조건 추출 (개선: 문맥 인식)"""
        data = {}
        
        # CsPbCl3 합성 섹션만 추출 시도 (확장: 5000자)
        synthesis_section = ""
        
        # "CsPbCl3 synthesis" 또는 "QD synthesis" 섹션 찾기
        synthesis_keywords = [
            r'synthesis\s+and\s+characterization',  # 가장 구체적
            r'cspbcl3.*?synthesis',
            r'quantum dot.*?synthesis',
            r'perovskite.*?synthesis',
            r'qd.*?preparation',
            r'experimental.*?section',
            r'methods.*?section',
        ]
        
        for keyword in synthesis_keywords:
            match = re.search(keyword, text, re.IGNORECASE | re.DOTALL)
            if match:
                # 매치된 위치부터 5000자 추출 (늘림)
                start = match.start()
                synthesis_section = text[start:start+5000]
                logger.debug(f"✅ 합성 섹션 발견: '{match.group()}'")
                break
        
        # 섹션을 찾지 못하면 전체 텍스트 사용
        if not synthesis_section:
            synthesis_section = text
            logger.debug("⚠️ 합성 섹션 특정 불가 - 전체 텍스트 사용")
        
        # 온도 추출 (개선: hot injection 근처만 + 패턴 3배 확장)
        temp_patterns = [
            # Hot injection 명시
            r'hot[- ]injection.*?(?:at|temperature|heated|to)\s*(\d{2,3})\s*[°º]?\s*C',
            r'hot[- ]inject(?:ed|ion).*?(\d{2,3})\s*[°º]?\s*C',
            r'(\d{2,3})\s*[°º]?\s*C.*?hot[- ]injection',
            
            # Temperature raised/increased
            r'temperature.*?(?:raised|increased|heated).*?(?:to|at)\s*(\d{2,3})\s*[°º]?\s*C',
            r'(?:raised|increased|heated).*?(?:to|at)\s*(\d{2,3})\s*[°º]?\s*C',
            r'(\d{2,3})\s*[°º]?\s*C.*?(?:raised|heated)',
            
            # Injection 일반
            r'inject(?:ed|ion).*?(?:at|temperature)\s*(\d{2,3})\s*[°º]?\s*C',
            r'temperature.*?(\d{2,3})\s*[°º]?\s*C.*?inject',
            r'(\d{2,3})\s*[°º]?\s*C.*?inject(?:ed|ion)',
            r'at\s*(\d{2,3})\s*[°º]?\s*C.*?(?:was|were)\s+inject',
            
            # Swift injection (변형)
            r'swift(?:ly)?.*?inject.*?(\d{2,3})\s*[°º]?\s*C',
            r'rapid(?:ly)?.*?inject.*?(\d{2,3})\s*[°º]?\s*C',
            
            # Cs precursor injection
            r'Cs[- ](?:oleate|precursor).*?inject.*?(\d{2,3})\s*[°º]?\s*C',
            r'inject.*?Cs[- ](?:oleate|precursor).*?(\d{2,3})\s*[°º]?\s*C',
            r'(\d{2,3})\s*[°º]?\s*C.*?Cs[- ](?:oleate|precursor).*?inject',
            
            # Synthesis temperature (문맥 필수)
            r'CsPbCl3.*?synthesized.*?(\d{2,3})\s*[°º]?\s*C',
            r'synthesized.*?CsPbCl3.*?(\d{2,3})\s*[°º]?\s*C',
            r'QDs.*?(?:formed|prepared|synthesized).*?(\d{2,3})\s*[°º]?\s*C',
            
            # Reaction temperature
            r'reaction temperature.*?(\d{2,3})\s*[°º]?\s*C',
            r'at\s*(\d{2,3})\s*[°º]?\s*C.*?(?:for|during).*?synthesis'
        ]
        
        for pattern in temp_patterns:
            match = re.search(pattern, synthesis_section, re.IGNORECASE)
            if match:
                temp = float(match.group(1))
                # 합리적인 범위 검증
                if 100 <= temp <= 250:
                    data['injection_temp_C'] = temp
                    logger.debug(f"✅ 온도 추출: {temp}°C (패턴: hot-injection)")
                    break
        
        # Cs 전구체 (확장: 화학식 + 이름 + 약어)
        cs_patterns = [
            (r'Cs2CO3', 'Cs2CO3'),
            (r'cesium\s+carbonate', 'Cs2CO3'),
            (r'CsOAc', 'CsOAc'),
            (r'Cs-OAc', 'CsOAc'),
            (r'cesium\s+acetate', 'CsOAc'),
            (r'Cs[- ]oleate', 'Cs-oleate'),
            (r'cesium\s+oleate', 'Cs-oleate'),
            (r'CsOA', 'Cs-oleate'),
            (r'Cs\s+precursor', 'Cs-precursor'),
        ]
        
        for pattern, source_name in cs_patterns:
            if re.search(pattern, synthesis_section, re.IGNORECASE):
                data['Cs_source'] = source_name
                logger.debug(f"✅ Cs source: {source_name}")
                break
        
        # Pb 전구체 (확장: 화학식 + 이름 + 변형)
        pb_patterns = [
            (r'PbCl2', 'PbCl2'),
            (r'PbCl₂', 'PbCl2'),  # 아래첨자
            (r'lead\s+chloride', 'PbCl2'),
            (r'lead\(II\)\s+chloride', 'PbCl2'),
            (r'lead\s*\(2\+\)\s+chloride', 'PbCl2'),
            (r'Pb[- ]chloride', 'PbCl2'),
        ]
        
        for pattern, source_name in pb_patterns:
            if re.search(pattern, synthesis_section, re.IGNORECASE):
                data['Pb_source'] = source_name
                logger.debug(f"✅ Pb source: {source_name}")
                break
        
        # Cl 전구체
        data['Cl_source'] = data.get('Pb_source', 'PbCl2')
        
        # 양 추출 (mmol) - CsPbCl3 합성 섹션에서만
        amount_patterns = [
            r'(\d+\.?\d*)\s*mmol.*?(?:PbCl2|lead chloride)',
            r'PbCl2.*?(\d+\.?\d*)\s*mmol',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, synthesis_section, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                if 0.01 <= amount <= 10:  # 합리적인 범위
                    data['Pb_amount_mmol'] = amount
                    break
        
        # 리간드 추출 (OA, OLA, ODE)
        ligand_patterns = {
            'OA_volume_ml': [r'oleic acid.*?(\d+\.?\d*)\s*(?:ml|mL|μL)', 
                            r'OA.*?(\d+\.?\d*)\s*(?:ml|mL|μL)'],
            'OLA_volume_ml': [r'oleylamine.*?(\d+\.?\d*)\s*(?:ml|mL|μL)',
                             r'OLA.*?(\d+\.?\d*)\s*(?:ml|mL|μL)'],
            'ODE_volume_ml': [r'octadecene.*?(\d+\.?\d*)\s*(?:ml|mL|μL)',
                             r'ODE.*?(\d+\.?\d*)\s*(?:ml|mL|μL)']
        }
        
        for key, patterns in ligand_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    volume = float(match.group(1))
                    # μL -> mL 변환
                    if 'μL' in match.group(0) or 'uL' in match.group(0):
                        volume = volume / 1000
                    data[key] = volume
                    break
        
        # 반응 시간 (min)
        time_patterns = [
            r'(\d+\.?\d*)\s*min',
            r'(\d+\.?\d*)\s*minutes',
            r'(\d+\.?\d*)\s*h(?:our)?'  # 시간도 추출
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_val = float(match.group(1))
                if 'h' in pattern:
                    time_val *= 60  # 시간 -> 분
                data['reaction_time_min'] = time_val
                break
        
        # 합성 방법 추출
        method_keywords = {
            'hot-injection': ['hot injection', 'hot-injection', 'injection method'],
            'room-temperature': ['room temperature', 'RT synthesis', 'ambient'],
            'microwave': ['microwave', 'MW synthesis'],
            'sonication': ['sonication', 'ultrasonic', 'sonochemical']
        }
        
        for method, keywords in method_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text, re.IGNORECASE):
                    data['synthesis_method'] = method
                    break
            if 'synthesis_method' in data:
                break
        
        return data
    
    def extract_qd_properties(self, text: str) -> Dict:
        """QD 특성 추출"""
        data = {}
        
        # 크기 (nm)
        size_patterns = [
            r'size.*?(\d+\.?\d*)\s*nm',
            r'diameter.*?(\d+\.?\d*)\s*nm',
            r'(\d+\.?\d*)\s*nm.*?(?:size|diameter|particle)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['size_nm'] = float(match.group(1))
                break
        
        # PL peak (nm)
        pl_patterns = [
            r'PL.*?(\d{3})\s*nm',
            r'emission.*?(\d{3})\s*nm',
            r'photoluminescence.*?(\d{3})\s*nm'
        ]
        
        for pattern in pl_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                wavelength = int(match.group(1))
                if 350 <= wavelength <= 500:  # CsPbCl3 범위
                    data['PL_peak_nm'] = wavelength
                    break
        
        # PLQY (%)
        plqy_patterns = [
            r'PLQY.*?(\d+\.?\d*)\s*%',
            r'quantum yield.*?(\d+\.?\d*)\s*%',
            r'QY.*?(\d+\.?\d*)\s*%'
        ]
        
        for pattern in plqy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                qy = float(match.group(1))
                if 0 <= qy <= 100:
                    data['PLQY_percent'] = qy
                    break
        
        # FWHM (nm)
        fwhm_patterns = [
            r'FWHM.*?(\d+\.?\d*)\s*nm',
            r'full width.*?(\d+\.?\d*)\s*nm'
        ]
        
        for pattern in fwhm_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['FWHM_nm'] = float(match.group(1))
                break
        
        # Absorption peak (nm)
        abs_patterns = [
            r'absorption.*?(\d{3})\s*nm',
            r'absorbance.*?(\d{3})\s*nm',
            r'1S.*?(\d{3})\s*nm'
        ]
        
        for pattern in abs_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                wavelength = int(match.group(1))
                if 300 <= wavelength <= 450:
                    data['abs_1S_peak_nm'] = wavelength
                    break
        
        return data
    
    def extract_metadata(self, doi: str, text: str) -> Dict:
        """메타데이터 추출 (CrossRef API 사용)"""
        try:
            url = f"https://api.crossref.org/works/{doi}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()['message']
                
                authors = data.get('author', [])
                author_names = [f"{a.get('given', '')} {a.get('family', '')}" 
                               for a in authors[:3]]  # 처음 3명만
                
                return {
                    'year': data.get('published', {}).get('date-parts', [[0]])[0][0],
                    'authors': ', '.join(author_names),
                    'journal': data.get('container-title', ['Unknown'])[0][:50]
                }
        except Exception as e:
            logger.error(f"❌ 메타데이터 추출 실패: {e}")
        
        return {
            'year': 2024,
            'authors': 'Unknown',
            'journal': 'Unknown'
        }
    
    def extract_all_data(self, doi: str, paper_id: str) -> Dict:
        """논문에서 모든 데이터 추출 (전체 파이프라인 - 개선: 표 우선)"""
        logger.info(f"🔬 데이터 추출 시작: {doi}")
        
        # 1. PDF 다운로드 시도
        pdf_path = self.download_pdf(doi)
        
        if not pdf_path:
            logger.warning(f"⚠️  PDF 없음, 메타데이터만 저장: {doi}")
            metadata = self.extract_metadata(doi, "")
            return {
                'paper_id': paper_id,
                'doi': doi,
                **metadata,
                'notes': 'PDF not available - metadata only'
            }
        
        # 2. 텍스트 추출
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            logger.warning(f"⚠️  텍스트 추출 실패: {doi}")
            return None
        
        # 3. 표 추출 (새로운 기능 - 우선순위 1)
        logger.info("📊 표 추출 시도...")
        tables = self.extract_tables_from_pdf(pdf_path)
        
        table_synthesis = {}
        table_properties = {}
        
        if tables:
            table_synthesis = self.parse_synthesis_from_table(tables)
            table_properties = self.parse_properties_from_table(tables)
            
            if table_synthesis:
                logger.info(f"   ✅ 표에서 합성 조건 {len(table_synthesis)}개 추출")
            if table_properties:
                logger.info(f"   ✅ 표에서 QD 특성 {len(table_properties)}개 추출")
        
        # 4. 텍스트에서 추출 (표에서 못 찾은 것만)
        logger.info("📝 텍스트에서 추출...")
        metadata = self.extract_metadata(doi, text)
        text_synthesis = self.extract_synthesis_conditions(text)
        text_properties = self.extract_qd_properties(text)
        
        # 5. 통합 (표 데이터 우선, 텍스트로 보완)
        synthesis = {**text_synthesis, **table_synthesis}  # 표가 텍스트를 덮어씀
        properties = {**text_properties, **table_properties}
        
        result = {
            'paper_id': paper_id,
            'doi': doi,
            **metadata,
            **synthesis,
            **properties
        }
        
        # 6. 추출된 필드 로깅
        extracted_fields = [k for k, v in result.items() 
                           if v is not None and k not in ['paper_id', 'doi', 'year', 'authors', 'journal']]
        
        if extracted_fields:
            logger.info(f"✅ 추출 완료: {len(extracted_fields)}개 필드")
            logger.info(f"   합성: {[f for f in extracted_fields if f in ['injection_temp_C', 'Pb_amount_mmol', 'OA_volume_ml', 'OLA_volume_ml', 'ODE_volume_ml']]}")
            logger.info(f"   특성: {[f for f in extracted_fields if f in ['size_nm', 'PL_peak_nm', 'PLQY_percent', 'FWHM_nm']]}")
        else:
            logger.warning("⚠️ 데이터 필드 추출 없음")
        
        return result


def test_extractor():
    """추출기 테스트"""
    extractor = PDFDataExtractor(Path("pdf/downloaded"))
    
    # 테스트 DOI (오픈액세스)
    test_doi = "10.1038/srep45906"
    
    result = extractor.extract_all_data(test_doi, "TEST001")
    
    print("\n" + "="*80)
    print("📊 추출 결과:")
    print("="*80)
    for key, value in result.items():
        if value is not None:
            print(f"  {key}: {value}")
    print("="*80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_extractor()
