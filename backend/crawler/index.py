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
        
        # Tìm các item bất động sản với nhiều selector khác nhau
        selectors = [
            'div[class*="AdItem_adItem"]',
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
            '[class*="property"]',
            'div[class*="card"]',
            'li[class*="item"]'
        ]
        
        property_items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                property_items = items
                print(f"✅ Sử dụng selector: {selector}")
                break
        
        if not property_items:
            # Fallback 1: tìm tất cả links có href chứa bat-dong-san
            property_items = soup.find_all('a', href=re.compile(r'.*bat-dong-san.*', re.I))
            if property_items:
                print("✅ Sử dụng fallback: links chứa 'bat-dong-san'")
            
        if not property_items:
            # Fallback 2: tìm tất cả divs có chứa text giá tiền
            property_items = soup.find_all('div', string=re.compile(r'.*tỷ.*|.*triệu.*|.*million.*', re.I))
            if property_items:
                print("✅ Sử dụng fallback: divs chứa giá tiền")
                
        if not property_items:
            # Fallback 3: tìm tất cả articles
            property_items = soup.find_all('article')
            if property_items:
                print("✅ Sử dụng fallback: article tags")
                
        if not property_items:
            # Fallback 4: tìm tất cả divs có class chứa 'item' hoặc 'card'
            property_items = soup.find_all('div', class_=re.compile(r'.*item.*|.*card.*', re.I))
            if property_items:
                print("✅ Sử dụng fallback: divs với class item/card")
            
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
        """Extract thông tin từ một item bất động sản"""
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
        
        # Tìm parent container nếu cần
        container = item
        for _ in range(3):  # Tìm trong 3 level parent
            parent = container.parent if container.parent else container
            if parent.find('a', href=True):
                container = parent
                break
            container = parent
        
        # Title - thử nhiều selector
        title_selectors = [
            'h3', 'h2', 'h4', 'h5',
            '[class*="title"]', '[class*="heading"]', 
            '[class*="subject"]', '[class*="name"]'
        ]
        
        for selector in title_selectors:
            title_elem = container.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                property_data['title'] = title_elem.get_text(strip=True)
                break
        
        # Nếu không tìm được title, thử tìm text trong links
        if not property_data['title']:
            link_elem = container.find('a')
            if link_elem:
                property_data['title'] = link_elem.get_text(strip=True)
        
        # Price - tìm text chứa tiền
        price_patterns = [r'.*tỷ.*', r'.*triệu.*', r'.*đồng.*', r'.*VND.*', r'.*million.*']
        for pattern in price_patterns:
            price_elem = container.find(text=re.compile(pattern, re.I))
            if price_elem:
                property_data['price'] = price_elem.strip()
                break
        
        # Nếu không tìm được, thử tìm trong span/div có class chứa price
        if not property_data['price']:
            price_elem = container.find(['span', 'div'], class_=re.compile(r'.*price.*|.*gia.*', re.I))
            if price_elem:
                property_data['price'] = price_elem.get_text(strip=True)
        
        # Area - tìm text chứa m²
        area_elem = container.find(text=re.compile(r'.*m².*|.*m2.*|.*diện tích.*', re.I))
        if area_elem:
            property_data['area'] = area_elem.strip()
        
        # Location - tìm địa chỉ
        location_selectors = [
            '[class*="location"]', '[class*="address"]', 
            '[class*="dia-chi"]', '[class*="diadiem"]'
        ]
        for selector in location_selectors:
            location_elem = container.select_one(selector)
            if location_elem:
                property_data['location'] = location_elem.get_text(strip=True)
                break
        
        # URL
        link_elem = container.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if href.startswith('/'):
                property_data['url'] = f"https://www.nhatot.com{href}"
            elif not href.startswith('http'):
                property_data['url'] = f"https://www.nhatot.com/{href}"
            else:
                property_data['url'] = href
        
        # Image URL
        img_elem = container.find('img', src=True)
        if img_elem:
            src = img_elem['src']
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
