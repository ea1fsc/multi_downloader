"""YouTube Downloader Script"""

from __future__ import annotations

import datetime
import os
import platform
import re
import sys
from typing import Optional, Tuple, List

import pytubefix as pyt  # Library for interacting with YouTube

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")))
import variables as vr
import functions as func

banner_yt = vr.banner_yt
separator = vr.separator


def request_url() -> str:
    """Ask the user for a YouTube URL and validate it with a regex that covers common formats."""
    # Regex covers: youtube.com/watch, youtu.be, embed, shorts, /v/, and preserves the 11-char video ID
    youtube_regex = re.compile(
        r"^(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})",
        re.IGNORECASE,
    )
    print(separator)
    while True:
        url = input("Por favor, introduce la URL de YouTube: ").strip()
        if url and youtube_regex.search(url):
            return url
        print("Introduce una URL válida de YouTube, por favor.")


def build_and_confirm_yt(url: str) -> Tuple[bool, Optional[pyt.YouTube]]:
    """Build a YouTube object from URL, show info, and ask for confirmation.
    Always return a (bool, YouTube|None) tuple.
    """
    try:
        yt = pyt.YouTube(url)  # Build the YouTube object
        title = yt.title
        duration = str(datetime.timedelta(seconds=yt.length))
        channel_title = yt.author
        channel_url = yt.channel_url

        print(separator)
        print(f"Título: {title}")
        print(f"Duración: {duration}")
        print(f"Canal: {channel_title}")
        print(f"URL del canal: {channel_url}")
        print(separator)

        while True:
            ans = input("¿Es este el vídeo que quieres? (y/n): ").strip().lower()
            if ans == "y":
                print(separator)
                return True, yt
            if ans == "n":
                return False, None
            print("Entrada no válida. Escribe 'y' o 'n'.")
    except Exception as e:
        print(f"Ocurrió un error obteniendo los detalles del vídeo: {e}")
        return False, None


def get_streams_by_format(yt_video: pyt.YouTube, kind: str):
    """Return streams filtered by the chosen kind: 'audio' | 'video' | 'audio+video' (progressive)."""
    streams = yt_video.streams
    if kind == "audio":
        return streams.filter(only_audio=True)
    if kind == "video":
        return streams.filter(only_video=True, progressive=False)
    if kind == "audio+video":
        return streams.filter(progressive=True)
    raise ValueError(f"Unknown format kind: {kind}")


def display_stream_info(idx: int, stream, kind_label: str) -> None:
    """Pretty-print stream info with safe fallbacks."""
    # File extension
    file_ext = (stream.mime_type.split("/")[-1] if stream.mime_type else "unknown")
    # Codecs
    codecs = getattr(stream, "codecs", None)
    codec = codecs[0] if codecs else "unknown"
    # Resolution & fps for video; abr for audio
    resolution = getattr(stream, "resolution", None) or "N/A"
    fps = getattr(stream, "fps", None) or "N/A"
    abr = getattr(stream, "abr", None) or "N/A"
    # Estimated filesize if available
    size_mb = getattr(stream, "filesize_mb", None)
    size_str = f"{size_mb:.1f} MB" if isinstance(size_mb, float) else "N/A"

    # Build a concise line depending on kind
    if kind_label == "audio":
        extra = f"ABR: {abr}"
    elif kind_label == "video":
        extra = f"Res: {resolution} | FPS: {fps}"
    else:  # progressive audio+video
        extra = f"Res: {resolution} | FPS: {fps}"

    print(f"[{idx}] Tipo: {kind_label} | Formato: {file_ext} | Codec: {codec} | {extra} | Tamaño aprox: {size_str}")


def choose_stream(streams, kind_label: str):
    """List available streams and return the selected stream after confirmation."""
    print(separator)
    print("Opciones disponibles:\n")
    for i, s in enumerate(streams, start=1):
        display_stream_info(i, s, kind_label)

    print(separator)
    while True:
        selected = input("Selecciona el índice del stream deseado: ").strip()
        if not selected.isdigit():
            print("Entrada no válida. Introduce un número de la lista.")
            continue
        index = int(selected)
        if not (1 <= index <= len(streams)):
            print("El índice seleccionado no existe. Selecciona otro.")
            continue

        stream = streams[index - 1]
        display_stream_info(index, stream, kind_label)
        while True:
            ans = input("¿Confirmas que es el stream correcto? (y/n): ").strip().lower()
            print(separator)
            if ans == "y":
                return stream
            if ans == "n":
                break  # go back to list prompt
            print("Entrada no válida. Escribe 'y' o 'n'.")


def ask_download_directory() -> str:
    """Ask the user for a download directory; provide sensible defaults per OS."""
    while True:
        download_dir = input(
            "Carpeta de destino (Enter para la carpeta Descargas/Downloads por defecto): "
        ).strip()
        if not download_dir:
            system_name = platform.system()
            home = os.path.expanduser("~")
            if system_name in ("Windows", "Darwin"):
                download_dir = os.path.join(home, "Downloads")
            elif system_name == "Linux":
                # Try Spanish 'Descargas'; fallback to 'Downloads'
                candidate = os.path.join(home, "Descargas")
                download_dir = candidate if os.path.isdir(candidate) else os.path.join(home, "Downloads")
            else:
                print("SO no soportado. Indica la carpeta manualmente.")
                continue
        if os.path.isdir(download_dir):
            return download_dir
        print("Directorio no válido. Introduce una ruta válida.")


def sanitize_filename(name: str) -> str:
    """Very small helper to avoid odd characters in filenames."""
    return re.sub(r'[\\/*?:"<>|]+', "_", name).strip()


def download_stream(stream, yt_title: str) -> None:
    download_dir = ask_download_directory()
    user_name = input("Nombre de archivo (Enter para usar el título del vídeo): ").strip()
    base_name = sanitize_filename(user_name if user_name else yt_title)

    try:
        # 1) Let pytubefix choose the right extension (.mp4, .webm, .m4a, ...)
        tmp_path = stream.download(output_path=download_dir)  # <--- no filename!

        # 2) Keep extension chosen by the library
        _, ext = os.path.splitext(tmp_path)  # ext includes leading dot

        final_path = os.path.join(download_dir, f"{base_name}{ext}")
        if tmp_path != final_path:
            os.replace(tmp_path, final_path)

        print(f"Descarga completada: {final_path}")
    except Exception as e:
        print(f"Ocurrió un error durante la descarga: {e}")


def ask_mode() -> Optional[str]:
    """Ask the user which kind of download they want. Return one of: 'video', 'audio', 'audio+video', 'back'."""
    sel = input(
        "Selecciona la opción deseada:\n"
        "1 - Descargar vídeo (sin audio).\n"
        "2 - Descargar audio.\n"
        "3 - Descargar vídeo (con audio) [progresivo <=720p].\n"
        "0 - Seleccionar otra URL.\n"
        "Opción seleccionada: "
    ).strip()
    if sel == "1":
        return "video"
    if sel == "2":
        return "audio"
    if sel == "3":
        return "audio+video"
    if sel == "0":
        return "back"
    print("Opción no válida.")
    return None


def ask_another_and_same_url() -> Tuple[bool, bool]:
    """Ask whether the user wants to download another item, and if so, whether from the same URL."""
    while True:
        other = input("¿Quieres descargar otro elemento? (y/n): ").strip().lower()
        if other == "y":
            while True:
                same = input("¿De la misma URL? (y/n): ").strip().lower()
                if same in ("y", "n"):
                    return True, (same == "y")
                print("Entrada no válida. Escribe 'y' o 'n'.")
        elif other == "n":
            return False, False
        else:
            print("Entrada no válida. Escribe 'y' o 'n'.")


def main() -> int:
    """Main loop: URL loop + per-URL download loop."""
    print(banner_yt)
    print("¡Bienvenido/a al Descargador de YouTube!")
    while True:
        # --- URL loop ---
        url = request_url()
        if not func.check_url_accessibility(url):
            # If URL is not accessible, restart URL loop
            continue

        confirmed, yt = build_and_confirm_yt(url)
        if not confirmed or yt is None:
            # User declined or we failed to build the YouTube object; restart URL loop
            continue

        # --- per-URL loop (allow multiple downloads for this video) ---
        while True:
            kind = ask_mode()
            if kind is None:
                # invalid option, re-ask inside same URL
                continue
            if kind == "back":
                # go back to URL loop
                break

            # List and choose streams for the chosen kind
            streams = get_streams_by_format(yt, kind)
            stream = choose_stream(streams, "audio" if kind == "audio" else ("audio+video" if kind == "audio+video" else "video"))

            # Download
            download_stream(stream, yt.title)

            # Ask whether to download another file and whether from same URL
            wants_more, same_url = ask_another_and_same_url()
            if not wants_more:
                print("Gracias por usar el Descargador de YouTube. Volviendo al menú principal...")
                return 0
            if not same_url:
                # Break per-URL loop to trigger a new URL
                break

        # Back to top of URL loop

    # Unreachable
    # return 0


if __name__ == "__main__":
    main()
