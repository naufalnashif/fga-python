import streamlit as st
import pandas as pd
from google_play_scraper import Sort, reviews, reviews_all
import re

import requests

from datetime import datetime
import pytz

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
#---------------------------------------------insert--------------------------------
import nltk
from nltk.corpus import stopwords

utc_timezone = pytz.timezone('UTC')
datetime_utc = datetime.now(utc_timezone)
wib_timezone = pytz.timezone('Asia/Jakarta')
dateNow = datetime_utc.astimezone(wib_timezone)

# dateNow = datetime.now(timezone.utc)
dateSimple = dateNow.strftime("%A, %d %b %Y")
timeNow = dateNow.strftime("%H:%M WIB")
yearNow = dateNow.strftime("%Y")
yearNowInt = int(dateNow.strftime("%Y"))

# URL dari FastAPI
API_URL = "http://localhost:8000/analyze-sentiment/"

# Download stopwords jika belum tersedia
nltk.download('stopwords')

# Ambil daftar stopwords Bahasa Indonesia
stop_words = set(stopwords.words('indonesian'))

def preprocess_text(text):
    # Hapus karakter non-alphabetic
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Hapus kata-kata yang termasuk dalam stopwords
    text = ' '.join(word for word in text.split() if word.lower() not in stop_words)
    return text

@st.cache_data(show_spinner=False)
def analyze_sentiment(text):
    response = requests.post(API_URL, json={"content": text})
    if response.status_code == 200:
        result = response.json()
        return result['sentimentClass']
    else:
        st.error("Failed to analyze sentiment")
        return None

@st.cache_data(show_spinner=False)
def analyze_sentiments_batch(texts):
    sentiment_classes = []
    num_texts = len(texts)
    
    # Placeholder untuk progress bar dan teks
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    for i, text in enumerate(texts):
        sentiment_class = analyze_sentiment(text)
        sentiment_classes.append(sentiment_class)
        
        # Update progress bar dan teks
        progress_percentage = (i + 1) / num_texts
        progress_bar.progress(progress_percentage)
        progress_text.text(f"Analysis: {i + 1} of {num_texts}")
    
    # Update progress bar dan teks setelah proses selesai
    progress_bar.progress(1.0)
    progress_text.text(f"Sentiment Analysis Complete\n({num_texts} reviews processed)")
    
    return sentiment_classes
#---------------------------------------------func----------------------------------

@st.cache_data
def get_url_by_app_name(nama_apl):
    """
    Mengembalikan URL aplikasi berdasarkan nama aplikasi dari kamus.

    Parameters:
    - nama_apl (str): Nama aplikasi yang dicari.
    - aplikasi_dict (dict): Kamus yang memetakan nama aplikasi ke URL.

    Returns:
    - str or None: URL aplikasi atau None jika tidak ditemukan.
    """
    list_url = [
        'https://play.google.com/store/apps/details?id=com.shopee.id',
        'https://play.google.com/store/apps/details?id=com.tokopedia.tkpd',
        'https://play.google.com/store/apps/details?id=com.amazon.mShop.android.shopping',
        'https://play.google.com/store/apps/details?id=com.grabtaxi.passenger'
    ]
    aplikasi_dict = {
        'Shopee': list_url[0],
        'Tokopedia': list_url[1],
        'Amazon': list_url[2],
        'Grab': list_url[3]
    }
    return aplikasi_dict.get(nama_apl, None)
    
@st.cache_data
def extract_app_id(play_store_url):
    # Definisikan pola ekspresi reguler untuk menemukan ID aplikasi
    pattern = r'id=([a-zA-Z0-9._]+)'

    # Gunakan ekspresi reguler untuk mencocokkan pola dalam URL
    match = re.search(pattern, play_store_url)

    # Periksa apakah ada kecocokan dan kembalikan ID aplikasi jika ada
    if match:
        app_id = match.group(1)
        return app_id
    else:
        return None
@st.cache_data(show_spinner = 'On progress, please wait...')
def scraping_func(app_id, bahasa, negara, filter_score, jumlah):
    filter_score = None if filter_score == "Semua Rating" else filter_score
    
    rws, token = reviews(   
        app_id,
        lang=bahasa,
        country=negara,
        sort=Sort.NEWEST,
        filter_score_with=filter_score,
        count=jumlah
    )
    
    scraping_done = bool(rws)
    
    return rws, token, scraping_done

@st.cache_data(show_spinner = 'Scraping on progress, please wait...')
def scraping_all_func(app_id, bahasa, negara, filter_score, sleep = 0):
    filter_score = None if filter_score == "Semua Rating" else filter_score
    
    rws = reviews_all(   
        app_id,
        sleep_milliseconds=sleep, # defaults to 0
        lang=bahasa,
        country=negara,
        filter_score_with=filter_score,
    )
    
    scraping_done = bool(rws)
    
    return rws, scraping_done

@st.cache_data
def buat_chart(df, target_year):
    # Ambil bulan
    df['at'] = pd.to_datetime(df['at'])  # Convert 'at' column to datetime
    df['month'] = df['at'].dt.month
    df['year'] = df['at'].dt.year

    # Filter DataFrame for the desired year
    df_filtered = df[df['year'] == target_year]

    # Check if data for the target year is available
    if df_filtered.empty:
        st.warning(f"Tidak ada data untuk tahun {target_year}.")
        return

    # Mapping nilai bulan ke nama bulan
    bulan_mapping = {
        1: f'Januari {target_year}',
        2: f'Februari {target_year}',
        3: f'Maret {target_year}',
        4: f'April {target_year}',
        5: f'Mei {target_year}',
        6: f'Juni {target_year}',
        7: f'Juli {target_year}',
        8: f'Agustus {target_year}',
        9: f'September {target_year}',
        10: f'Oktober {target_year}',
        11: f'November {target_year}',
        12: f'Desember {target_year}'
    }

    # Mengganti nilai dalam kolom 'month' menggunakan mapping
    df_filtered['month'] = df_filtered['month'].replace(bulan_mapping)

    # Menentukan warna untuk setiap kategori dalam kolom 'score'
    warna_score = {
        1: '#FF9AA2',
        2: '#FFB7B2',
        3: '#FFDAC1',
        4: '#E2F0CB',
        5: '#B5EAD7'
    }

    # Sorting unique scores
    unique_scores = sorted(df_filtered['score'].unique())

    # Ensure months are in the correct order
    months_order = [
        f'Januari {target_year}', f'Februari {target_year}', f'Maret {target_year}', f'April {target_year}', f'Mei {target_year}', f'Juni {target_year}',
        f'Juli {target_year}', f'Agustus {target_year}', f'September {target_year}', f'Oktober {target_year}', f'November {target_year}', f'Desember {target_year}'
    ]

    # Sort DataFrame based on the custom order of months
    df_filtered['month'] = pd.Categorical(df_filtered['month'], categories=months_order, ordered=True)
    df_filtered = df_filtered.sort_values('month')

    # 2. Table for Average Rating, Total Review, Total Response, Response Rate
    avg_rating = df_filtered['score'].mean()
    total_review = df_filtered.shape[0]
    total_response = df_filtered['replyContent'].notnull().sum()
    response_rate = (total_response / total_review) * 100 if total_review > 0 else 0

    table_data = {
        "Average Rating": [f"{avg_rating:.2f}"],
        "Total Review": [total_review],
        "Total Response": [total_response],
        "Response Rate (%)": [f"{response_rate:.2f}"]
    }
    st.subheader(f"Descriptive Analysis of {target_year}:")
    st.write("Summary Table")
    st.table(pd.DataFrame(table_data))

    # Create a bar chart with stacking and manual colors
    st.bar_chart(
        df_filtered.groupby(['month', 'score']).size().unstack().fillna(0),
        color=[warna_score[score] for score in unique_scores]
    )

    # Create columns for Pie Chart and Heatmap
    col1, col2 = st.columns(2)


    # 3. Interaktif Pie Chart Rating
    with col1:
        st.write("Pie Chart of Ratings")
        pie_data = df_filtered['score'].value_counts().sort_index().reset_index()
        pie_data.columns = ['score', 'count']

        # Menggunakan plotly.express untuk pie chart
        fig_pie = px.pie(pie_data, names='score', values='count',
                        color='score',
                        color_discrete_map=warna_score,
                        hole=0.6)  # Menambahkan hole untuk efek donut

        # Menghapus legend
        fig_pie.update_layout(
            showlegend=False,
            height=350,  # Ubah nilai sesuai dengan kebutuhan
            width=350,   # Ubah nilai sesuai dengan kebutuhan
            margin=dict(t=0, b=0, l=0, r=0)  # Menghapus margin
        )

        st.plotly_chart(fig_pie, use_container_width=False)  # Menonaktifkan use_container_width untuk menerapkan ukuran

    # 4. Interaktif Heatmap Score Rating vs App Version
    with col2:
        st.write("Heatmap of Score Rating vs App Version")
        heatmap_data = df_filtered.pivot_table(index='score', columns='appVersion', aggfunc='size', fill_value=0).reset_index()

        # Menggunakan plotly.graph_objs untuk heatmap dengan warna yang sesuai
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data.values[:, 1:],  # Data heatmap
            x=heatmap_data.columns[1:],    # Kolom appVersion
            y=heatmap_data['score'],       # Indeks score
            colorscale='Greys',          # Ganti warna sesuai dengan chart lain
            colorbar=dict(title='Count'),  # Menambahkan title pada colorbar
            hoverongaps=False
        ))

        # Menghapus legend
        fig_heatmap.update_layout(
            showlegend=False,
            height=350,  # Ubah nilai sesuai dengan kebutuhan
            width=350,   # Ubah nilai sesuai dengan kebutuhan
            margin=dict(t=0, b=0, l=0, r=0)  # Menghapus margin
        )

        st.plotly_chart(fig_heatmap, use_container_width=False) 
    st.divider()
    st.subheader("Sentiment Analysis")
    # Pie Chart Distribusi Kelas dan Wordcloud
    colom1, colom2 = st.columns(2)

    with colom1:
        st.write("Distribusi Kelas Sentimen")
        sentiment_dist = df_filtered['sentimentClass'].value_counts().reset_index()
        sentiment_dist.columns = ['Sentiment Class', 'Count']
        
        # Menghapus legend
        fig_pie.update_layout(
            showlegend=False,
            height=400,  # Ubah nilai sesuai dengan kebutuhan
            width=400,   # Ubah nilai sesuai dengan kebutuhan
            margin=dict(t=0, b=0, l=0, r=0)  # Menghapus margin
        )

        # Warna yang akan digunakan untuk masing-masing kelas sentimen
        sentiment_colors = {
            'positive': '#B5EAD7',  # Hijau terang
            'neutral': 'grey',      # Abu-abu
            'negative': '#FF9AA2'   # Merah muda
        }

        # Menggunakan plotly.express untuk pie chart
        fig_pie = px.pie(sentiment_dist, names='Sentiment Class', values='Count',
                        title="Distribusi Kelas Sentimen",
                        color='Sentiment Class',  # Menggunakan warna yang sesuai
                        color_discrete_map=sentiment_colors,
                        hole=0.6)  # Menambahkan hole untuk efek donut
        
        # Menghapus legend dan mengatur ukuran
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            width=400,
            margin=dict(t=0, b=0, l=0, r=0)  # Menghapus margin
        )
        
        st.plotly_chart(fig_pie, use_container_width=False)

    with colom2:
        st.write("Wordcloud dari Konten")
        
        # Gabungkan semua konten dan hapus stopwords
        text = ' '.join(df_filtered['content'].astype(str))
        text = preprocess_text(text)
        
        # Buat wordcloud
        wordcloud = WordCloud(width=800, height=800, background_color='white', colormap="Greys").generate(text)
        
        # Tampilkan wordcloud
        fig_wc, ax_wc = plt.subplots(figsize=(8, 8))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis('off')
        
        st.pyplot(fig_wc)

    # Sentimen Overtime
    if 'at' in df_filtered.columns and 'sentimentClass' in df_filtered.columns:
        # Konversi kolom 'at' menjadi datetime
        df_filtered['at'] = pd.to_datetime(df_filtered['at'])
        
        # Group by kelas sentimen dan bulan
        sentiment_overtime = df_filtered.groupby([df_filtered['at'].dt.to_period('M'), 'sentimentClass']).size().reset_index(name='Count')
        sentiment_overtime['at'] = sentiment_overtime['at'].dt.to_timestamp()

        # Warna yang akan digunakan untuk masing-masing kelas sentimen
        sentiment_colors = {
            'positive': '#B5EAD7',  # Hijau terang
            'neutral': 'grey',      # Abu-abu
            'negative': '#FF9AA2'   # Merah muda
        }

        # Membuat grafik garis menggunakan Plotly
        fig_overtime = px.line(sentiment_overtime, x='at', y='Count', color='sentimentClass',
                            title="Sentimen dari Waktu ke Waktu Berdasarkan Kelas Sentimen",
                            labels={'at': 'Tanggal', 'Count': 'Jumlah', 'sentimentClass': 'Kelas Sentimen'},
                            color_discrete_map=sentiment_colors)
        
        # Menampilkan grafik di Streamlit
        st.plotly_chart(fig_overtime, use_container_width=True)


#--------------------------------------------UI---------------------------------------
# Streamlit UI
st.title("Data Everywhere : Scraping Playstore Reviews and Analysis")
scraping_done = False
with st.sidebar :
    st.text(f"Today\t: {dateSimple}")
    st.text(f"Time\t: {timeNow}")
    with st.expander("Scraping Settings :"):
        scrape = st.selectbox("PIlih Metode :", ("Semua Reviews", "Estimasi Data"), index = 1)
        aplikasi = st.radio( 
            "Pilih Input :",
            ["Defaults", "Custom URL"], index = 0,
            captions = ["Shopee, Tokopedia, Amazon, Grab", "Tambahkan URL Manual"])
        if aplikasi == "Defaults" :
            nama_apl = st.selectbox("Pilih Aplikasi :", ('Amazon','Shopee', 'Tokopedia', 'Grab'))
            if nama_apl :
                url = get_url_by_app_name(nama_apl)
        elif aplikasi == "Custom URL":
            url = st.text_input("Masukkan URL Aplikasi Pada Web Playstore :", 'https://play.google.com/store/apps/details?id=com.shopee.id')
        if scrape == "Estimasi Data" :
            jumlah = st.number_input("Masukkan Estimasi Banyak Data :", min_value = 10, max_value = 25000, step = 10, placeholder="Type a number...")
    with st.expander("Preference Settings :"):
        if scrape == "Semua Reviews" : 
            sleep = st.number_input("Masukkan sleep (milisecond) :", min_value = 1, max_value = 1000, step = 10, placeholder="Type a number...")
        bahasa = st.selectbox("Pilih Bahasa:", ('id', 'en'))
        negara = st.selectbox("Pilih Negara :", ('id', 'us'))
        filter_score = st.selectbox("Pilih Rating :", ('Semua Rating', 1, 2, 3, 4, 5))


        # Dynamically generate the years list up to the current year
        years = list(range(2017, yearNowInt + 1))  # Add +1 for the current year and +2 for the next year
        # Create a selectbox for selecting the year, defaulting to the current year
        target_year = st.selectbox("Pilih Tahun:", years, index=years.index(yearNowInt))

        download_format = st.selectbox("Pilih Format Unduhan :", ["CSV", "XLSX", "JSON"])
    st.info('Tekan "Mulai Scraping" kembali jika tampilan menghilang ', icon="ℹ️")

    # Kode untuk scraping dan analisis
    if url and bahasa and negara and filter_score and download_format:
        if st.button("Mulai Scraping & Analysis"):
            app_id = extract_app_id(url)
            
            if scrape == "Semua Reviews":
                reviews, scraping_done = scraping_all_func(app_id, bahasa, negara, filter_score, sleep)
                df = pd.DataFrame(reviews)
            elif scrape == "Estimasi Data":
                reviews, token, scraping_done = scraping_func(app_id, bahasa, negara, filter_score, jumlah)
                df = pd.DataFrame(reviews)
            else:
                st.warning("Masukkan pilihan yang valid")
            
        if 'df' in locals():
            # Menampilkan progress bar dan teks kemajuan
            sentiment_classes = analyze_sentiments_batch(df['content'])
            
            # Menambahkan kolom sentimentClass ke DataFrame
            df['sentimentClass'] = sentiment_classes
        if st.button("Clear Cache"):
            # Clear values from *all* all in-memory and on-disk data caches:
            # i.e. clear values from both square and cube
            st.cache_data.clear()
    else:
        st.error("Mohon Masukkan Parameter.")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Readme", "📈 Results", "🤵 Creator", "🔍 More"])
with tab1:
    @st.cache_resource
    def tab_1():
        st.image("/Users/naufalnashif/Desktop/python-dev/FGA-Python/scraping_analysis_app/frontend/assets/architechture.png", caption="Architecture")
        st.header("User Guide:")
        '''
        Langkah - langkah :
        1. Buka sidebar sebelah kiri
        2. Buka Scraping Settings
        3. Hati - hati jika menggunakan "Semua Reviews" karena bisa berjumlah jutaan data
        4. Masukkan URL app pada situs playstore
        5. Sesuaikan bahasa, negara, dan rating yang akan diambil
        6. Pilih tahun
        7. Pilih format unduhan
        8. Klik "Mulai Scraping"
        9. Buka tab Results
        '''
    tab_1()
#-------------------------------------------BE----------------------------------------

with tab2:
    st.header("Results:")

    if scraping_done == True:
        with st.expander(f"Hasil Scraping {app_id}:"):
            st.write(df)
        
            if download_format == "XLSX":
                # Clean the data to remove illegal characters
                cleaned_data = df.applymap(lambda x: "".join(char for char in str(x) if char.isprintable()))
        
                # Save the cleaned data to Excel
                cleaned_data.to_excel(f"hasil_scraping_{app_id}.xlsx", index=False)
        
                # Provide the download button for the cleaned Excel file
                st.download_button(label=f"Unduh XLSX ({len(reviews)} data)", data=open(f"hasil_scraping_{app_id}.xlsx", "rb").read(), key="xlsx_download", file_name=f"hasil_scraping_{app_id}.xlsx")
        
            elif download_format == "CSV":
                csv = df.to_csv(index=False)
        
                # Provide the download button for the CSV file
                st.download_button(label=f"Unduh CSV ({len(reviews)} data)", data=csv, key="csv_download", file_name=f"hasil_scraping_{app_id}.csv")
        
            elif download_format == "JSON":
                json_data = df.to_json(orient="records")
        
                # Provide the download button for the JSON file
                st.download_button(label=f"Unduh JSON ({len(reviews)} data)", data=json_data, key="json_download", file_name=f"hasil_scraping_{app_id}.json")
        with st.expander(f"Hasil Analysis {app_id}:"):
            buat_chart(df, target_year)

    else:
        st.info("Tidak ada data")
        
with tab3:
    @st.cache_resource
    def tab_3():
        st.header("Profile:")
        st.image('https://raw.githubusercontent.com/naufalnashif/naufalnashif.github.io/main/assets/img/my-profile-sidang-idCard-crop.JPG', caption='Naufal Nashif')
        st.subheader('Hello, nice to meet you !')
        # Tautan ke GitHub
        github_link = "https://github.com/naufalnashif/"
        st.markdown(f"GitHub: [{github_link}]({github_link})")
        
        # Tautan ke Instagram
        instagram_link = "https://www.instagram.com/naufal.nashif/"
        st.markdown(f"Instagram: [{instagram_link}]({instagram_link})")
        
        # Tautan ke Website
        website_link = "https://naufalnashif.netlify.app/"
        st.markdown(f"Website: [{website_link}]({website_link})")
    tab_3()
    
with tab4:
    @st.cache_resource   
    def tab_4():
        st.header("More:")
        more1, more2, more3 = st.columns(3)
        with more1 :
            st.image('https://raw.githubusercontent.com/naufalnashif/huggingface-repo/main/assets/img/sentiment-analysis-biskita.png', caption = 'Sentiment Analysis Web App')
            more1_link = "https://huggingface.co/spaces/naufalnashif/sentiment-analysis-ensemble-model"
            st.markdown(f"[{more1_link}]({more1_link})")
        with more2 :
            st.image('https://raw.githubusercontent.com/naufalnashif/huggingface-repo/main/assets/img/scraping-news-headline.png', caption = 'Scraping News Headline')
            more2_link = "https://huggingface.co/spaces/naufalnashif/scraping-news-headline"
            st.markdown(f"[{more2_link}]({more2_link})")
        with more3 :
            st.image('https://raw.githubusercontent.com/naufalnashif/huggingface-repo/main/assets/img/scraping-ecommerce.png', caption = 'Scraping Ecommerce Product')
            more3_link = "https://huggingface.co/spaces/naufalnashif/scraping-ecommerce-2023"
            st.markdown(f"[{more3_link}]({more3_link})")
    tab_4()
    
# Garis pemisah
st.divider()
st.write('Thank you for trying the demo!') 
st.caption(f'Made with ❤️ by :blue[Naufal Nashif] ©️ {yearNow}')