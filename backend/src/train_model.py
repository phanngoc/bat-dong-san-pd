import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import joblib
import numpy as np

def main():
    """Hàm chính để train model dự đoán giá bất động sản"""
    # Đọc dữ liệu
    df = pd.read_csv('real_estate_data.csv')
    df = df.dropna()

    # Tính giá mỗi m2
    df['price_per_m2'] = df['price'] / df['area']

    # Tính tuổi nhà
    current_year = 2024
    df['building_age'] = current_year - df['year_built']

    # Mã hóa các biến categorical
    le_district = LabelEncoder()
    le_type = LabelEncoder()
    le_facing = LabelEncoder()

    df['district_encoded'] = le_district.fit_transform(df['district'])
    df['type_encoded'] = le_type.fit_transform(df['type'])
    df['facing_encoded'] = le_facing.fit_transform(df['facing_direction'])

    # Tạo feature tỷ lệ floor
    df['floor_ratio'] = df['floor'] / df['total_floors']

    # Tạo feature density (mật độ dân số khu vực)
    df['area_density'] = df['nearby_price_count'] / (df['distance_to_center_km'] + 1)

    # Tạo feature tổng hợp về khoảng cách đến các tiện ích
    df['avg_distance_to_amenities'] = (
        df['distance_to_metro_km'] + 
        df['distance_to_school_km'] + 
        df['distance_to_hospital_km'] + 
        df['distance_to_mall_km']
    ) / 4

    # Tạo feature về tỷ lệ giá so với khu vực
    df['price_vs_nearby_ratio'] = df['price_per_m2'] / (df['nearby_avg_price_per_m2'] + 1)

    # Chọn features để train
    feature_columns = [
        'latitude', 'longitude', 'bedrooms', 'bathrooms', 'area',
        'district_encoded', 'type_encoded', 'facing_encoded',
        'building_age', 'floor', 'total_floors', 'floor_ratio',
        'parking', 'condition_score',
        'distance_to_center_km', 'distance_to_metro_km', 
        'distance_to_school_km', 'distance_to_hospital_km', 'distance_to_mall_km',
        'avg_distance_to_amenities', 'area_density',
        'nearby_avg_price_per_m2', 'nearby_price_count', 'price_vs_nearby_ratio'
    ]

    X = df[feature_columns]
    y = df['price_per_m2']

    # Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Chia dữ liệu train/test
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Huấn luyện model XGBoost với hyperparameters tốt hơn
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)

    # Đánh giá model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print(f"Train R² Score: {train_score:.4f}")
    print(f"Test R² Score: {test_score:.4f}")

    # Hiển thị feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\nTop 10 Feature Importance:")
    print(feature_importance.head(10))

    # Lưu model và các encoder
    joblib.dump(model, "xgb_model.pkl")
    joblib.dump(scaler, "scaler.pkl")
    joblib.dump(le_district, "label_encoder_district.pkl")
    joblib.dump(le_type, "label_encoder_type.pkl")
    joblib.dump(le_facing, "label_encoder_facing.pkl")

    # Lưu danh sách features để sử dụng khi predict
    joblib.dump(feature_columns, "feature_columns.pkl")

    print("\nModel và encoders đã được lưu thành công!")
    print("Các file được tạo:")
    print("- xgb_model.pkl")
    print("- scaler.pkl") 
    print("- label_encoder_district.pkl")
    print("- label_encoder_type.pkl")
    print("- label_encoder_facing.pkl")
    print("- feature_columns.pkl")

if __name__ == "__main__":
    main()
