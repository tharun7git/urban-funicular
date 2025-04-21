from django.db import models
from django.conf import settings
import os

def upload_to_folder(instance, filename):
    folder_name = instance.folder.name if instance.folder else 'others'
    # Clean folder name to remove unsafe characters
    folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '_', '-')).strip()
    return os.path.join('photos', folder_name, filename)

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    class Meta:
        pass

class Photo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to_folder)
    folder = models.ForeignKey(
        'Folder',  
        on_delete=models.CASCADE,
        related_name='photos',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

