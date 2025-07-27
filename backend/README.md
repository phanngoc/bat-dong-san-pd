# Real Estate Backend (FastAPI + Poetry)

## Cài đặt & chạy server bằng Poetry

1. Cài Poetry (nếu chưa có):
   ```sh
   pip install poetry
   ```
2. Cài dependencies:
   ```sh
   poetry install
   ```
3. Vào shell Poetry:
   ```sh
   poetry shell
   ```
4. Huấn luyện model (chạy 1 lần):
   ```sh
   python train_model.py
   ```
5. Chạy server FastAPI:
   ```sh
   uvicorn app:app --reload
   ```

## Lưu ý
- Đảm bảo Python >=3.8, <3.12
- Nếu thiếu package, thêm vào `[tool.poetry.dependencies]` rồi chạy lại `poetry install`
- Nếu lỗi version, kiểm tra lại version Python và các package

## Scripts Poetry (nâng cao)
Có thể thêm vào `[tool.poetry.scripts]` để chạy nhanh:
```toml
[tool.poetry.scripts]
serve = "uvicorn app:app --reload"
train = "python train_model.py"
```
Sau đó dùng:
```
poetry run serve
poetry run train
```
