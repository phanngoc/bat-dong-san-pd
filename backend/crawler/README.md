# Crawler Bất Động Sản Nhatot.com

Script crawler sử dụng [browserless](https://github.com/browserless/browserless) để thu thập dữ liệu bất động sản từ nhatot.com

## Tính năng

- ✅ Crawl dữ liệu bất động sản Đà Nẵng từ nhatot.com
- ✅ Crawl theo page (page=1, page=2, ...) thay vì scroll
- ✅ Sử dụng pyppeteer để connect browserless
- ✅ Extract thông tin chi tiết: tiêu đề, giá, diện tích, vị trí, URL, ảnh, etc.
- ✅ Lưu dữ liệu vào file CSV với timestamp
- ✅ Delay giữa các trang để tránh bị block

## Cài đặt

### 1. Setup Browserless Service

Chạy browserless bằng Docker:

```bash
# Pull và chạy browserless
docker run -p 3000:3000 ghcr.io/browserless/chromium

# Hoặc chạy ở background
docker run -d -p 3000:3000 ghcr.io/browserless/chromium
```

### 2. Cài đặt Dependencies

```bash
# Từ thư mục backend
cd backend

# Cài đặt bằng pip
pip install -r requirements.txt

# Hoặc cài đặt bằng poetry
poetry install
```

## Sử dụng

### Chạy crawler

```bash
# Từ thư mục crawler
cd backend/crawler

# Chạy script
python index.py
```

### Output

Script sẽ tạo file CSV với format:
- `real_estate_data_YYYYMMDD_HHMMSS.csv`

Các cột dữ liệu:
- `title`: Tiêu đề bất động sản
- `price`: Giá bán
- `area`: Diện tích
- `location`: Địa chỉ/vị trí
- `description`: Mô tả
- `url`: Link đến chi tiết
- `image_url`: URL ảnh
- `posted_date`: Ngày đăng
- `property_type`: Loại bất động sản
- `bedrooms`: Số phòng ngủ
- `bathrooms`: Số phòng tắm
- `page_number`: Số trang được crawl
- `item_index`: Thứ tự item trong trang
- `scraped_at`: Thời gian crawl

## Cấu hình

Bạn có thể tùy chỉnh các tham số trong file `index.py`:

```python
# URL browserless service và số trang tối đa
crawler = NhatotRealEstateCrawler("ws://localhost:3000", max_pages=5)

# Crawl từ page 1 đến page 5
# URL pattern: https://www.nhatot.com/mua-ban-bat-dong-san-da-nang?page=2
```

## Lưu ý

1. **Browserless service**: Đảm bảo browserless đang chạy trên port 3000
2. **Rate limiting**: Nhatot.com có thể có rate limiting, hãy sử dụng có trách nhiệm
3. **Selectors**: CSS selectors có thể thay đổi theo thời gian, cần cập nhật nếu cần
4. **Robot.txt**: Tuân thủ robots.txt và terms of service của trang web

## Troubleshooting

### Lỗi kết nối browserless
```
❌ Lỗi kết nối: [Errno 61] Connection refused
```
- Kiểm tra browserless service có đang chạy không
- Kiểm tra port 3000 có bị block không

### Không extract được dữ liệu
```
🏠 Tìm thấy 0 bất động sản
```
- CSS selectors có thể đã thay đổi
- Trang web có thể có captcha hoặc bot detection
- Cần cập nhật logic extract

### Script chạy chậm
- Giảm số trang: `max_pages=3`
- Tối ưu CSS selectors
- Kiểm tra kết nối mạng

## Todo

- [ ] Thêm support cho nhiều thành phố khác
- [ ] Implement retry mechanism
- [ ] Thêm proxy support
- [ ] Optimize performance
- [ ] Thêm database storage option 