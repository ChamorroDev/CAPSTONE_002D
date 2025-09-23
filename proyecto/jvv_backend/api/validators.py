from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("El tamaño máximo de imagen es 5MB"))

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()[1:]
    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise ValidationError(_('Formatos permitidos: JPG, JPEG, PNG, GIF, WEBP'))