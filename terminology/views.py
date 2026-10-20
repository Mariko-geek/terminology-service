from datetime import date

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RefBook
from .serializers import (
    CheckElementResponseSerializer,
    RefBookElementSerializer,
    RefBookElementsResponseSerializer,
    RefBookListResponseSerializer,
    RefBookSerializer,
)
from .services import get_version


def _parse_iso_date(raw_value):
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


class RefBookListView(APIView):
    @extend_schema(
        summary='Получение списка справочников',
        parameters=[
            OpenApiParameter(
                name='date',
                description='Дата в формате ГГГГ-ММ-ДД. Возвращаются справочники, у которых к этой дате уже есть действующая версия.',
                required=False,
                type=str,
            ),
        ],
        responses={200: RefBookListResponseSerializer},
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    'refbooks': [
                        {'id': '1', 'code': 'MS1', 'name': 'Специальности медицинских работников'}
                    ]
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        raw_date = request.query_params.get('date')
        target_date = _parse_iso_date(raw_date)
        if raw_date and target_date is None:
            return Response(
                {'detail': 'Параметр date должен быть в формате ГГГГ-ММ-ДД.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = RefBook.objects.all()
        if target_date:
            queryset = queryset.filter(
                versions__start_date__lte=target_date,
            ).distinct()

        data = RefBookSerializer(queryset, many=True).data
        return Response({'refbooks': data})


class RefBookElementsView(APIView):
    @extend_schema(
        summary='Получение элементов заданного справочника',
        parameters=[
            OpenApiParameter(
                name='version',
                description='Версия справочника. Если не указана — используется текущая версия.',
                required=False,
                type=str,
            ),
        ],
        responses={200: RefBookElementsResponseSerializer},
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    'elements': [
                        {'code': 'Z01.6', 'value': 'Радиологическое обследование, не классифицированное в других рубриках'},
                        {'code': 'Z01.7', 'value': 'Лабораторное обследование'},
                    ]
                },
                response_only=True,
            )
        ],
    )
    def get(self, request, pk):
        refbook = get_object_or_404(RefBook, pk=pk)
        version = get_version(refbook, request.query_params.get('version'))
        elements = version.elements.all()
        return Response({
            'elements': RefBookElementSerializer(elements, many=True).data,
        })


class CheckElementView(APIView):
    @extend_schema(
        summary='Валидация элемента справочника',
        description='Проверяет, существует ли одновременно указанный код и указанное значение в версии справочника.',
        parameters=[
            OpenApiParameter(name='code', required=True, type=str, description='Код элемента'),
            OpenApiParameter(name='value', required=True, type=str, description='Значение элемента'),
            OpenApiParameter(
                name='version',
                required=False,
                type=str,
                description='Версия. Если не указана — используется текущая версия.',
            ),
        ],
        responses={200: CheckElementResponseSerializer},
        examples=[
            OpenApiExample(
                'Элемент найден',
                value={'valid': True},
                response_only=True,
            ),
            OpenApiExample(
                'Элемент не найден',
                value={'valid': False},
                response_only=True,
            ),
        ],
    )
    def get(self, request, pk):
        code = request.query_params.get('code')
        value = request.query_params.get('value')
        if not code or value is None:
            return Response(
                {'detail': 'Параметры code и value обязательны.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refbook = get_object_or_404(RefBook, pk=pk)
        version = get_version(refbook, request.query_params.get('version'))
        valid = version.elements.filter(code=code, value=value).exists()
        return Response({'valid': valid})
