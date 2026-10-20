from django.db import models
from django.utils import timezone


class RefBook(models.Model):
    code = models.CharField('Код', max_length=100, unique=True)
    name = models.CharField('Наименование', max_length=300)
    description = models.TextField('Описание', blank=True)

    class Meta:
        ordering = ('code',)
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'

    def __str__(self):
        return f'{self.code} — {self.name}'

    def version_for_date(self, target_date=None):
        """Последняя версия, уже вступившая в действие на target_date."""
        target_date = target_date or timezone.localdate()
        return (
            self.versions
            .filter(start_date__lte=target_date)
            .order_by('-start_date', '-id')
            .first()
        )

    @property
    def current_version(self):
        return self.version_for_date()


class RefBookVersion(models.Model):
    refbook = models.ForeignKey(
        RefBook,
        verbose_name='Справочник',
        related_name='versions',
        on_delete=models.CASCADE,
    )
    version = models.CharField('Версия', max_length=50)
    start_date = models.DateField('Дата начала действия', null=True, blank=True)

    class Meta:
        ordering = ('refbook__code', '-start_date', '-id')
        verbose_name = 'Версия справочника'
        verbose_name_plural = 'Версии справочников'
        constraints = [
            models.UniqueConstraint(
                fields=('refbook', 'version'),
                name='uniq_refbook_version',
            ),
            models.UniqueConstraint(
                fields=('refbook', 'start_date'),
                name='uniq_refbook_start_date',
            ),
        ]

    def __str__(self):
        return f'{self.refbook.code} — {self.version}'


class RefBookElement(models.Model):
    version = models.ForeignKey(
        RefBookVersion,
        verbose_name='Версия справочника',
        related_name='elements',
        on_delete=models.CASCADE,
    )
    code = models.CharField('Код элемента', max_length=100)
    value = models.CharField('Значение элемента', max_length=300)

    class Meta:
        ordering = ('code',)
        verbose_name = 'Элемент справочника'
        verbose_name_plural = 'Элементы справочника'
        constraints = [
            models.UniqueConstraint(
                fields=('version', 'code'),
                name='uniq_element_code_in_version',
            ),
        ]

    def __str__(self):
        return f'{self.code} — {self.value}'
