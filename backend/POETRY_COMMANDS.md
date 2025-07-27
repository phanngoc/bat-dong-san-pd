# 🎭 Poetry Commands - Nhatot Crawler

Hướng dẫn sử dụng poetry commands để chạy crawler bất động sản.

## 📦 Setup

```bash
# Cài đặt dependencies
poetry install

# Activate virtual environment
poetry shell
```

## 🚀 Commands Available

### 1. Crawler chính
```bash
# Chạy crawler với cấu hình mặc định (5 trang)
poetry run crawler

# Tương đương với:
# cd crawler && python index.py
```

### 2. Test crawler
```bash
# Chạy test để kiểm tra setup
poetry run test-crawler

# Tương đương với:
# cd crawler && python test_crawler.py
```

### 3. Crawler với options
```bash
# Chạy crawler với các tùy chọn
poetry run crawler-run --help

# Ví dụ:
poetry run crawler-run --pages 10
poetry run crawler-run --pages 5 --output my_data.csv
poetry run crawler-run --url ws://remote:3000

# Tương đương với:
# cd crawler && python run_crawler.py --pages 10
```

### 4. Backend API (có sẵn)
```bash
# Chạy development server
poetry run dev

# Chạy production server
poetry run start

# Train model ML
poetry run train
```

## 🔧 Workflow khuyến nghị

### Lần đầu setup:
```bash
# 1. Setup poetry
poetry install

# 2. Setup browserless
cd crawler
./start_browserless.sh

# 3. Test crawler
cd ..
poetry run test-crawler
```

### Sử dụng hàng ngày:
```bash
# Kiểm tra browserless
cd crawler && ./start_browserless.sh --status

# Chạy crawler
poetry run crawler

# Hoặc với options tùy chỉnh
poetry run crawler-run --pages 10 --output today_data.csv
```

## 🎯 Lợi ích Poetry Commands

✅ **Đơn giản**: Không cần `cd` vào thư mục crawler  
✅ **Consistent**: Dùng cùng một virtual environment  
✅ **Portable**: Có thể chạy từ bất kỳ đâu trong project  
✅ **Documented**: Tất cả commands được list trong pyproject.toml  

## 🐛 Troubleshooting

### ImportError khi chạy poetry commands
```bash
# Reinstall dependencies
poetry install --no-cache

# Check package structure
poetry run python -c "import crawler; print(crawler.__version__)"
```

### Browserless not found
```bash
# Start browserless first
cd crawler
./start_browserless.sh

# Then run crawler
cd ..
poetry run test-crawler
```

## 📝 So sánh commands

| Task | Direct Python | Poetry |
|------|---------------|--------|
| Chạy crawler | `cd crawler && python index.py` | `poetry run crawler` |
| Test setup | `cd crawler && python test_crawler.py` | `poetry run test-crawler` |
| Với options | `cd crawler && python run_crawler.py --pages 10` | `poetry run crawler-run --pages 10` |
| Dev server | `cd src && uvicorn app:app --reload` | `poetry run dev` |

Poetry commands giúp workflow sạch sẽ và professional hơn! 🎉 