from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class serializer_user(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=False)
	groups = serializers.PrimaryKeyRelatedField(
		many=True, 
		queryset=Group.objects.all(), 
		required=False
	)
	role = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'is_active', 'password', 'groups', 'role']
		read_only_fields = ['id', 'role']

	def get_role(self, obj):
		"""Devuelve el nombre del primer grupo/rol asignado al usuario"""
		first_group = obj.groups.first()
		return first_group.name if first_group else None

	def create(self, validated_data):
		groups = validated_data.pop('groups', [])
		password = validated_data.pop('password', None)
		user = User(**validated_data)
		if password:
			user.set_password(password)
		user.save()
		if groups:
			user.groups.set(groups)
		return user

	def update(self, instance, validated_data):
		groups = validated_data.pop('groups', None)
		password = validated_data.pop('password', None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		if password:
			instance.set_password(password)
		if groups is not None:
			instance.groups.set(groups)
		instance.save()
		return instance
