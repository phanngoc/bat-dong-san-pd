from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os

app = FastAPI(title="Dự đoán giá bất động sản", description="API dự đoán giá bất động sản tại TP.HCM")

# Load model và các encoders
try:
    model = joblib.load("xgb_model.pkl")
    scaler = joblib.load("scaler.pkl")
    le_district = joblib.load("label_encoder_district.pkl")
    le_type = joblib.load("label_encoder_type.pkl")
    le_facing = joblib.load("label_encoder_facing.pkl")
    feature_columns = joblib.load("feature_columns.pkl")
except Exception as e:
    print(f"Lỗi khi load model: {e}")

class PredictRequest(BaseModel):
    latitude: float
    longitude: float
    area: float
    bedrooms: int
    bathrooms: int
    type: str  # apartment, house, villa
    district: str
    year_built: int
    floor: int
    total_floors: int
    parking: int  # 0 hoặc 1
    facing_direction: str  # North, South, East, West
    distance_to_center_km: float
    distance_to_metro_km: float
    distance_to_school_km: float
    distance_to_hospital_km: float
    distance_to_mall_km: float
    nearby_avg_price_per_m2: float
    nearby_price_count: int
    condition_score: float

class SimplePredictRequest(BaseModel):
    latitude: float
    longitude: float
    bedrooms: int
    district: str

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách Euclidean giữa 2 điểm"""
    return np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def load_real_estate_data():
    """Load dữ liệu bất động sản từ CSV"""
    try:
        df = pd.read_csv("real_estate_data.csv")
        return df
    except Exception as e:
        print(f"Lỗi khi load dữ liệu: {e}")
        return None

def normalize_district_name(district: str) -> str:
    """Chuẩn hóa tên quận về format trong dữ liệu training"""
    # Mapping từ tên có dấu sang tên không dấu
    district_mapping = {
        "Quận 1": "Quan 1",
        "Quận 2": "Quan 2", 
        "Quận 3": "Quan 3",
        "Quận 4": "Quan 4",
        "Quận 5": "Quan 5",
        "Quận 6": "Quan 6",
        "Quận 7": "Quan 7",
        "Quận 8": "Quan 8",
        "Quận 9": "Quan 9",
        "Quận 10": "Quan 10",
        "Quận 11": "Quan 11",
        "Quận 12": "Quan 12",
        "Quận Bình Thạnh": "Quan Binh Thanh",
        "Quận Phú Nhuận": "Quan Phu Nhuan",
        "Quận Tân Bình": "Quan Tan Binh",
        "Quận Tân Phú": "Quan Tan Phu",
        "Quận Gò Vấp": "Quan Go Vap",
        "Thành phố Thủ Đức": "Thu Duc",
        "Thủ Đức": "Thu Duc"
    }
    
    # Nếu có trong mapping thì convert, không thì giữ nguyên
    return district_mapping.get(district, district)

@app.post("/predict-price")
def predict_price(data: PredictRequest):
    try:
        # Chuẩn hóa tên district
        normalized_district = normalize_district_name(data.district)
        
        # Kiểm tra district có tồn tại trong training data không
        try:
            district_encoded = le_district.transform([normalized_district])[0]
        except ValueError:
            available_districts = list(le_district.classes_)
            raise HTTPException(
                status_code=400, 
                detail=f"District '{data.district}' không được hỗ trợ. Các district có sẵn: {available_districts}"
            )
        
        # Encode type và facing_direction
        try:
            type_encoded = le_type.transform([data.type])[0]
            facing_encoded = le_facing.transform([data.facing_direction])[0]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Giá trị không hợp lệ: {str(e)}")
        
        # Tính toán building_age
        current_year = 2024
        building_age = current_year - data.year_built
        
        # Tính toán floor_ratio
        floor_ratio = data.floor / data.total_floors if data.total_floors > 0 else 0
        
        # Tính toán avg_distance_to_amenities
        avg_distance_to_amenities = (
            data.distance_to_metro_km + 
            data.distance_to_school_km + 
            data.distance_to_hospital_km + 
            data.distance_to_mall_km
        ) / 4
        
        # Tính toán area_density
        area_density = data.nearby_price_count / (data.distance_to_center_km + 1)
        
        # Tính toán price_vs_nearby_ratio (sẽ được tính sau khi có prediction)
        # Tạm thời set = 1, sẽ cập nhật sau
        price_vs_nearby_ratio = 1.0
        
        # Tạo array features theo đúng thứ tự
        features = np.array([[
            data.latitude,
            data.longitude, 
            data.bedrooms,
            data.bathrooms,
            data.area,
            district_encoded,
            type_encoded,
            facing_encoded,
            building_age,
            data.floor,
            data.total_floors,
            floor_ratio,
            data.parking,
            data.condition_score,
            data.distance_to_center_km,
            data.distance_to_metro_km,
            data.distance_to_school_km,
            data.distance_to_hospital_km,
            data.distance_to_mall_km,
            avg_distance_to_amenities,
            area_density,
            data.nearby_avg_price_per_m2,
            data.nearby_price_count,
            price_vs_nearby_ratio
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict
        predicted_price_per_m2 = model.predict(features_scaled)[0]
        
        # Tính tổng giá
        total_estimated_price = predicted_price_per_m2 * data.area
        
        return {
            "estimated_price_per_m2": float(predicted_price_per_m2),
            "total_estimated_price": float(total_estimated_price),
            "area": data.area,
            "normalized_district": normalized_district
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự đoán: {str(e)}")

@app.post("/simple-predict-price")
def simple_predict_price(data: SimplePredictRequest):
    try:
        # Load dữ liệu bất động sản
        df = load_real_estate_data()
        if df is None:
            raise HTTPException(status_code=500, detail="Không thể load dữ liệu bất động sản")
        
        # Chuẩn hóa tên district
        normalized_district = normalize_district_name(data.district)
        
        # Kiểm tra district có tồn tại trong training data không
        try:
            district_encoded = le_district.transform([normalized_district])[0]
        except ValueError:
            available_districts = list(le_district.classes_)
            raise HTTPException(
                status_code=400, 
                detail=f"District '{data.district}' không được hỗ trợ. Các district có sẵn: {available_districts}"
            )
        
        # Tính khoảng cách đến tất cả các điểm trong dataset
        df['distance'] = df.apply(lambda row: calculate_distance(
            data.latitude, data.longitude, row['latitude'], row['longitude']
        ), axis=1)
        
        # Lọc các bất động sản có cùng số phòng ngủ hoặc gần số phòng ngủ yêu cầu
        # Ưu tiên cùng số phòng ngủ, nếu không có thì lấy ±1 phòng
        same_bedrooms = df[df['bedrooms'] == data.bedrooms]
        if len(same_bedrooms) >= 5:
            nearest_df = same_bedrooms.nsmallest(5, 'distance')
        else:
            # Nếu không đủ 5 căn cùng số phòng ngủ, lấy thêm căn ±1 phòng
            similar_bedrooms = df[df['bedrooms'].isin([data.bedrooms-1, data.bedrooms, data.bedrooms+1])]
            nearest_df = similar_bedrooms.nsmallest(5, 'distance')
        
        # Nếu vẫn không đủ 5 căn, lấy 5 căn gần nhất bất kể số phòng ngủ
        if len(nearest_df) < 5:
            nearest_df = df.nsmallest(5, 'distance')
        
        # Tính trung bình các thông số từ 5 điểm gần nhất
        avg_area = nearest_df['area'].mean()
        avg_bathrooms = int(round(nearest_df['bathrooms'].mean()))
        most_common_type = nearest_df['type'].mode()[0]
        avg_year_built = int(round(nearest_df['year_built'].mean()))
        avg_floor = int(round(nearest_df['floor'].mean()))
        avg_total_floors = int(round(nearest_df['total_floors'].mean()))
        avg_parking = int(round(nearest_df['parking'].mean()))
        most_common_facing = nearest_df['facing_direction'].mode()[0]
        avg_distance_to_center = nearest_df['distance_to_center_km'].mean()
        avg_distance_to_metro = nearest_df['distance_to_metro_km'].mean()
        avg_distance_to_school = nearest_df['distance_to_school_km'].mean()
        avg_distance_to_hospital = nearest_df['distance_to_hospital_km'].mean()
        avg_distance_to_mall = nearest_df['distance_to_mall_km'].mean()
        avg_nearby_price_per_m2 = nearest_df['nearby_avg_price_per_m2'].mean()
        avg_nearby_price_count = int(round(nearest_df['nearby_price_count'].mean()))
        avg_condition_score = nearest_df['condition_score'].mean()
        
        # Encode các thông số cần thiết
        try:
            type_encoded = le_type.transform([most_common_type])[0]
            facing_encoded = le_facing.transform([most_common_facing])[0]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Giá trị không hợp lệ: {str(e)}")
        
        # Tính toán các thông số phái sinh
        current_year = 2024
        building_age = current_year - avg_year_built
        floor_ratio = avg_floor / avg_total_floors if avg_total_floors > 0 else 0
        avg_distance_to_amenities = (
            avg_distance_to_metro + 
            avg_distance_to_school + 
            avg_distance_to_hospital + 
            avg_distance_to_mall
        ) / 4
        area_density = avg_nearby_price_count / (avg_distance_to_center + 1)
        price_vs_nearby_ratio = 1.0  # Tạm thời set = 1
        
        # Tạo array features theo đúng thứ tự
        features = np.array([[
            data.latitude,
            data.longitude, 
            data.bedrooms,
            avg_bathrooms,
            avg_area,
            district_encoded,
            type_encoded,
            facing_encoded,
            building_age,
            avg_floor,
            avg_total_floors,
            floor_ratio,
            avg_parking,
            avg_condition_score,
            avg_distance_to_center,
            avg_distance_to_metro,
            avg_distance_to_school,
            avg_distance_to_hospital,
            avg_distance_to_mall,
            avg_distance_to_amenities,
            area_density,
            avg_nearby_price_per_m2,
            avg_nearby_price_count,
            price_vs_nearby_ratio
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict
        predicted_price_per_m2 = model.predict(features_scaled)[0]
        
        # Tính tổng giá
        total_estimated_price = predicted_price_per_m2 * avg_area
        
        return {
            "estimated_price_per_m2": float(predicted_price_per_m2),
            "total_estimated_price": float(total_estimated_price),
            "area": float(avg_area),
            "normalized_district": normalized_district,
            "nearest_properties_used": len(nearest_df),
            "average_parameters_used": {
                "area": float(avg_area),
                "bathrooms": avg_bathrooms,
                "type": most_common_type,
                "year_built": avg_year_built,
                "floor": avg_floor,
                "total_floors": avg_total_floors,
                "parking": avg_parking,
                "facing_direction": most_common_facing,
                "condition_score": float(avg_condition_score)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự đoán: {str(e)}")

@app.get("/")
def root():
    return {"message": "API dự đoán giá bất động sản TP.HCM"}

@app.get("/districts")
def get_available_districts():
    """Trả về danh sách các quận có sẵn"""
    try:
        districts = list(le_district.classes_)
        return {"available_districts": districts}
    except:
        return {"error": "Không thể load danh sách districts"}

@app.get("/property-types")
def get_property_types():
    """Trả về danh sách loại bất động sản có sẵn"""
    try:
        types = list(le_type.classes_)
        return {"available_types": types}
    except:
        return {"error": "Không thể load danh sách property types"}

@app.get("/facing-directions")
def get_facing_directions():
    """Trả về danh sách hướng nhà có sẵn"""
    try:
        facings = list(le_facing.classes_)
        return {"available_facings": facings}
    except:
        return {"error": "Không thể load danh sách facing directions"}
