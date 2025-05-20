from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    用于用户信息的序列化和反序列化
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'confirm_password', 'email', 'is_active']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        """
        验证密码是否匹配
        """
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})
        return attrs

    def create(self, validated_data):
        """
        创建用户
        """
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        更新用户信息
        """
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器
    用于用户列表展示，不包含敏感信息
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined']
        read_only_fields = fields