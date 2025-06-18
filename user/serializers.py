from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("username")
        password = attrs.get("password")

        user = None

        # Try to find user by email or phone number
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=identifier)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    pass

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            data = super().get_token(user)
            return {
                "refresh": str(data),
                "access": str(data.access_token),
            }
        else:
            raise serializers.ValidationError("Invalid credentials.")


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'middle_name', 'last_name', 'email', 'is_staff', 'is_driver', 'is_active', 'is_superuser', 'phone_number']

    def validate(self, attrs):
        request = self.context.get('request')
        
        # On create, require password
        if request and request.method == 'POST':
            if 'password' not in attrs:
                raise serializers.ValidationError({"password": "This field is required."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Update the rest of the fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle password securely
        if password:
            instance.set_password(password)

        instance.save()
        return instance