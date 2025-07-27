#!/usr/bin/env python3
"""
Script chạy crawler với các tùy chọn khác nhau
"""

import asyncio
import argparse
import sys
import time
from .index import NhatotRealEstateCrawler


def print_banner():
    """In banner chào mừng"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🏠 NHATOT CRAWLER 🏠                     ║
║              Crawler Bất Động Sản Việt Nam                  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_crawler_with_options(
    browserless_url: str,
    max_pages: int,
    output_file: str = None
):
    """
    Chạy crawler với các tùy chọn được chỉ định
    
    Args:
        browserless_url: URL của browserless service
        max_pages: Số trang tối đa để crawl
        output_file: Tên file output (optional)
    """
    print(f"⚙️  Cấu hình:")
    print(f"   📍 Browserless URL: {browserless_url}")
    print(f"   📄 Số trang tối đa: {max_pages}")
    if output_file:
        print(f"   📁 File output: {output_file}")
    print("-" * 60)
    
    # Khởi tạo crawler
    crawler = NhatotRealEstateCrawler(browserless_url, max_pages)
    
    # Tùy chỉnh output file nếu có
    if output_file:
        original_save = crawler.save_to_csv
        def custom_save():
            return original_save(output_file)
        crawler.save_to_csv = custom_save
    
    # Chạy crawler
    start_time = time.time()
    success = await crawler.crawl_nhatot_danang()
    end_time = time.time()
    
    print("-" * 60)
    print(f"⏱️  Thời gian thực hiện: {end_time - start_time:.2f} giây")
    
    return success


def main():
    """Hàm main với argument parsing"""
    parser = argparse.ArgumentParser(
        description="Crawler dữ liệu bất động sản từ nhatot.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python run_crawler.py                                    # Chạy với cấu hình mặc định
  python run_crawler.py --pages 10                        # Crawl 10 trang
  python run_crawler.py --output my_data.csv               # Lưu vào file tùy chỉnh
  python run_crawler.py --url ws://remote:3000             # Sử dụng browserless remote
        """
    )
    
    parser.add_argument(
        "--url", "-u",
        default="ws://localhost:3000",
        help="URL của browserless service (mặc định: ws://localhost:3000)"
    )
    
    parser.add_argument(
        "--pages", "-p",
        type=int,
        default=5,
        help="Số trang tối đa để crawl (mặc định: 5)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Tên file CSV output (mặc định: auto-generate với timestamp)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Chạy ở chế độ im lặng (ít log hơn)"
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.pages < 1 or args.pages > 50:
        print("❌ Số trang phải từ 1-50")
        sys.exit(1)
    
    # In banner nếu không ở chế độ quiet
    if not args.quiet:
        print_banner()
    
    # Chạy crawler
    try:
        success = asyncio.run(run_crawler_with_options(
            browserless_url=args.url,
            max_pages=args.pages,
            output_file=args.output
        ))
        
        if success:
            print("🎉 Crawler hoàn thành thành công!")
            sys.exit(0)
        else:
            print("❌ Crawler thất bại!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Crawler bị dừng bởi người dùng")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 