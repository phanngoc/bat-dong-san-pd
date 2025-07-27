import React, { useState } from "react";
import axios from "axios";

const DISTRICTS = [
  "Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5", 
  "Quận 6", "Quận 7", "Quận 8", "Quận 9", "Quận 10",
  "Quận 11", "Quận 12", "Quận Bình Thạnh", "Quận Gò Vấp",
  "Quận Phú Nhuận", "Quận Tân Bình", "Quận Tân Phú",
  "Huyện Bình Chánh", "Huyện Hóc Môn", "Huyện Nhà Bè"
];

export default function App() {
  const [lat, setLat] = useState(10.762622);
  const [lon, setLon] = useState(106.660172);
  const [bedrooms, setBedrooms] = useState(2);
  const [district, setDistrict] = useState("Quận 1");
  const [price, setPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePredict = async () => {
    if (!lat || !lon || !bedrooms || !district) {
      setError("Vui lòng điền đầy đủ thông tin");
      return;
    }

    setLoading(true);
    setPrice(null);
    setError("");
    
    try {
      const res = await axios.post("/api/simple-predict-price", {
        latitude: lat,
        longitude: lon,
        bedrooms,
        district,
      });
      setPrice(res.data.estimated_price_per_m2);
    } catch (e) {
      setError("Lỗi khi dự đoán giá. Vui lòng thử lại.");
      console.error(e);
    }
    setLoading(false);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN').format(Math.round(price));
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🏠 Dự Đoán Giá Bất Động Sản</h1>
        <p style={styles.subtitle}>Nhập thông tin để dự đoán giá per m²</p>
      </div>

      <div style={styles.form}>
        <div style={styles.row}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>📍 Vĩ độ (Latitude)</label>
            <input 
              style={styles.input}
              type="number" 
              value={lat} 
              onChange={e => setLat(Number(e.target.value))} 
              step="0.000001"
              placeholder="VD: 10.762622"
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>📍 Kinh độ (Longitude)</label>
            <input 
              style={styles.input}
              type="number" 
              value={lon} 
              onChange={e => setLon(Number(e.target.value))} 
              step="0.000001"
              placeholder="VD: 106.660172"
            />
          </div>
        </div>

        <div style={styles.row}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>🛏️ Số phòng ngủ</label>
            <input 
              style={styles.input}
              type="number" 
              value={bedrooms} 
              onChange={e => setBedrooms(Number(e.target.value))} 
              min={1} 
              max={10}
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label style={styles.label}>🏘️ Quận/Huyện</label>
            <select 
              style={styles.select}
              value={district} 
              onChange={e => setDistrict(e.target.value)}
            >
              {DISTRICTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>

        <button 
          onClick={handlePredict} 
          disabled={loading} 
          style={{
            ...styles.button,
            ...(loading ? styles.buttonDisabled : {})
          }}
        >
          {loading ? "🔄 Đang dự đoán..." : "💰 Dự đoán giá"}
        </button>

        {error && (
          <div style={styles.error}>
            ⚠️ {error}
          </div>
        )}

        {price !== null && (
          <div style={styles.result}>
            <div style={styles.resultTitle}>📊 Kết quả dự đoán:</div>
            <div style={styles.resultPrice}>
              {formatPrice(price)} triệu VNĐ/m²
            </div>
            <div style={styles.resultNote}>
              * Giá dự đoán chỉ mang tính tham khảo
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '600px',
    margin: '20px auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    backgroundColor: '#f8fafc',
    minHeight: '100vh'
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px'
  },
  title: {
    color: '#1e293b',
    margin: '0 0 10px 0',
    fontSize: '2rem',
    fontWeight: '700'
  },
  subtitle: {
    color: '#64748b',
    margin: '0',
    fontSize: '1rem'
  },
  form: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e2e8f0'
  },
  row: {
    display: 'flex',
    gap: '20px',
    marginBottom: '20px',
    flexWrap: 'wrap'
  },
  inputGroup: {
    flex: '1',
    minWidth: '200px'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    color: '#374151',
    fontWeight: '500',
    fontSize: '14px'
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    fontSize: '16px',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box'
  },
  select: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #e5e7eb',
    borderRadius: '8px',
    fontSize: '16px',
    backgroundColor: 'white',
    boxSizing: 'border-box'
  },
  button: {
    width: '100%',
    padding: '14px 24px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    marginTop: '10px'
  },
  buttonDisabled: {
    backgroundColor: '#9ca3af',
    cursor: 'not-allowed'
  },
  error: {
    marginTop: '20px',
    padding: '12px 16px',
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    borderRadius: '8px',
    border: '1px solid #fecaca'
  },
  result: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#f0f9ff',
    borderRadius: '8px',
    border: '1px solid #bae6fd',
    textAlign: 'center'
  },
  resultTitle: {
    color: '#0369a1',
    fontWeight: '600',
    marginBottom: '10px'
  },
  resultPrice: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#065f46',
    marginBottom: '10px'
  },
  resultNote: {
    fontSize: '12px',
    color: '#6b7280',
    fontStyle: 'italic'
  }
};
