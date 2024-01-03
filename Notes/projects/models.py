from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Note(models.Model):

    title = models.CharField(max_length=128, blank=False)
    note = models.TextField(max_length=512, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
    
