from django.db import models

# Create your models here.


class FileData(models.Model):
    task_id = models.SlugField()
    file_name = models.CharField(max_length=100, default='')
    downloaded_file = models.FileField()
    total_file_size = models.FloatField(default=0.0)
    downloaded_file_size = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, default='Downloading')
    is_downloading = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.task_id

    class Meta:
        ordering = ['-id']
