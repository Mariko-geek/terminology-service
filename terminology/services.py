from django.utils import timezone
from rest_framework.exceptions import NotFound


def get_version(refbook, version_value=None, target_date=None):
    """Выбрать указанную версию либо текущую на заданную/сегодняшнюю дату."""
    if version_value:
        version = refbook.versions.filter(version=version_value).first()
        if version is None:
            raise NotFound('Указанная версия справочника не найдена.')
        return version

    target_date = target_date or timezone.localdate()
    version = refbook.version_for_date(target_date)
    if version is None:
        raise NotFound('У справочника нет версии, действующей на указанную дату.')
    return version
