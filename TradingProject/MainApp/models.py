from django.db import models
from django.utils.timezone import make_aware

class Candle(models.Model):
    id = models.AutoField(primary_key=True)
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()

    def __str__(self):
        return f"Candle {self.id} - {self.date}"
