# Generated by Django 3.2.4 on 2021-06-25 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('aircraft_id', models.AutoField(primary_key=True, serialize=False)),
                ('aircraft_name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('annotation_id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('flag', models.BooleanField()),
                ('file_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('dictionary_id', models.AutoField(primary_key=True, serialize=False)),
                ('entity', models.CharField(max_length=100)),
                ('entity_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('annotation_id', models.CharField(max_length=10)),
                ('user_id', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('model_id', models.AutoField(primary_key=True, serialize=False)),
                ('model_name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Rel',
            fields=[
                ('rel_id', models.AutoField(primary_key=True, serialize=False)),
                ('headEntity', models.CharField(max_length=100)),
                ('headEntityType', models.CharField(max_length=100)),
                ('tailEntity', models.CharField(max_length=100)),
                ('tailEntityType', models.CharField(max_length=100)),
                ('relationshipCategory', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=255)),
                ('re_flag', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('relation_id', models.AutoField(primary_key=True, serialize=False)),
                ('head_entity', models.CharField(max_length=100)),
                ('tail_entity', models.CharField(max_length=100)),
                ('relation', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Temp',
            fields=[
                ('temp_id', models.AutoField(primary_key=True, serialize=False)),
                ('headEntity', models.CharField(max_length=100)),
                ('headEntityType', models.CharField(max_length=100)),
                ('tailEntity', models.CharField(max_length=100)),
                ('tailEntityType', models.CharField(max_length=100)),
                ('relationshipCategory', models.CharField(max_length=100)),
                ('user_id', models.IntegerField()),
                ('filename', models.CharField(max_length=100)),
                ('annotation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.annotation')),
            ],
        ),
        migrations.AddField(
            model_name='annotation',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.user'),
        ),
    ]
