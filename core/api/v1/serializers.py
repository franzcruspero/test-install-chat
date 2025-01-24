from constance import config
from rest_framework import serializers


class ConstanceSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()

    def to_representation(self, instance):
        return {
            "key": instance[0],
            "value": getattr(config, instance[0]),
        }
class SocialAccountSerializer(serializers.Serializer):
    providers = serializers.ListField(child=serializers.CharField())

    def to_representation(self, instance):
        return {"providers": instance}

class DisconnectSocialAccountSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True)
