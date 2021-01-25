from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    cf_handle = models.CharField(max_length=100, default='not_added', unique=True)
    uri_id = models.CharField(max_length=20, default='not_added')
    batch = models.IntegerField(default=0)
    solve = models.IntegerField(default=0)
    accepted = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    error = models.IntegerField(default=0)
    other = models.IntegerField(default=0)

    class Meta:
        ordering = ['-batch', 'solve']


class Problem(models.Model):
    submissions = ArrayField(models.JSONField(null=True), null=True)
    problem_name = models.CharField(max_length=100)
    problem_link = models.CharField(max_length=100)
    total_solve = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)
    accepted = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    error = models.IntegerField(default=0)
    other = models.IntegerField(default=0)

    class Meta:
        ordering = ['-total_solve', 'problem_name']
        verbose_name_plural = 'Codeforces_problems'


class Submission(models.Model):
    language = models.CharField(max_length=255)
    accepted = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    error = models.IntegerField(default=0)
    other = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    problem = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(Problem, on_delete=models.CASCADE)
