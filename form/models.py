from django.db import models

# Create your models here.
class form(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"
