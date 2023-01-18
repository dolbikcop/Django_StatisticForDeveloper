from django.db import models


# Create your models here.


class Vacancy(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False, default='')
    key_skills = models.CharField(max_length=255, blank=True, null=True, default='')
    salary = models.IntegerField(blank=True, null=True, default=0)
    area_name = models.CharField(max_length=100, blank=False, null=False, default='')
    published_at = models.IntegerField(blank=False, null=False, default=0)

    class Meta:
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"

    def __str__(self):
        return f"{self.name} из г. {self.area_name}"


class HH(models.Model):
    date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return f"{self.date}"
