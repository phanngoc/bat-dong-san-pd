#!/bin/bash

# Script để khởi chạy Backend API Bất Động Sản ở chế độ Development với Poetry
# Author: Auto-generated script

set -e  # Dừng script nếu có lỗi

echo "🏠 Đang khởi chạy Backend API Bất Động Sản (Development Mode)..."

# Kiểm tra Poetry có được cài đặt không
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry chưa được cài đặt. Vui lòng cài đặt Poetry trước khi chạy script này."
    echo "Hướng dẫn cài đặt: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✅ Poetry đã được cài đặt."

# Cài đặt dependencies nếu chưa có
echo "📦 Đang kiểm tra và cài đặt dependencies..."
poetry install

# Kiểm tra xem model đã được train chưa
if [ ! -f "xgb_model.pkl" ]; then
    echo "🤖 Model chưa được train. Đang tiến hành training..."
    poetry run train
    echo "✅ Model đã được train thành công."
else
    echo "✅ Model đã có sẵn."
fi

echo "🚀 Đang khởi chạy server ở chế độ Development..."
echo "📍 Server sẽ chạy tại: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔄 Auto-reload đã được bật - server sẽ tự động restart khi có thay đổi code"
echo "🛑 Nhấn Ctrl+C để dừng server"

# Chạy server với poetry ở chế độ development (với reload)
PYTHONPATH=src poetry run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload 