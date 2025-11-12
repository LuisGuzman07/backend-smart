from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Cliente, Empleado

# Campo personalizado para aceptar ID o objeto anidado
class UserPKOrNestedField(serializers.PrimaryKeyRelatedField):
	def to_representation(self, value):
		return value.pk

User = get_user_model()

class ClienteSerializer(serializers.ModelSerializer):
	usuario_info = serializers.SerializerMethodField(read_only=True)
	usuario = UserPKOrNestedField(queryset=User.objects.all(), required=False, allow_null=True)

	class Meta:
		model = Cliente
		fields = [
			'id', 'nombre', 'apellido', 'ci', 'telefono',
			'direccion', 'estado', 'sexo', 'usuario', 'usuario_info'
		]
		read_only_fields = ('id',)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance:
			self.fields['ci'].required = False
			self.fields['telefono'].required = False

	def get_usuario_info(self, obj):
		if not obj.usuario:
			return None
		return {
			'id': obj.usuario.id,
			'username': getattr(obj.usuario, 'username', None),
			'email': getattr(obj.usuario, 'email', None),
		}

	def validate_nombre(self, value):
		value = value.strip()
		if len(value) < 2:
			raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
		return value

	def validate_apellido(self, value):
		value = value.strip()
		if value == "":
			return value
		if len(value) < 2:
			raise serializers.ValidationError("El apellido debe tener al menos 2 caracteres si se proporciona.")
		return value

	def validate_telefono(self, value):
		value = value.strip()
		if value == "":
			return value
		qs = Cliente.objects.filter(telefono=value)
		if self.instance:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("Este teléfono ya está registrado.")
		if not value.isdigit():
			raise serializers.ValidationError("El teléfono solo puede contener números.")
		return value

	def validate_ci(self, value):
		value = value.strip()
		qs = Cliente.objects.filter(ci=value)
		if self.instance:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("Este CI ya está registrado.")
		return value

	def create(self, validated_data):
		return Cliente.objects.create(**validated_data)

	def update(self, instance, validated_data):
		return super().update(instance, validated_data)


class EmpleadoSerializer(serializers.ModelSerializer):
	usuario_info = serializers.SerializerMethodField(read_only=True)
	usuario = UserPKOrNestedField(queryset=User.objects.all(), required=True)

	class Meta:
		model = Empleado
		fields = [
			'id', 'nombre', 'apellido', 'ci', 'telefono', 'sexo', 'direccion',
			'estado', 'fecha_nacimiento', 'cargo', 'sueldo', 'usuario', 'usuario_info'
		]
		read_only_fields = ('id',)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance:
			self.fields['ci'].required = False
			self.fields['telefono'].required = False

	def get_usuario_info(self, obj):
		if not obj.usuario:
			return None
		return {
			'id': obj.usuario.id,
			'username': getattr(obj.usuario, 'username', None),
			'email': getattr(obj.usuario, 'email', None),
		}

	def validate_nombre(self, value):
		value = value.strip()
		if len(value) < 2:
			raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
		return value

	def validate_apellido(self, value):
		value = value.strip()
		if value == "":
			return value
		if len(value) < 2:
			raise serializers.ValidationError("El apellido debe tener al menos 2 caracteres si se proporciona.")
		return value

	def validate_telefono(self, value):
		value = value.strip()
		if value == "":
			return value
		qs = Empleado.objects.filter(telefono=value)
		if self.instance:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("Este teléfono ya está registrado.")
		if not value.isdigit():
			raise serializers.ValidationError("El teléfono solo puede contener números.")
		return value

	def validate_ci(self, value):
		value = value.strip()
		qs = Empleado.objects.filter(ci=value)
		if self.instance:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("Este CI ya está registrado.")
		return value

	def validate_usuario(self, value):
		if not value:
			raise serializers.ValidationError("El campo usuario es obligatorio.")
		# Verificar si el usuario ya está asignado a otro empleado
		qs = Empleado.objects.filter(usuario=value)
		if self.instance:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("Este usuario ya está asignado a otro empleado.")
		return value

	def create(self, validated_data):
		return Empleado.objects.create(**validated_data)

	def update(self, instance, validated_data):
		return super().update(instance, validated_data)
