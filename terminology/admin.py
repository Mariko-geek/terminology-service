from django.contrib import admin

from .models import RefBook, RefBookElement, RefBookVersion

admin.site.site_header = 'Сервис терминологии'
admin.site.site_title = 'Сервис терминологии'
admin.site.index_title = 'Управление справочниками'


class RefBookVersionInline(admin.TabularInline):
    model = RefBookVersion
    extra = 0
    fields = ('version', 'start_date')
    show_change_link = True


@admin.register(RefBook)
class RefBookAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'name',
        'current_version_value',
        'current_version_start_date',
    )
    search_fields = ('code', 'name')
    inlines = (RefBookVersionInline,)

    @admin.display(description='Текущая версия')
    def current_version_value(self, obj):
        version = obj.current_version
        return version.version if version else '—'

    @admin.display(description='Дата начала действия версии')
    def current_version_start_date(self, obj):
        version = obj.current_version
        return version.start_date if version else None


class RefBookElementInline(admin.TabularInline):
    model = RefBookElement
    extra = 1
    fields = ('code', 'value')


@admin.register(RefBookVersion)
class RefBookVersionAdmin(admin.ModelAdmin):
    list_display = ('refbook_code', 'refbook_name', 'version', 'start_date')
    list_filter = ('refbook',)
    search_fields = ('refbook__code', 'refbook__name', 'version')
    autocomplete_fields = ('refbook',)
    inlines = (RefBookElementInline,)

    @admin.display(description='Код справочника', ordering='refbook__code')
    def refbook_code(self, obj):
        return obj.refbook.code

    @admin.display(description='Наименование справочника', ordering='refbook__name')
    def refbook_name(self, obj):
        return obj.refbook.name


@admin.register(RefBookElement)
class RefBookElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'code', 'value')
    list_filter = ('version__refbook', 'version')
    search_fields = ('code', 'value', 'version__refbook__code')
    autocomplete_fields = ('version',)
