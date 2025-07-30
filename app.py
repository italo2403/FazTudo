import streamlit as st
from pytubefix import YouTube
import os
from moviepy.editor import AudioFileClip
from rembg import remove
from PIL import Image
import io
from urllib.parse import urlparse, parse_qs
import unicodedata, re

st.set_page_config(page_title="Media Tool", layout="centered")
st.title("🎵📹 Remover Fundo e Baixar do YouTube")

OUTPUT_DIR = "downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def limpar_link(link):
    parts = urlparse(link)
    v = parse_qs(parts.query).get("v")
    return f"https://www.youtube.com/watch?v={v[0]}" if v else link

def limpar_nome(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^\w\-_.]', '_', texto)

opcao = st.sidebar.radio("Selecione:", ["Baixar MP3", "Baixar Vídeo", "Remover Fundo de Imagem"])

if opcao in ("Baixar MP3", "Baixar Vídeo"):
    st.header("🔗 YouTube Downloader")
    link = st.text_input("Cole o link do vídeo:")

    if st.button("Baixar"):
        try:
            link_clean = limpar_link(link)
            yt = YouTube(link_clean)

            if opcao == "Baixar MP3":
                stream = yt.streams.filter(only_audio=True).first()
                path_mp4 = os.path.join(OUTPUT_DIR, f"{limpar_nome(yt.title)}.mp4")
                stream.download(output_path=OUTPUT_DIR, filename=os.path.basename(path_mp4))
                mp3file = os.path.splitext(path_mp4)[0] + ".mp3"

                if os.path.exists(mp3file):
                    os.remove(mp3file)

                clip = AudioFileClip(path_mp4)
                clip.write_audiofile(mp3file)
                clip.close()
                os.remove(path_mp4)

                st.success("MP3 pronto!")
                with open(mp3file, "rb") as f:
                    st.download_button("🔽 Baixar MP3", f, file_name=os.path.basename(mp3file))

            elif opcao == "Baixar Vídeo":
                stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
                path_video = os.path.join(OUTPUT_DIR, f"{limpar_nome(yt.title)}.mp4")
                
                if os.path.exists(path_video):
                    os.remove(path_video)

                stream.download(output_path=OUTPUT_DIR, filename=os.path.basename(path_video))

                st.success("Vídeo pronto!")
                with open(path_video, "rb") as f:
                    st.download_button("🔽 Baixar Vídeo", f, file_name=os.path.basename(path_video))

        except Exception as e:
            st.error(f"Erro ao baixar: {e}")

elif opcao == "Remover Fundo de Imagem":
    st.header("🖼️ Remover Fundo")
    uploaded_file = st.file_uploader("Envie uma imagem:", type=["png","jpg","jpeg"])
    if uploaded_file:
        try:
            img = Image.open(uploaded_file).convert("RGBA")
            result = remove(img)
            st.image(result, caption="Sem Fundo", use_column_width=True)
            buffer = io.BytesIO()
            result.save(buffer, format="PNG")
            st.download_button("🔽 Baixar imagem sem fundo", buffer.getvalue(), file_name="imagem_sem_fundo.png")
        except Exception as e:
            st.error(f"Erro ao processar imagem: {e}")
