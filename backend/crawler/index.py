import asyncio
import csv
import time
from datetime import datetime
from typing import List, Dict, Any
from pyppeteer import connect
from bs4 import BeautifulSoup
import re


class NhatotRealEstateCrawler:
    def __init__(self, browserless_url: str = "ws://localhost:3000", max_pages: int = 5):
        """
        Khởi tạo crawler với browserless service
        
        Args:
            browserless_url: URL của browserless service (mặc định localhost:3000)
            max_pages: Số trang tối đa để crawl (mặc định 5)
        """
        self.browserless_url = browserless_url
        self.max_pages = max_pages
        self.browser = None
        self.page = None
        self.scraped_data = []
        
    async def connect_browser(self):
        """Kết nối đến browserless service bằng pyppeteer"""
        try:
            print("🔗 Đang kết nối đến browserless service...")
            self.browser = await connect(
                browserWSEndpoint=self.browserless_url,
                defaultViewport={'width': 1920, 'height': 1080}
            )
            print("✅ Đã kết nối thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False
    
    async def create_page(self):
        """Tạo page mới"""
        try:
            self.page = await self.browser.newPage()
            
            # Set user agent để tránh bị phát hiện bot
            await self.page.setUserAgent(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            )
            
            # Set extra headers
            await self.page.setExtraHTTPHeaders({
                'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })
            
            print("✅ Đã tạo page thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi tạo page: {e}")
            return False
    
    async def navigate_to_page(self, url: str, page_num: int = 1):
        """Navigate đến trang web với page number"""
        try:
            if page_num > 1:
                url = f"{url}?page={page_num}"
            
            print(f"🌐 Đang truy cập trang {page_num}: {url}")
            
            # Navigate với timeout
            await self.page.goto(url, {
                'waitUntil': 'networkidle2',
                'timeout': 30000
            })
            
            # Chờ thêm một chút để trang load hoàn toàn
            await asyncio.sleep(2)
            
            print(f"✅ Đã tải trang {page_num} thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi tải trang {page_num}: {e}")
            return False
    
    async def wait_for_content(self):
        """Chờ content load"""
        try:
            # Thử nhiều selectors khác nhau
            selectors = [
                'div[class*="AdItem"]',
                'a[class*="AdItem"]', 
                'div[class*="ad-item"]',
                'div[data-testid*="ad"]',
                'div[class*="Item"]',
                'a[href*="/bat-dong-san"]',
                '.list-item',
                '[class*="listing"]'
            ]
            
            for selector in selectors:
                try:
                    await self.page.waitForSelector(selector, {'timeout': 3000})
                    print(f"✅ Content đã load với selector: {selector}")
                    return True
                except:
                    continue
            
            print("⚠️ Không tìm thấy content với selectors thông thường, tiếp tục anyway...")
            return True  # Tiếp tục crawl dù không tìm thấy specific selectors
        except Exception as e:
            print(f"⚠️ Lỗi chờ content: {e}")
            return True  # Vẫn tiếp tục
    
    async def get_page_content(self) -> str:
        """Lấy HTML content của trang"""
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            print(f"❌ Lỗi lấy content: {e}")
            return ""
    
    async def check_page_exists(self, page_num: int) -> bool:
        """Kiểm tra trang có tồn tại không (có data)"""
        try:
            # Kiểm tra page có còn live không
            if self.page.isClosed():
                print(f"⚠️ Page đã bị đóng tại trang {page_num}")
                return False
                
            # Đếm số lượng items trên trang với nhiều selectors
            items_count = await self.page.evaluate('''() => {
                const selectors = [
                    'div[class*="AdItem"]',
                    'a[class*="AdItem"]', 
                    'div[class*="ad-item"]',
                    'div[data-testid*="ad"]',
                    'div[class*="Item"]',
                    'a[href*="/bat-dong-san"]',
                    '.list-item',
                    '[class*="listing"]',
                    'div[class*="item"]',
                    'article',
                    '[class*="property"]'
                ];
                
                let maxCount = 0;
                for (const selector of selectors) {
                    try {
                        const items = document.querySelectorAll(selector);
                        maxCount = Math.max(maxCount, items.length);
                    } catch (e) {
                        continue;
                    }
                }
                return maxCount;
            }''')
            
            print(f"📊 Trang {page_num}: Tìm thấy {items_count} items")
            return items_count > 0
        except Exception as e:
            print(f"❌ Lỗi kiểm tra trang {page_num}: {e}")
            return False
    
    def extract_property_data(self, html_content: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract dữ liệu bất động sản từ HTML
        
        Args:
            html_content: HTML content của trang
            page_num: Số trang hiện tại
            
        Returns:
            List các dict chứa thông tin bất động sản
        """
        print(f"🔍 Đang extract dữ liệu từ trang {page_num}...")
        
        soup = BeautifulSoup(html_content, 'lxml')
        properties = []
        
        # Tìm container chính theo cấu trúc: div.list-view>div>div.ListAds_ListAds__ANK2d>ul>div
        main_container = soup.select_one('div.list-view div div.ListAds_ListAds__ANK2d ul')
        
        if not main_container:
            print("⚠️ Không tìm thấy container chính với selector div.ListAds_ListAds__ANK2d")
        else:
            # Tìm các div items trong container
            property_items = main_container.find_all('div', recursive=False)
            print(f"✅ Tìm thấy container chính, có {len(property_items)} items")
        
        if not property_items:
            print("⚠️ Không tìm thấy items nào")
            return properties
            
        print(f"🏠 Tìm thấy {len(property_items)} bất động sản trên trang {page_num}")
        
        for idx, item in enumerate(property_items):
            try:
                property_data = self._extract_single_property(item, page_num, idx + 1)
                if property_data and property_data.get('title'):  # Chỉ thêm nếu có title
                    properties.append(property_data)
            except Exception as e:
                print(f"⚠️ Lỗi extract property {idx + 1} trang {page_num}: {e}")
                continue
        
        print(f"✅ Extract thành công {len(properties)} bất động sản từ trang {page_num}")
        return properties
    
    def _extract_single_property(self, item, page_num: int, item_idx: int) -> Dict[str, Any]:
        """Extract thông tin từ một item bất động sản theo cấu trúc HTML mới sử dụng nth selectors"""
        property_data = {
            'title': '',
            'price': '',
            'area': '',
            'location': '',
            'description': '',
            'url': '',
            'image_url': '',
            'posted_date': '',
            'property_type': '',
            'bedrooms': '',
            'bathrooms': '',
            'page_number': page_num,
            'item_index': item_idx,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Tìm li element chứa itemListElement
        li_element = item.find('li', {'itemprop': 'itemListElement'})
        if not li_element:
            # Fallback: tìm trong chính item
            li_element = item
        
        # Tìm div chính chứa content (thường là div thứ 2 trong structure)
        main_content_div = li_element.select_one('a[itemprop="item"] > div:nth-child(2)')
        if not main_content_div:
            # Fallback: tìm div có chứa h3
            main_content_div = li_element.find('div', lambda value: value and li_element.find('h3'))
            if not main_content_div:
                main_content_div = li_element
        
        # Title - tìm h3 (thường là element đầu tiên trong content)
        title_elem = main_content_div.find('h3')
        if title_elem:
            property_data['title'] = title_elem.get_text(strip=True)
        
        # Property type - tìm span đầu tiên sau h3
        spans_in_content = main_content_div.find_all('span', recursive=False)
        if len(spans_in_content) >= 1:
            type_text = spans_in_content[0].get_text(strip=True)
            property_data['property_type'] = type_text
            # Extract bedrooms/bathrooms nếu có trong text
            if 'phòng ngủ' in type_text.lower():
                bedrooms_match = re.search(r'(\d+)\s*phòng ngủ', type_text, re.I)
                if bedrooms_match:
                    property_data['bedrooms'] = bedrooms_match.group(1)
            if 'phòng tắm' in type_text.lower() or 'wc' in type_text.lower():
                bathrooms_match = re.search(r'(\d+)\s*(?:phòng tắm|wc)', type_text, re.I)
                if bathrooms_match:
                    property_data['bathrooms'] = bathrooms_match.group(1)
        
        # Price và Area - tìm div chứa price info (thường là div thứ 2-3 trong content)
        price_div = main_content_div.find('div', lambda value: value and main_content_div.find('div').find_all('span'))
        
        if price_div:
            price_spans = price_div.find_all('span')
            for i, span in enumerate(price_spans):
                text = span.get_text(strip=True)
                style = span.get('style', '')
                
                # Price - thường là span đầu tiên hoặc span có màu đỏ
                if not property_data['price'] and (
                    i == 0 or 
                    'rgb(229, 25, 59)' in style or 
                    any(keyword in text.lower() for keyword in ['tỷ', 'triệu', 'đồng', 'vnd'])
                ):
                    property_data['price'] = text
                
                # Area - tìm span chứa m²
                if not property_data['area'] and ('m²' in text or 'm2' in text):
                    property_data['area'] = text
        
        # Location và posted date - tìm span cuối cùng trong content (thường chứa location • date)
        location_span = None
        all_spans = main_content_div.find_all('span')
        # Tìm span cuối cùng có chứa dấu •
        for span in reversed(all_spans):
            if '•' in span.get_text():
                location_span = span
                break
        
        if location_span:
            location_text = location_span.get_text(strip=True)
            # Split by • để tách location và date
            parts = [part.strip() for part in location_text.split('•')]
            if len(parts) >= 1:
                property_data['location'] = parts[0]
            if len(parts) >= 2:
                property_data['posted_date'] = parts[1]
        
        # URL - tìm link chính
        link_elem = li_element.find('a', {'itemprop': 'item'})
        if not link_elem:
            link_elem = li_element.find('a', href=True)
        
        if link_elem:
            href = link_elem.get('href', '')
            if href.startswith('/'):
                property_data['url'] = f"https://www.nhatot.com{href}"
            elif not href.startswith('http'):
                property_data['url'] = f"https://www.nhatot.com/{href}"
            else:
                property_data['url'] = href
        
        # Image URL - tìm img đầu tiên
        img_elem = li_element.find('img', src=True)
        if img_elem:
            src = img_elem.get('src', '')
            alt = img_elem.get('alt', '')
            # Sử dụng alt làm description nếu có
            if alt and not property_data.get('description'):
                property_data['description'] = alt
                
            if src.startswith('//'):
                property_data['image_url'] = f"https:{src}"
            elif src.startswith('/'):
                property_data['image_url'] = f"https://www.nhatot.com{src}"
            else:
                property_data['image_url'] = src
        
        return property_data
    
    def save_to_csv(self, filename: str = None):
        """Lưu dữ liệu vào file CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../real_estate_data_{timestamp}.csv"
        
        if not self.scraped_data:
            print("⚠️ Không có dữ liệu để lưu")
            return
        
        print(f"💾 Đang lưu {len(self.scraped_data)} bất động sản vào {filename}...")
        
        fieldnames = [
            'title', 'price', 'area', 'location', 'description', 
            'url', 'image_url', 'posted_date', 'property_type',
            'bedrooms', 'bathrooms', 'page_number', 'item_index', 'scraped_at'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.scraped_data)
        
        print(f"✅ Đã lưu thành công vào {filename}")
    
    async def crawl_nhatot_danang(self):
        """Crawl dữ liệu bất động sản Đà Nẵng từ nhatot.com theo pages"""
        base_url = "https://www.nhatot.com/mua-ban-bat-dong-san-da-nang"
        
        try:
            # Kết nối browser
            if not await self.connect_browser():
                return False
            
            # Tạo page
            if not await self.create_page():
                return False
            
            # Crawl từng trang
            for page_num in range(1, self.max_pages + 1):
                print(f"\n🔄 Đang crawl trang {page_num}/{self.max_pages}...")
                
                # Navigate đến trang
                if not await self.navigate_to_page(base_url, page_num):
                    print(f"❌ Không thể tải trang {page_num}, bỏ qua...")
                    continue
                
                # Chờ content load
                await self.wait_for_content()
                
                # Kiểm tra trang có data không
                if not await self.check_page_exists(page_num):
                    print(f"⚠️ Trang {page_num} không có dữ liệu, dừng crawl")
                    break
                
                # Lấy HTML content
                html_content = await self.get_page_content()
                
                if html_content:
                    # Extract dữ liệu
                    page_data = self.extract_property_data(html_content, page_num)
                    self.scraped_data.extend(page_data)
                    
                    print(f"✅ Crawl trang {page_num}: +{len(page_data)} bất động sản")
                else:
                    print(f"❌ Không thể lấy content từ trang {page_num}")
                
                # Delay giữa các trang để tránh bị block
                if page_num < self.max_pages:
                    print(f"⏳ Chờ 2s trước khi crawl trang tiếp theo...")
                    await asyncio.sleep(2)
            
            # Lưu dữ liệu
            if self.scraped_data:
                self.save_to_csv()
                print(f"🎉 Crawl hoàn thành! Tổng cộng: {len(self.scraped_data)} bất động sản từ {page_num} trang")
                return True
            else:
                print("⚠️ Không crawl được dữ liệu nào")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình crawl: {e}")
            return False
        finally:
            try:
                if self.page and not self.page.isClosed():
                    await self.page.close()
                    print("🔐 Đã đóng page")
            except Exception as e:
                print(f"⚠️ Lỗi đóng page: {e}")
            
            try:
                if self.browser:
                    await self.browser.disconnect()
                    print("🔐 Đã đóng kết nối browser")
            except Exception as e:
                print(f"⚠️ Lỗi đóng browser: {e}")


async def async_main():
    """Hàm async main để chạy crawler"""
    print("🚀 Bắt đầu crawl dữ liệu bất động sản Đà Nẵng từ nhatot.com")
    print("📄 Crawl theo pages thay vì scroll")
    print("=" * 60)
    
    # Khởi tạo crawler với 5 trang
    crawler = NhatotRealEstateCrawler(max_pages=5)
    
    # Chạy crawler
    success = await crawler.crawl_nhatot_danang()
    
    if success:
        print("✅ Crawl hoàn thành thành công!")
    else:
        print("❌ Crawl thất bại!")
    
    print("=" * 60)
    return success


def main():
    """Entry point function for poetry scripts"""
    import sys
    try:
        success = asyncio.run(async_main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Crawler bị dừng bởi người dùng")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Chạy crawler
    main()
