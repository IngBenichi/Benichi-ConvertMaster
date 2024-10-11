
# SonicMingle

SonicMingle es una aplicación de escritorio que permite buscar y descargar videos de YouTube en formato MP3 o MP4. Utiliza la API de YouTube para buscar videos y `yt-dlp` para la descarga.

## Requisitos

Asegúrate de tener instaladas las siguientes librerías antes de ejecutar la aplicación:

- `flet`
- `yt_dlp`
- `requests`
- `tkinter` (incluida en la mayoría de las distribuciones de Python)
- `os`, `re`, `threading`, `queue`, `time`

Puedes instalarlas usando pip:

```bash
pip install flet yt-dlp requests
```

Además, necesitarás tener [FFmpeg](https://ffmpeg.org/download.html) instalado y disponible en la ruta especificada en el código.

## Uso

1. **Buscar Canciones**:
   - Escribe el nombre de la canción que deseas buscar en el campo "Buscar canción:" y presiona **Enter**.
   - La aplicación mostrará una lista de resultados de búsqueda.

2. **Seleccionar Video**:
   - Haz clic en el título del video que deseas descargar de la lista de resultados.
   - La carátula del video se mostrará automáticamente.

3. **Ingrese URL Manualmente**:
   - Si no deseas buscar, puedes ingresar la URL del video directamente en el campo "Ingrese URL de la canción:".
   - Haz clic en el botón **Obtener Carátula** para mostrar la carátula del video y su título.

4. **Seleccionar Ruta de Salida**:
   - Haz clic en el botón **Buscar** para seleccionar la carpeta donde se guardará el video descargado.
   - La ruta de salida se mostrará en la interfaz.

5. **Seleccionar Formato y Resolución**:
   - Escoge el formato de descarga (MP3 o MP4) en el menú desplegable "Formato de descarga:".
   - Si seleccionas MP4, elige la resolución deseada en el menú "Resolución:".

6. **Descargar Video**:
   - Haz clic en el botón **Convertir** para iniciar la descarga.
   - Verás una barra de progreso que muestra el porcentaje de descarga y el tiempo restante.

7. **Limpiar Campos**:
   - Usa el botón **Limpiar** para restablecer los campos de entrada y la lista de resultados.

## Notas

- Asegúrate de tener una clave API válida de YouTube y reemplaza el valor de `API_KEY` en el código con tu propia clave.
- La aplicación mostrará mensajes de estado y diálogos de error según sea necesario.

## Ejecución

Para ejecutar la aplicación, asegúrate de estar en la misma carpeta donde se encuentra el archivo de código y ejecuta el siguiente comando:

```bash
python Benichi ConvertMaster.py
```

Reemplaza `Benichi ConvertMaster.py` con el nombre real de tu archivo Python.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir a este proyecto, por favor, abre un *issue* o envía un *pull request*.


## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo `LICENSE`.

¡Disfruta de SonicMingle!
