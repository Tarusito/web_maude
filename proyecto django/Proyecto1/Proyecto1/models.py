from django.db import models

class MiModelo(models.Model):
    campo1 = models.CharField(max_length=100)
    campo2 = models.IntegerField()
    campo3 = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campo1