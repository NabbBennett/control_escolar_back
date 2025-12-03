from django.shortcuts import render
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django.core import serializers
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from control_escolar_desit_api.serializers import *
from control_escolar_desit_api.models import *
from datetime import datetime, timedelta
import json

class MateriasView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            materia_id = request.GET.get("id", None)
            
            if materia_id:
                materia = Materias.objects.get(id=materia_id)
                materia_serializer = MateriaSerializer(materia)
                return Response(materia_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No se proporcionó el ID de la materia"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except Materias.DoesNotExist:
            return Response({"error": "La materia no existe"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos 
            nrc = request.data.get("nrc", None)
            nombre = request.data.get("nombre", None)
            seccion = request.data.get("seccion", None)
            dias = request.data.get("dias", None)
            hora_inicio = request.data.get("hora_inicio", None)
            hora_fin = request.data.get("hora_fin", None)
            salon = request.data.get("salon", None)
            programa_educativo = request.data.get("programa_educativo", None)
            profesor_id = request.data.get("profesor_id", None)
            creditos = request.data.get("creditos", None)

            # Validar campos 
            if not all([nrc, nombre, seccion, dias, hora_inicio, hora_fin, 
                       salon, programa_educativo, profesor_id, creditos]):
                return Response({"error": "Todos los campos son obligatorios"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Verificar que el NRC no exista
            if Materias.objects.filter(nrc=nrc).exists():
                return Response({"error": "El NRC ya está registrado"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Obtener el profesor
            try:
                profesor = Maestros.objects.get(id=profesor_id)
            except Maestros.DoesNotExist:
                return Response({"error": "El profesor no existe"}, 
                              status=status.HTTP_404_NOT_FOUND)

            # Crear la materia
            materia = Materias.objects.create(
                nrc=nrc,
                nombre=nombre,
                seccion=seccion,
                dias=dias,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                salon=salon,
                programa_educativo=programa_educativo,
                profesor=profesor,
                creditos=creditos
            )

            materia_serializer = MateriaSerializer(materia)
            return Response({
                "message": "Materia creada exitosamente",
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        #Actualizar
        try:
            materia_id = request.data.get("id", None)
            
            if not materia_id:
                return Response({"error": "No se proporcionó el ID de la materia"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            try:
                materia = Materias.objects.get(id=materia_id)
            except Materias.DoesNotExist:
                return Response({"error": "La materia no existe"}, 
                              status=status.HTTP_404_NOT_FOUND)

            # Actualizar campos
            nrc = request.data.get("nrc", materia.nrc)
            
            # Verificar que el NRC no esté duplicado
            if nrc != materia.nrc and Materias.objects.filter(nrc=nrc).exists():
                return Response({"error": "El NRC ya está registrado"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            materia.nrc = nrc
            materia.nombre = request.data.get("nombre", materia.nombre)
            materia.seccion = request.data.get("seccion", materia.seccion)
            materia.dias = request.data.get("dias", materia.dias)
            materia.hora_inicio = request.data.get("hora_inicio", materia.hora_inicio)
            materia.hora_fin = request.data.get("hora_fin", materia.hora_fin)
            materia.salon = request.data.get("salon", materia.salon)
            materia.programa_educativo = request.data.get("programa_educativo", materia.programa_educativo)
            materia.creditos = request.data.get("creditos", materia.creditos)

            # Actualizar profesor
            profesor_id = request.data.get("profesor_id", None)
            if profesor_id:
                try:
                    profesor = Maestros.objects.get(id=profesor_id)
                    materia.profesor = profesor
                except Maestros.DoesNotExist:
                    return Response({"error": "El profesor no existe"}, 
                                  status=status.HTTP_404_NOT_FOUND)

            materia.save()

            materia_serializer = MateriaSerializer(materia)
            return Response({
                "message": "Materia actualizada exitosamente",
                "materia": materia_serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        
        #Eliminar una materia
        try:
            materia_id = request.GET.get("id", None)
            
            if not materia_id:
                return Response({"error": "No se proporcionó el ID de la materia"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            try:
                materia = Materias.objects.get(id=materia_id)
                materia.delete()
                return Response({"message": "Materia eliminada exitosamente"}, 
                              status=status.HTTP_200_OK)
            except Materias.DoesNotExist:
                return Response({"error": "La materia no existe"}, 
                              status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MateriasAll(APIView):
    
    #Vista para obtener todas las materias

    def get(self, request, *args, **kwargs):
        try:
            search = request.GET.get('search', '').strip()
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '10')

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            try:
                page_size = int(page_size)
            except ValueError:
                page_size = 10
            page_size = max(1, min(page_size, 100))  # Limitar entre 1 y 100

            queryset = Materias.objects.all()

            if search:
                queryset = queryset.filter(
                    Q(nrc__icontains=search) |
                    Q(nombre__icontains=search) |
                    Q(seccion__icontains=search) |
                    Q(programa_educativo__icontains=search) |
                    Q(profesor__user__first_name__icontains=search) |
                    Q(profesor__user__last_name__icontains=search)
                )

            queryset = queryset.order_by('nrc')

            total = queryset.count()
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            if page > total_pages:
                page = total_pages

            start = (page - 1) * page_size
            end = start + page_size
            page_items = list(queryset[start:end])

            serializer = MateriaSerializer(page_items, many=True)
            return Response({
                'results': serializer.data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerificarNRC(APIView):

    # Verificar si un NRC ya existe
 
    def get(self, request, *args, **kwargs):
        try:
            nrc = request.GET.get("nrc", None)
            
            if not nrc:
                return Response({"error": "No se proporcionó el NRC"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            existe = Materias.objects.filter(nrc=nrc).exists()
            return Response({"existe": existe}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MateriasRegistradasPorDia(APIView):

    def get(self, request, *args, **kwargs):
        try:
            # Obtener fecha actual y hace 7 días
            fecha_fin = timezone.now()
            fecha_inicio = fecha_fin - timedelta(days=6)  # Últimos 7 días incluyendo hoy
            
            # Nombres de días en español
            dias_semana = {
                0: 'Lun',  # Lunes
                1: 'Mar',  # Martes
                2: 'Mié',  # Miércoles
                3: 'Jue',  # Jueves
                4: 'Vie',  # Viernes
                5: 'Sáb',  # Sábado
                6: 'Dom'   # Domingo
            }
            
            # Inicializar contadores para cada día
            labels = []
            data = []
            
            # Iterar sobre los últimos 7 días
            for i in range(7):
                dia_actual = fecha_inicio + timedelta(days=i)
                dia_siguiente = dia_actual + timedelta(days=1)
                
                # Contar materias creadas en ese día
                count = Materias.objects.filter(
                    creation__gte=dia_actual,
                    creation__lt=dia_siguiente
                ).count()
                
                # Obtener nombre del día
                dia_semana_num = dia_actual.weekday()
                nombre_dia = dias_semana.get(dia_semana_num, 'N/A')
                
                labels.append(nombre_dia)
                data.append(count)
            
            return Response({
                "labels": labels,
                "data": data,
                "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_fin": fecha_fin.strftime('%Y-%m-%d')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
