import streamlit as st
import pandas as pd
import numpy as np
import re

# Judul aplikasi
st.title('Prediksi Klasifikasi Popularitas Hotel')

# Deskripsi aplikasi
st.write("""
    Aplikasi ini memprediksi popularitas hotel menjadi kategori 'Good' atau 'Superb' berdasarkan jarak dan skor ulasan.
""")

# Fungsi untuk klasifikasi skor ulasan
def classify_review_score(review_score):
    return "Superb" if review_score >= 8.6 else "Good"

# Path ke file dataset bawaan
file_path = 'data/hotem_mumbai.csv'

try:
    # Membaca data dari dataset
    data = pd.read_csv(file_path)

    # Fungsi untuk membersihkan kolom Distance
    def clean_distance(value):
        if isinstance(value, str):
            value = value.strip()
            value = re.sub(r'from centre', '', value, flags=re.IGNORECASE)
            if 'km' in value:
                return float(value.replace('km', '').strip())
            elif 'm' in value:
                return float(value.replace('m', '').strip()) / 1000
        elif isinstance(value, (int, float)):
            return value
        return np.nan

    # Bersihkan kolom 'Distance' jika ada
    if 'Distance' in data.columns:
        data['Distance'] = data['Distance'].apply(clean_distance)
        data['Distance'].fillna(data['Distance'].median(), inplace=True)

    # Tambahkan kolom kategori berdasarkan Review_Score
    if 'Review_Score' in data.columns:
        data['Kategori'] = data['Review_Score'].apply(classify_review_score)

    # Filter data untuk kategori 'Good' dan 'Superb'
    data = data[data['Kategori'].isin(['Good', 'Superb'])]
    # Membagi layout ke dua kolom
    col1, col2 = st.columns(2)

    # Menampilkan 15 hotel dengan kategori Superb di kolom kiri
    with col1:
        st.subheader("15 Hotel dengan Kategori Superb")
        hotel_superb = data[data['Kategori'] == "Superb"].head(10)[['Title', 'Distance', 'Review_Score', 'Kategori']]
        hotel_superb = hotel_superb.reset_index(drop=True)  # Reset index, drop kolom index lama
        hotel_superb.index = hotel_superb.index + 1  # Set index mulai dari 1
        st.dataframe(hotel_superb)

    # Menampilkan 15 hotel dengan kategori Good di kolom kanan
    with col2:
        st.subheader("15 Hotel dengan Kategori Good")
        hotel_good = data[data['Kategori'] == "Good"].head(10)[['Title', 'Distance', 'Review_Score', 'Kategori']]
        hotel_good = hotel_good.reset_index(drop=True)  # Reset index, drop kolom index lama
        hotel_good.index = hotel_good.index + 1  # Set index mulai dari 1
        st.dataframe(hotel_good)

    # Inisialisasi DataFrame untuk data baru
    if "data_baru" not in st.session_state:
        st.session_state.data_baru = pd.DataFrame(columns=["Hotel Name", "Distance", "Review_Score", "Kategori"])

    # Form untuk input data baru
    with st.form("input_form"):
        title = st.text_input("Masukkan Nama Hotel:")
        distance = st.number_input("Masukkan Jarak (km):", min_value=0.0, step=0.1)
        review_score = st.number_input("Masukkan Review Score (1-10):", min_value=7.0, max_value=10.0, step=0.1)
        submitted = st.form_submit_button("Tambahkan")
        if submitted:
            if title.strip() and 0.0 <= distance and 1.0 <= review_score <= 10.0:
                kategori = classify_review_score(review_score)

                new_data = pd.DataFrame({
                    "Hotel Name": [title],
                    "Distance": [distance],
                    "Review_Score": [review_score],
                    "Kategori": [kategori]
                })

                st.session_state.data_baru = pd.concat([st.session_state.data_baru, new_data], ignore_index=True)
                st.success(f"Hotel '{title}' berhasil ditambahkan!")
            else:
                st.error("Pastikan semua input valid dan tidak kosong.")

    # Reset index dan mulai dari 1 untuk data baru
    st.session_state.data_baru = st.session_state.data_baru.reset_index(drop=True)
    st.session_state.data_baru.index = st.session_state.data_baru.index + 1

    # Tampilkan data baru yang telah ditambahkan
    st.write("Data Baru yang Ditambahkan:")
    st.write(st.session_state.data_baru)

    # Gabungkan data lama dan data baru
    data = pd.concat([data, st.session_state.data_baru], ignore_index=True)


except FileNotFoundError:
    st.error(f"File dataset '{file_path}' tidak ditemukan. Pastikan file tersedia di path yang benar.")
except pd.errors.EmptyDataError:
    st.error("File dataset kosong atau tidak valid.")
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
