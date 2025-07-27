# 🚀 Quick Start - Nhatot Crawler

Hướng dẫn nhanh để crawl dữ liệu bất động sản từ nhatot.com

## ⚡ Setup Nhanh (< 5 phút)

### Bước 1: Setup Browserless Service
```bash
# Chạy script setup tự động
./start_browserless.sh

# Hoặc chạy manual
docker run -d -p 3000:3000 ghcr.io/browserless/chromium
```

### Bước 2: Cài Dependencies
```bash
# Cách 1: Sử dụng Poetry (khuyến nghị)
cd backend
poetry install

# Cách 2: Sử dụng pip
pip install -r requirements.txt
```

### Bước 3: Test Setup (Tùy chọn)
```bash
# Poetry commands (khuyến nghị)
poetry run test-crawler

# Hoặc direct Python
cd crawler
python test_crawler.py
```

### Bước 4: Chạy Crawler
```bash
# Poetry commands (khuyến nghị)
poetry run crawler                              # Cấu hình mặc định
poetry run crawler-run --pages 10               # Với options

# Hoặc direct Python
cd crawler
python index.py                                 # Cấu hình mặc định  
python run_crawler.py --pages 10                # Với options
```

## 📊 Kết Quả

Sau khi chạy thành công, bạn sẽ có:
- File CSV chứa dữ liệu bất động sản với timestamp
- Log chi tiết quá trình crawl
- Dữ liệu được lưu tại `../real_estate_data_YYYYMMDD_HHMMSS.csv`

## 🔧 Commands Hữu Ích

```bash
# Kiểm tra trạng thái browserless
./start_browserless.sh --status

# Xem logs browserless
./start_browserless.sh --logs

# Restart browserless
./start_browserless.sh --restart

# Dừng browserless
./start_browserless.sh --stop

# Test crawler setup
python test_crawler.py

# Chạy crawler với options
python run_crawler.py --help
```

## 🎯 Quick Examples

```bash
# Poetry commands (khuyến nghị)
poetry run crawler-run -p 10                    # Crawl 10 trang
poetry run crawler-run -o my_data.csv           # Lưu vào file tùy chỉnh
poetry run crawler-run -q                       # Chạy ở chế độ im lặng
poetry run crawler-run -u ws://remote:3000      # Sử dụng browserless remote

# Direct Python
python run_crawler.py -p 10                     # Crawl 10 trang
python run_crawler.py -o my_data.csv            # Lưu vào file tùy chỉnh
python run_crawler.py -q                        # Chạy ở chế độ im lặng
python run_crawler.py -u ws://remote-server:3000 # Sử dụng browserless remote
```

## ❗ Troubleshooting

**Lỗi kết nối:** Kiểm tra browserless có chạy không
```bash
curl http://localhost:3000/json/version
```

**Không có dữ liệu:** Website có thể đã thay đổi cấu trúc
- Xem logs để debug
- Kiểm tra selectors trong code

**Docker issues:** 
```bash
docker ps  # Kiểm tra containers
docker logs nhatot-browserless  # Xem logs
```

## 🏆 That's it!

Giờ bạn đã có thể crawl dữ liệu bất động sản từ nhatot.com! 

Để biết thêm chi tiết, xem `README.md` 📖 