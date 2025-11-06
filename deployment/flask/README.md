# Demo Prediksi Cuaca Sederhana (Flask)

Tujuan: jalankan model `.pkl` dan pakai lewat browser atau API. Aplikasi dibuat simpel: hanya 1 file `app.py`.

- Lokasi model: `models/random-forest-model.pkl`
- Buka di browser: `http://127.0.0.1:8000/`

Apa yang tersedia:
- `GET /` — Halaman form untuk input 4 angka dan dapat 1 prediksi
- `GET /health` — Cek status model
- `POST /predict` — API JSON untuk prediksi banyak data sekaligus

### Kirim lewat API (opsional)

Contoh JSON ke `POST /predict`:

```json
{
  "records": [
    {"precipitation": 0.0, "temp_max": 1.2, "temp_min": -0.5, "wind": 2.3}
  ]
}
```

### Contoh hasil

```json
{ "predictions": ["drizzle"] }
```

Catatan: Server akan mengembalikan NAMA label (string) jika `models/label-encoder.pkl` ada (atau model memang output string). Kalau tidak ada, bisa keluar angka (index kelas) sebagai fallback.

## Cara cepat (3 langkah)

1) Pastikan file model ada: `models/random-forest-model.pkl`
2) Double-click `run.bat` di folder ini (Windows)
3) Buka `http://127.0.0.1:8000/` (isi form dan klik Predict)

## Catatan

- Jika file model tidak bisa dibuka, biasanya versi `scikit-learn` tidak cocok dengan versi saat melatih model.
- Jika saat melatih kamu pakai `LabelEncoder`/`Scaler`, sebaiknya taruh di pipeline dan simpan bareng, atau pastikan preprocess sama saat prediksi.

## (Opsional) Jalan manual via Terminal

### PowerShell (Windows)

```powershell
cd "d:\BeData\SMK Telkom\Project Analisis Data\deployment\flask"
py -3 -m venv .venv
 .\.venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

Kalau `py` tidak ada, ganti `py -3` dengan `python`.

### Command Prompt (cmd.exe)

```bat
cd /d "d:\BeData\SMK Telkom\Project Analisis Data\deployment\flask"
py -3 -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

Kalau port 8000 dipakai aplikasi lain, ganti port di `app.py` (misal 8080) lalu akses dengan port tersebut.
