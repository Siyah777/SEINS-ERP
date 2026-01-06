# -*- coding: utf-8 -*-
import os
from PIL import Image
from io import BytesIO

MEDIA_ORDENES = "/app/media/ordenes"
MAX_KB = 300
MAX_SIZE = (1920, 1920)

total = 0
reducidas = 0

def reducir_imagen(path):
    global reducidas

    size_kb = os.path.getsize(path) / 1024
    if size_kb <= MAX_KB:
        return

    try:
        img = Image.open(path)
        formato = img.format or "JPEG"

        img.thumbnail(MAX_SIZE, Image.LANCZOS)

        calidad = 85
        buffer = BytesIO()

        while True:
            buffer.seek(0)
            buffer.truncate()

            img.save(buffer, format=formato, optimize=True, quality=calidad)

            if buffer.tell() / 1024 <= MAX_KB or calidad <= 30:
                break

            calidad -= 5

        with open(path, "wb") as f:
            f.write(buffer.getvalue())

        reducidas += 1
        print(f"🗜️ Reducida: {path}")

    except Exception as e:
        print(f"⚠️ Error con {path}: {e}")

for root, _, files in os.walk(MEDIA_ORDENES):
    for file in files:
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            total += 1
            reducir_imagen(os.path.join(root, file))

print(f"\n📊 Total imágenes encontradas: {total}")
print(f"📉 Imágenes recomprimidas: {reducidas}")

