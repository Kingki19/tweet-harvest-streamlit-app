import streamlit as st
import subprocess
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

def install_npm_and_tweet_harvest():
    # Perintah instalasi (contoh untuk Ubuntu/Debian)
    commands = [
        #"sudo apt install npm",
        "npm install -g tweet-harvest"
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Error menjalankan perintah: {command}\n{result.stderr}")
            return False
    
    st.success("npm dan tweet-harvest berhasil diinstal!")
    return True

def run_tweet_harvest(options, search_keyword):
    """Dibangun berdasarkan skrip ini: https://github.com/helmisatria/tweet-harvest"""
    command = ["npx", "--yes", "tweet-harvest@2.6.0"] + options # Semisal ada eror ganti versi ganti ini aja nanti.
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        st.success("Skrip berhasil dijalankan!")
        try:
            df = pd.read_json(options[options.index("-o") + 1])
            st.dataframe(df)  # Tampilkan data dalam DataFrame

            towrite = BytesIO()
            writer = pd.ExcelWriter(towrite, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
            towrite.seek(0)  # reset pointer
            st.download_button(
                label="Download Data sebagai Excel",
                data=towrite,
                file_name = f"tweets:{search_keyword}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except:
            st.error("Gagal Membaca File JSON")
  

# Antarmuka Streamlit
st.title("Pengunduh Tweet")

# Input teks
token = st.text_input("Token Otentikasi (auth_token) Twitter:", type="password")
with st.popover("Tutorial Cara Mendapatkan Otentikasi Twitter"):
    st.markdown("""
    1. Buka halaman Twitter dan masuk seperti biasa menggunakan akunmu  
    2. Klik kanan dan masuk ke menu inspeksi (inspect) halaman  
    3. Cari menu application dan masuk ke situ  
    4. Di sidebar (kiri), cari bagian cookies lalu masuk ke bagian 'https://twitter.com'  
    5. Di bagian dalam kolom 'name', cari 'auth_token' lalu copy paste value dari 'auth_token' ini ke sini.  
    """)
search_keyword = st.text_input("Kata Kunci Pencarian:")

# Input tanggal
from_date = st.date_input("Tanggal Mulai (DD-MM-YYYY):")
to_date = st.date_input("Tanggal Akhir (DD-MM-YYYY):")

# Input angka
limit = st.number_input("Jumlah Tweet:", min_value=1, value=100)
delay = st.number_input("Jeda Antar Tweet (detik):", min_value=0, value=3)

# Pilihan tab
tab = st.selectbox("Tab Pencarian:", ["TOP", "LATEST"], index=0)

# Opsi thread (input URL)
thread_url = st.text_input("URL Thread Tweet (opsional):")

# Membangun daftar opsi
options = []
if token:
    options.extend(["-t", token])
if from_date:
    options.extend(["-f", from_date.strftime("%d-%m-%Y")])
if to_date:
    options.extend(["--to", to_date.strftime("%d-%m-%Y")])
if search_keyword:
    options.extend(["-s", search_keyword])
if thread_url:
    options.extend(["--thread", thread_url])
options.extend(["-l", str(limit)])
options.extend(["-d", str(delay)])
options.extend(["--tab", tab])

st.write('Sebelum menjalankan, tekan tombol dibawah. (tekan satu kali)')
if st.button("Instal npm dan tweet-harvest"):
    install_npm_and_tweet_harvest()
# Tombol jalankan
if st.button("Jalankan"):
    run_tweet_harvest(options, search_keyword)
