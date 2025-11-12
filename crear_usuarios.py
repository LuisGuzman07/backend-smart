import os
import json
import random
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

from django.contrib.auth.models import User, Group
from perfiles.models import Cliente, Empleado

def crear_usuarios():
    # Crear grupos si no existen
    cliente_group, _ = Group.objects.get_or_create(name='cliente')
    empleado_group, _ = Group.objects.get_or_create(name='empleado')
    admin_group, _ = Group.objects.get_or_create(name='administrador')

    direcciones = [
        "Av. Cristo Redentor 123, Santa Cruz de la Sierra, Bolivia",
        "Calle Sucre 456, Barrio Equipetrol, Santa Cruz",
        "Plaza 24 de Septiembre 789, Centro, Santa Cruz de la Sierra",
        "Av. San Martín 101, Barrio Norte, Santa Cruz",
        "Calle Bolívar 202, Zona Sur, Santa Cruz de la Sierra",
        "Av. Irala 303, Barrio Universitario, Santa Cruz",
        "Calle Warnes 404, Zona Industrial, Santa Cruz de la Sierra",
        "Av. Cañoto 505, Barrio Los Lotes, Santa Cruz",
        "Calle Monseñor Rivero 606, Centro Histórico, Santa Cruz de la Sierra",
        "Av. Busch 707, Barrio Mutualista, Santa Cruz",
        "Calle 1, Santa Cruz de la Sierra, Bolivia",
        "Calle 2, Santa Cruz de la Sierra, Bolivia",
        "Calle 3, Santa Cruz de la Sierra, Bolivia",
        "Calle 4, Santa Cruz de la Sierra, Bolivia",
        "Calle 5, Santa Cruz de la Sierra, Bolivia",
        "Calle 6, Santa Cruz de la Sierra, Bolivia",
        "Calle 7, Santa Cruz de la Sierra, Bolivia",
        "Calle 8, Santa Cruz de la Sierra, Bolivia",
        "Calle 9, Santa Cruz de la Sierra, Bolivia",
        "Calle 10, Santa Cruz de la Sierra, Bolivia",
        "Calle 11, Santa Cruz de la Sierra, Bolivia",
        "Calle 12, Santa Cruz de la Sierra, Bolivia",
        "Calle 13, Santa Cruz de la Sierra, Bolivia",
        "Calle 14, Santa Cruz de la Sierra, Bolivia",
        "Calle 15, Santa Cruz de la Sierra, Bolivia",
        "Calle 16, Santa Cruz de la Sierra, Bolivia",
        "Calle 17, Santa Cruz de la Sierra, Bolivia",
        "Calle 18, Santa Cruz de la Sierra, Bolivia",
        "Calle 19, Santa Cruz de la Sierra, Bolivia",
        "Calle 20, Santa Cruz de la Sierra, Bolivia",
        "Calle 21, Santa Cruz de la Sierra, Bolivia",
        "Calle 22, Santa Cruz de la Sierra, Bolivia",
        "Calle 23, Santa Cruz de la Sierra, Bolivia",
        "Calle 24, Santa Cruz de la Sierra, Bolivia",
        "Calle 25, Santa Cruz de la Sierra, Bolivia",
        "Calle 26, Santa Cruz de la Sierra, Bolivia",
        "Calle 27, Santa Cruz de la Sierra, Bolivia",
        "Calle 28, Santa Cruz de la Sierra, Bolivia",
        "Calle 29, Santa Cruz de la Sierra, Bolivia",
        "Calle 30, Santa Cruz de la Sierra, Bolivia"
    ]
    with open('nuevos_usuarios.json', 'r', encoding='utf-8') as f:
        usuarios_data = json.load(f)

    for i, user_data in enumerate(usuarios_data):
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'first_name': user_data['nombre'],
                'last_name': user_data['apellido'],
                'email': user_data['email'],
            }
        )
        if created:
            user.set_password('pass3210')
            user.save()
            print(f"Usuario {user.username} creado.")
        else:
            print(f"Usuario {user.username} ya existe, actualizando perfil.")

        rol = user_data.get('rol', 'cliente')

        if rol == 'cliente':
            sexo = 'F' if user_data['nombre'].endswith('a') else 'M'
            ci = f"{10000030 + i}"
            direccion = direcciones[i % len(direcciones)]
            telefono = f"+591 7{random.randint(10000000, 99999999)}"
            estado = 'inactivo' if i % 10 == 0 else 'activo'

            cliente, cliente_created = Cliente.objects.get_or_create(
                usuario=user,
                defaults={
                    'nombre': user_data['nombre'],
                    'apellido': user_data['apellido'],
                    'sexo': sexo,
                    'ci': ci,
                    'direccion': direccion,
                    'telefono': telefono,
                    'estado': estado,
                }
            )
            if cliente_created:
                print(f"Cliente {user.username} creado.")
            else:
                # Actualizar campos si faltan
                updated = False
                if not cliente.sexo:
                    cliente.sexo = sexo
                    updated = True
                if not cliente.ci:
                    cliente.ci = ci
                    updated = True
                if not cliente.direccion:
                    cliente.direccion = direccion
                    updated = True
                if not cliente.telefono:
                    cliente.telefono = telefono
                    updated = True
                if cliente.estado != estado:
                    cliente.estado = estado
                    updated = True
                if updated:
                    cliente.save()
                    print(f"Cliente {user.username} actualizado.")
                else:
                    print(f"Cliente {user.username} ya existe.")
            user.groups.add(cliente_group)
            print(f"Grupo 'cliente' asignado a {user.username}.")
        elif rol == 'empleado':
            sexo = 'F' if user_data['nombre'].endswith('a') else 'M'
            cargo = user_data.get('cargo', 'GESTOR_PEDIDOS')
            empleado, empleado_created = Empleado.objects.get_or_create(
                usuario=user,
                defaults={
                    'nombre': user_data['nombre'],
                    'apellido': user_data['apellido'],
                    'sexo': sexo,
                    'cargo': cargo,
                }
            )
            if empleado_created:
                print(f"Empleado {user.username} ({cargo}) creado.")
            else:
                # Actualizar si cambió
                if empleado.cargo != cargo:
                    empleado.cargo = cargo
                    empleado.save()
                    print(f"Empleado {user.username} actualizado a {cargo}.")
                else:
                    print(f"Empleado {user.username} ya existe con {cargo}.")
            user.groups.add(empleado_group)
            print(f"Grupo 'empleado' asignado a {user.username}.")

if __name__ == '__main__':
    crear_usuarios()