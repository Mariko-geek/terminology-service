from rest_framework import serializers
from .models import RefBook, RefBookElement


class RefBookSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = RefBook
        fields = ('id', 'code', 'name')


class RefBookElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefBookElement
        fields = ('code', 'value')


class RefBookListResponseSerializer(serializers.Serializer):
    refbooks = RefBookSerializer(many=True)


class RefBookElementsResponseSerializer(serializers.Serializer):
    elements = RefBookElementSerializer(many=True)


class CheckElementResponseSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
