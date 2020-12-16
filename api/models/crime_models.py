from django.db import models
from api.models.person_models import Criminal, Victim


class CrimeOfInterest(models.Model):
    type = models.CharField(max_length=4096, null=True, unique=False)
    severity_index = models.IntegerField(null=True, blank=True)
    criminals = models.ForeignKey(Criminal, on_delete=models.PROTECT)
    victims = models.ForeignKey(Victim, on_delete=models.PROTECT)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'api_crime'
