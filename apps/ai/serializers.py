from rest_framework import serializers
from .models import AIConversation, AIMessage, AIPrediction

class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = '__all__'
        read_only_fields = ('created_at',)

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = AIConversation
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class AIPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'is_accurate')
