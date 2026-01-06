from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os

class ImageReduceMixin:
    IMAGE_FIELDS = ()
    MAX_KB = 300
    MAX_SIZE = (1920, 1920)

    def reducir_imagenes(self):
        for field_name in self.IMAGE_FIELDS:
            imagen = getattr(self, field_name, None)
            if not imagen:
                continue

            self._reducir_imagen(imagen)

    def _reducir_imagen(self, imagen_field):
        try:
            img = Image.open(imagen_field)
            img = img.convert("RGB")

            img.thumbnail(self.MAX_SIZE, Image.LANCZOS)

            quality = 85
            buffer = BytesIO()

            while True:
                buffer.seek(0)
                buffer.truncate()

                img.save(
                    buffer,
                    format="JPEG",
                    optimize=True,
                    quality=quality
                )

                if buffer.tell() / 1024 <= self.MAX_KB or quality <= 30:
                    break

                quality -= 5

            nombre = os.path.splitext(imagen_field.name)[0] + ".jpg"
            imagen_field.file = ContentFile(buffer.getvalue(), name=nombre)

        except Exception:
            # 🔒 sin print en producción
            pass
