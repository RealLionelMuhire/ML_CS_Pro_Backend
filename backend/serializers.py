# backend/serializers.py
from rest_framework import serializers
from .models import CustomUser, Client, Action

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    elapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = ['title', 'objective', 'start_time', 'end_time', 'description', 'is_active', 'elapsed_time', 'sum_elapsed_time']

    def get_elapsed_time(self, obj):
        start_time = obj.start_time
        end_time = obj.end_time

        if start_time and end_time:
            elapsed_time = end_time - start_time
            elapsed_time_minutes = elapsed_time.total_seconds() / 60
            return elapsed_time_minutes
        return None
