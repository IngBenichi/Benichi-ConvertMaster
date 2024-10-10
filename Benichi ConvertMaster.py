import os
import re
import flet as ft
import yt_dlp
from tkinter import filedialog
from threading import Thread, Event
import queue
import time
import requests

API_KEY = ''  # Asegúrate de ingresar tu API Key aquí

def main(page: ft.Page):
    page.title = "SonicMingle"
    page.window.width = 600
    page.window.height = 750
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    youtube_urls = []
    download_queue = queue.Queue()
    stop_event = Event()
    available_resolutions = []
    thumbnail_url = ""

    def browse_output_path(e):
        output_path = filedialog.askdirectory()
        if output_path:
            output_path_entry.value = output_path
            output_path_label.value = f"Ruta de salida: {output_path}"
            page.update()

    def clear_fields(e):
        search_entry.value = ""
        video_title_text.value = ""
        urls_list_view.controls.clear()
        cover_image.src = ""
        progress_bar.value = 0
        download_status.value = ""
        progress_bar.visible = False
        youtube_urls.clear()
        format_selector.value = "mp3"
        resolution_selector.options.clear()
        resolution_selector.visible = False
        manual_url_entry.value = ""
        page.update()

    def search_videos(e):
        query = search_entry.value.strip()
        if not query:
            return

        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={API_KEY}&maxResults=10"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            urls_list_view.controls.clear()
            for item in data.get("items", []):
                video_id = item["id"].get("videoId")
                if video_id:
                    title = item["snippet"]["title"]
                    urls_list_view.controls.append(
                        ft.TextButton(
                            text=f"{title} (https://www.youtube.com/watch?v={video_id})",
                            on_click=lambda e, vid=video_id, t=title: select_video(vid, t)
                        )
                    )
            page.update()
        else:
            show_dialog("Error", "Se agotaron las cuotas de la API. Por favor, ingrese la URL del video manualmente.")
            manual_url_entry.visible = True  # Habilitar el campo para ingresar la URL manual
            page.update()

    def select_video(video_id, title):
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_urls.append(youtube_url)
        video_title_text.value = f"Descargando: {title}"
        
        global thumbnail_url
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        cover_image.src = thumbnail_url

        urls_list_view.controls.clear()  # Limpiar la lista de URLs después de seleccionar un video
        page.update()

    def convert(e):
        output_path = output_path_entry.value.strip()
        if not youtube_urls and not manual_url_entry.value.strip() or not output_path:
            show_dialog("Advertencia", "Por favor, completa todos los campos y añade al menos un enlace.")
            return
    
        # Si hay una URL manual, añádala a la lista de URLs
        if manual_url_entry.value.strip():
            youtube_urls.append(manual_url_entry.value.strip())
            # Extraer el video_id de la URL manual
            video_id = manual_url_entry.value.split('=')[-1] if 'v=' in manual_url_entry.value else manual_url_entry.value.split('/')[-1]
            # Cargar la carátula
            global thumbnail_url
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            cover_image.src = thumbnail_url  # Establecer la URL de la carátula
            cover_image.visible = True  # Asegúrate de que la imagen sea visible
    
        for youtube_url in youtube_urls:
            download_queue.put((youtube_url, output_path))
    
        convert_button.label = "Descargando..."
        page.update()
    
        start_download_thread()


    def start_download_thread():
        Thread(target=process_download_queue, daemon=True).start()

    def process_download_queue():
        while not download_queue.empty():
            youtube_url, output_path = download_queue.get()
            download_video(youtube_url, output_path)
            download_queue.task_done()

    def download_video(youtube_url, output_path):
        try:
            selected_format = format_selector.value
            selected_resolution = resolution_selector.value
            if selected_format == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'ffmpeg_location': r'C:\Users\CAMILO\Desktop\ffmpeg-7.1-essentials_build\ffmpeg-7.1-essentials_build\bin',
                    'progress_hooks': [progress_hook],
                }
            else:  # Formato mp4
                ydl_opts = {
                    'format': f'bestvideo[height<={selected_resolution}] + bestaudio/best' if selected_resolution else 'bestvideo + bestaudio',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'ffmpeg_location': r'C:\Users\CAMILO\Desktop\ffmpeg-7.1-essentials_build\ffmpeg-7.1-essentials_build\bin',
                    'progress_hooks': [progress_hook],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                progress_bar.visible = True
                ydl.download([youtube_url])

            show_dialog("Éxito", f"Video descargado en: {output_path}")
            clear_fields(None)
        except Exception as e:
            print(f"Error en download_video: {str(e)}")
            show_dialog("Error", f"Se produjo un error: {str(e)}")
        finally:
            page.update()

    def list_available_formats(youtube_url):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                formats = info.get('formats', [])
                resolutions = set(fmt['height'] for fmt in formats if 'height' in fmt and fmt['height'] is not None)
                return sorted(resolutions, reverse=True)
        except Exception as e:
            print(f"Error al listar formatos: {str(e)}")
            return []

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = int(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100)
            progress_bar.value = percent / 100
            remaining_time = d.get('eta', 0)
            download_status.value = f"Descargando... {percent}% - Tiempo restante: {time.strftime('%M:%S', time.gmtime(remaining_time))}"
            page.update()

    def show_dialog(title, content):
        dialog = ft.AlertDialog(title=ft.Text(title), content=ft.Text(content))
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def get_resolutions(e):
        global available_resolutions
        if youtube_urls or manual_url_entry.value.strip():
            url_to_check = youtube_urls[-1] if youtube_urls else manual_url_entry.value.strip()
            available_resolutions = list_available_formats(url_to_check)
            resolution_selector.options.clear()
            for resolution in available_resolutions:
                resolution_selector.options.append(ft.dropdown.Option(resolution))
            resolution_selector.value = available_resolutions[0] if available_resolutions else None
            resolution_selector.visible = len(available_resolutions) > 0
        else:
            resolution_selector.options.clear()
            resolution_selector.visible = False

        page.update()

    # Nueva función para obtener la carátula desde la URL manual
    def get_thumbnail(e):
        manual_url = manual_url_entry.value.strip()

        # Validar si hay una URL ingresada manualmente
        if not manual_url:
            show_dialog("Advertencia", "Por favor, ingrese una URL válida.")
            return

        # Extraer el video_id de la URL manualmente (manejo de distintos formatos de URL)
        video_id = None
        if 'v=' in manual_url:
            video_id = manual_url.split('v=')[-1].split('&')[0]
        elif 'youtu.be/' in manual_url:
            video_id = manual_url.split('youtu.be/')[-1].split('?')[0]

        if video_id:
            # Cargar la carátula a partir del video_id
            global thumbnail_url
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            cover_image.src = thumbnail_url  # Establecer la URL de la carátula
            cover_image.visible = True  # Asegurarse de que la imagen sea visible
            page.update()  # Actualizar la interfaz
        else:
            show_dialog("Error", "No se pudo extraer el ID del video de la URL proporcionada.")

    search_entry = ft.TextField(label="Buscar canción:", on_change=search_videos)
    manual_url_entry = ft.TextField(label="Ingrese URL de la canción:", visible=True)  # Hacemos el campo visible
    output_path_entry = ft.TextField(label="Ruta de salida:", disabled=True)
    output_path_label = ft.Text("Ruta de salida: No seleccionada")
    browse_button = ft.ElevatedButton("Buscar", on_click=browse_output_path)

    format_selector = ft.Dropdown(
        label="Formato de descarga:",
        options=[
            ft.dropdown.Option("mp3"),
            ft.dropdown.Option("mp4"),
        ],
        value="mp3",
        on_change=lambda e: get_resolutions(e)
    )

    resolution_selector = ft.Dropdown(
        label="Resolución:",
        options=[],
        visible=False,
    )

    convert_button = ft.ElevatedButton("Convertir", on_click=convert)
    clear_button = ft.ElevatedButton("Limpiar", on_click=clear_fields)

    # Nuevo botón para obtener la carátula desde la URL manual
    get_thumbnail_button = ft.ElevatedButton("Obtener Carátula", on_click=get_thumbnail)

    urls_list_view = ft.ListView()
    video_title_text = ft.Text()
    cover_image = ft.Image()
    progress_bar = ft.ProgressBar(visible=False)
    download_status = ft.Text()

    page.add(
        search_entry,
        manual_url_entry,
        urls_list_view,
        output_path_label,
        output_path_entry,
        browse_button,
        format_selector,
        resolution_selector,
        convert_button,
        clear_button,
        get_thumbnail_button,  # Botón para obtener la carátula
        cover_image,
        video_title_text,
        progress_bar,
        download_status
    )

if __name__ == "__main__":
    ft.app(target=main)
