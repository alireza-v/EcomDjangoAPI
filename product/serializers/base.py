from rest_framework import serializers


class BaseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Remove null values
    """

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {k: v for k, v in rep.items() if v not in (None, "", [], {})}
