#!/usr/bin/env python3
"""
Script test để kiểm tra crawler hoạt động
"""

import asyncio
import sys
from .index import NhatotRealEstateCrawler


async def test_connection():
    """Test kết nối browserless"""
    print("🧪 Test 1: Kiểm tra kết nối browserless...")
    
    crawler = NhatotRealEstateCrawler(max_pages=1)
    
    try:
        success = await crawler.connect_browser()
        if success:
            print("✅ Kết nối browserless thành công!")
            await crawler.browser.disconnect()
            return True
        else:
            print("❌ Kết nối browserless thất bại!")
            return False
    except Exception as e:
        print(f"❌ Lỗi test kết nối: {e}")
        return False


async def test_page_navigation():
    """Test navigate to page"""
    print("\n🧪 Test 2: Kiểm tra navigate trang...")
    
    crawler = NhatotRealEstateCrawler(max_pages=1)
    
    try:
        # Connect
        if not await crawler.connect_browser():
            return False
        
        # Create page
        if not await crawler.create_page():
            return False
        
        # Navigate
        success = await crawler.navigate_to_page(
            "https://www.nhatot.com/mua-ban-bat-dong-san-da-nang", 
            1
        )
        
        if success:
            print("✅ Navigate trang thành công!")
            # Check page exists
            has_data = await crawler.check_page_exists(1)
            print(f"📊 Trang có dữ liệu: {'✅' if has_data else '❌'}")
            
            await crawler.page.close()
            await crawler.browser.disconnect()
            return has_data
        else:
            print("❌ Navigate trang thất bại!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test navigation: {e}")
        return False


async def test_data_extraction():
    """Test extract dữ liệu"""
    print("\n🧪 Test 3: Kiểm tra extract dữ liệu...")
    
    crawler = NhatotRealEstateCrawler(max_pages=1)
    
    try:
        success = await crawler.crawl_nhatot_danang()
        
        if success and len(crawler.scraped_data) > 0:
            print(f"✅ Extract dữ liệu thành công: {len(crawler.scraped_data)} items")
            
            # Hiển thị 1 item mẫu
            sample = crawler.scraped_data[0]
            print("\n📝 Dữ liệu mẫu:")
            for key, value in sample.items():
                if value:  # Chỉ hiển thị field có dữ liệu
                    print(f"   {key}: {str(value)[:100]}...")
            
            return True
        else:
            print("❌ Không extract được dữ liệu!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test extraction: {e}")
        return False


async def run_all_tests():
    """Chạy tất cả tests"""
    print("🚀 Bắt đầu test crawler...")
    print("=" * 60)
    
    tests = [
        ("Kết nối browserless", test_connection),
        ("Navigate trang", test_page_navigation), 
        ("Extract dữ liệu", test_data_extraction)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Lỗi test {test_name}: {e}")
            results.append((test_name, False))
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 Kết quả test:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tổng cộng: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Tất cả tests đều PASS! Crawler sẵn sàng sử dụng.")
        return True
    else:
        print("⚠️  Một số tests FAIL. Vui lòng kiểm tra lại setup.")
        return False


def main():
    """Main function"""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests bị dừng bởi người dùng")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 