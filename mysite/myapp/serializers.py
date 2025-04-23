from rest_framework import serializers

class SymptomInputSerializer(serializers.Serializer):
    symptoms = serializers.CharField(max_length=500)


class ImageUploadSerializer(serializers.Serializer):
    file = serializers.FileField()