import uuid
import pathlib
from django.db import models
from django.utils import timezone


def export_file_handler(instance, filename):
    today = timezone.now().strftime("%Y-%m-%d")
    fpath = pathlib.Path(filename)
    ext = fpath.suffix  # includes the dot
    if hasattr(instance, 'id'):
        new_fname = f"{instance.id}{ext}"
    else:
        new_fname = f"{uuid.uuid4()}{ext}"
    return F"exports/{today}/{new_fname}"


class Export(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    file = models.FileField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
