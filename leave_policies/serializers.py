from rest_framework import serializers
from .models import LeavePolicy


class LeavePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = '__all__'
