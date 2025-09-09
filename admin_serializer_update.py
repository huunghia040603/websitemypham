# Thêm vào file serializers.py

class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin model
    """
    class Meta:
        model = Admin
        fields = ('id', 'name', 'email', 'phone_number', 'address', 'dob', 'avatar', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        """
        Create a new admin user
        """
        password = validated_data.pop('password', None)
        admin = Admin.objects.create(**validated_data)
        if password:
            admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        return admin

    def update(self, instance, validated_data):
        """
        Update admin user
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
 
 
 
 