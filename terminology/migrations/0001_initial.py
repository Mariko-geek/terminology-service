# Generated manually for the test-task repository.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RefBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True, verbose_name='Код')),
                ('name', models.CharField(max_length=300, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Справочник',
                'verbose_name_plural': 'Справочники',
                'ordering': ('code',),
            },
        ),
        migrations.CreateModel(
            name='RefBookVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=50, verbose_name='Версия')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала действия')),
                ('refbook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='terminology.refbook', verbose_name='Справочник')),
            ],
            options={
                'verbose_name': 'Версия справочника',
                'verbose_name_plural': 'Версии справочников',
                'ordering': ('refbook__code', '-start_date', '-id'),
            },
        ),
        migrations.CreateModel(
            name='RefBookElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Код элемента')),
                ('value', models.CharField(max_length=300, verbose_name='Значение элемента')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='terminology.refbookversion', verbose_name='Версия справочника')),
            ],
            options={
                'verbose_name': 'Элемент справочника',
                'verbose_name_plural': 'Элементы справочника',
                'ordering': ('code',),
            },
        ),
        migrations.AddConstraint(
            model_name='refbookversion',
            constraint=models.UniqueConstraint(fields=('refbook', 'version'), name='uniq_refbook_version'),
        ),
        migrations.AddConstraint(
            model_name='refbookversion',
            constraint=models.UniqueConstraint(fields=('refbook', 'start_date'), name='uniq_refbook_start_date'),
        ),
        migrations.AddConstraint(
            model_name='refbookelement',
            constraint=models.UniqueConstraint(fields=('version', 'code'), name='uniq_element_code_in_version'),
        ),
    ]
