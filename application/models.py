# Create your models here.
from django.db import models
app_name = "application"


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)


class Annotation(models.Model):
    annotation_id = models.AutoField(primary_key=True)
    content = models.TextField()
    flag = models.BooleanField()
    file_name = models.CharField(max_length=100)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)  # 设置外键


class Log(models.Model):
    log_id = models.AutoField(primary_key=True)
    annotation_id = models.CharField(max_length=10)
    user_id = models.CharField(max_length=10)


class Temp(models.Model):
    temp_id = models.AutoField(primary_key=True)
    headEntity = models.CharField(max_length=100)
    headEntityType = models.CharField(max_length=100)

    tailEntity = models.CharField(max_length=100)
    tailEntityType = models.CharField(max_length=100)

    relationshipCategory = models.CharField(max_length=100)
    annotation_id = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    user_id = models.IntegerField()
    filename = models.CharField(max_length=100)


class Dictionary(models.Model):
    dictionary_id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)


class Relation(models.Model):
    relation_id = models.AutoField(primary_key=True)
    head_entity = models.CharField(max_length=100)
    tail_entity = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)