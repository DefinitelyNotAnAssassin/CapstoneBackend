from rest_framework import serializers
from .models import LeavePackage, LeavePackageItem


class LeavePackageItemSerializer(serializers.ModelSerializer):
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)

    class Meta:
        model = LeavePackageItem
        fields = ['id', 'leave_type', 'leave_type_display', 'quantity']


class LeavePackageSerializer(serializers.ModelSerializer):
    items = LeavePackageItemSerializer(many=True, read_only=True)

    class Meta:
        model = LeavePackage
        fields = ['id', 'name', 'description', 'is_active', 'is_predefined', 'items', 'created_at', 'updated_at']
        read_only_fields = ['is_predefined']


class LeavePackageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating packages with nested items."""
    items = LeavePackageItemSerializer(many=True)

    class Meta:
        model = LeavePackage
        fields = ['id', 'name', 'description', 'is_active', 'items', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        package = LeavePackage.objects.create(**validated_data)
        for item_data in items_data:
            LeavePackageItem.objects.create(package=package, **item_data)
        return package

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        if items_data is not None:
            # Replace all items
            instance.items.all().delete()
            for item_data in items_data:
                LeavePackageItem.objects.create(package=instance, **item_data)

        return instance
