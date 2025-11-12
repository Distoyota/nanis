# app.py - Versión con relaciones
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_mascotas_2024'

# Configuración de Supabase API
SUPABASE_URL = 'https://rexjcxtxbxjgdbblslfu.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJleGpjeHR4YnhqZ2RiYmxzbGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjExODYsImV4cCI6MjA3ODM5NzE4Nn0.GfERK-lud6Kef9jDKouA7b5ICwHI8EFvXthFddiIXug'  # Copia el "anon public" key

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ========== FUNCIONES AUXILIARES ==========

def crear_o_obtener_fecha(fecha_str):
    """Crea o obtiene una fecha en el calendario"""
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
    
    # Buscar si ya existe
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/calendario?fecha=eq.{fecha_str}',
        headers=HEADERS
    )
    
    if response.status_code == 200 and response.json():
        return response.json()[0]['id']
    
    # Si no existe, crear
    fecha_data = {
        'fecha': fecha_str,
        'dia_semana': fecha_obj.strftime('%A'),
        'mes': fecha_obj.strftime('%B'),
        'anio': fecha_obj.year
    }
    
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/calendario',
        headers=HEADERS,
        json=fecha_data
    )
    
    if response.status_code in [200, 201]:
        return response.json()[0]['id']
    return None

def obtener_ciudades():
    """Obtiene la lista de ciudades"""
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/ciudades?order=nombre.asc',
        headers=HEADERS
    )
    if response.status_code == 200:
        return response.json()
    return []

def obtener_reporte_completo(reporte_id):
    """Obtiene un reporte con todas sus relaciones"""
    # Obtener reporte
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/reportes_perdida?id=eq.{reporte_id}',
        headers=HEADERS
    )
    if response.status_code != 200 or not response.json():
        return None
    
    reporte = response.json()[0]
    
    # Obtener mascota
    mascota_resp = requests.get(
        f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{reporte["mascota_id"]}',
        headers=HEADERS
    )
    reporte['mascota'] = mascota_resp.json()[0] if mascota_resp.json() else {}
    
    # Obtener propietario
    if reporte['mascota']:
        prop_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/propietarios?id=eq.{reporte["mascota"]["propietario_id"]}',
            headers=HEADERS
        )
        reporte['propietario'] = prop_resp.json()[0] if prop_resp.json() else {}
    
    # Obtener ciudad del propietario
    if reporte.get('propietario') and reporte['propietario'].get('ciudad_id'):
        ciudad_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/ciudades?id=eq.{reporte["propietario"]["ciudad_id"]}',
            headers=HEADERS
        )
        reporte['ciudad_propietario'] = ciudad_resp.json()[0] if ciudad_resp.json() else {}
    
    # Obtener ciudad de pérdida
    if reporte.get('ciudad_perdida_id'):
        ciudad_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/ciudades?id=eq.{reporte["ciudad_perdida_id"]}',
            headers=HEADERS
        )
        reporte['ciudad_perdida'] = ciudad_resp.json()[0] if ciudad_resp.json() else {}
    
    # Obtener fecha
    if reporte.get('fecha_perdida_id'):
        fecha_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/calendario?id=eq.{reporte["fecha_perdida_id"]}',
            headers=HEADERS
        )
        reporte['fecha'] = fecha_resp.json()[0] if fecha_resp.json() else {}
    
    return reporte

# ========== RUTAS ==========

@app.route('/')
def index():
    """Página de bienvenida con el perrito animado"""
    return render_template('index.html')



@app.route('/mascotas')
def mascotas_index():
    """Lista todos los reportes de mascotas perdidas"""
    try:
        # Obtener todos los reportes
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/reportes_perdida?order=created_at.desc',
            headers=HEADERS
        )
        
        if response.status_code != 200:
            flash('Error al cargar reportes', 'error')
            return render_template('index.html', reportes=[])
        
        reportes = response.json()
        
        # Enriquecer cada reporte con sus datos relacionados
        for reporte in reportes:
            # Obtener mascota
            mascota_resp = requests.get(
                f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{reporte["mascota_id"]}',
                headers=HEADERS
            )
            reporte['mascota'] = mascota_resp.json()[0] if mascota_resp.json() else {}
            
            # Obtener propietario
            if reporte['mascota']:
                prop_resp = requests.get(
                    f'{SUPABASE_URL}/rest/v1/propietarios?id=eq.{reporte["mascota"]["propietario_id"]}',
                    headers=HEADERS
                )
                reporte['propietario'] = prop_resp.json()[0] if prop_resp.json() else {}
            
            # Obtener ciudad de pérdida
            if reporte.get('ciudad_perdida_id'):
                ciudad_resp = requests.get(
                    f'{SUPABASE_URL}/rest/v1/ciudades?id=eq.{reporte["ciudad_perdida_id"]}',
                    headers=HEADERS
                )
                reporte['ciudad_perdida'] = ciudad_resp.json()[0] if ciudad_resp.json() else {}
            
            # Obtener fecha
            if reporte.get('fecha_perdida_id'):
                fecha_resp = requests.get(
                    f'{SUPABASE_URL}/rest/v1/calendario?id=eq.{reporte["fecha_perdida_id"]}',
                    headers=HEADERS
                )
                reporte['fecha'] = fecha_resp.json()[0] if fecha_resp.json() else {}
        
        return render_template('index_relacional.html', reportes=reportes)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('index_relacional.html', reportes=[])

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    """Crear nuevo reporte de mascota perdida"""
    if request.method == 'POST':
        try:
            # 1. Crear o buscar propietario
            identificacion = request.form['identificacion']
            
            # Buscar si el propietario ya existe
            prop_response = requests.get(
                f'{SUPABASE_URL}/rest/v1/propietarios?identificacion=eq.{identificacion}',
                headers=HEADERS
            )
            
            if prop_response.status_code == 200 and prop_response.json():
                propietario_id = prop_response.json()[0]['id']
            else:
                # Crear nuevo propietario
                propietario_data = {
                    'identificacion': identificacion,
                    'nombre': request.form['nombre_propietario'],
                    'apellido': request.form['apellido_propietario'],
                    'email': request.form.get('email', ''),
                    'telefono': request.form['telefono_propietario'],
                    'direccion': request.form.get('direccion', ''),
                    'ciudad_id': int(request.form['ciudad_propietario'])
                }
                
                prop_response = requests.post(
                    f'{SUPABASE_URL}/rest/v1/propietarios',
                    headers=HEADERS,
                    json=propietario_data
                )
                
                if prop_response.status_code not in [200, 201]:
                    flash('Error al crear propietario', 'error')
                    return redirect(url_for('crear'))
                
                propietario_id = prop_response.json()[0]['id']
            
            # 2. Crear mascota
            mascota_data = {
                'nombre': request.form['nombre_mascota'],
                'tipo': request.form['tipo'],
                'raza': request.form.get('raza', ''),
                'color': request.form['color'],
                'edad': int(request.form['edad']) if request.form.get('edad') else None,
                'descripcion': request.form.get('descripcion', ''),
                'propietario_id': propietario_id
            }
            
            mascota_response = requests.post(
                f'{SUPABASE_URL}/rest/v1/mascotas',
                headers=HEADERS,
                json=mascota_data
            )
            
            if mascota_response.status_code not in [200, 201]:
                flash('Error al crear mascota', 'error')
                return redirect(url_for('crear'))
            
            mascota_id = mascota_response.json()[0]['id']
            
            # 3. Crear o obtener fecha
            fecha_id = crear_o_obtener_fecha(request.form['fecha_perdida'])
            
            # 4. Crear reporte de pérdida
            reporte_data = {
                'mascota_id': mascota_id,
                'fecha_perdida_id': fecha_id,
                'ciudad_perdida_id': int(request.form['ciudad_perdida']),
                'ubicacion_detallada': request.form['ubicacion_detallada'],
                'estado': 'Perdida'
            }
            
            reporte_response = requests.post(
                f'{SUPABASE_URL}/rest/v1/reportes_perdida',
                headers=HEADERS,
                json=reporte_data
            )
            
            if reporte_response.status_code in [200, 201]:
                flash('Reporte de mascota perdida creado exitosamente', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error al crear reporte', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # GET - Mostrar formulario
    ciudades = obtener_ciudades()
    return render_template('crear_relacional.html', ciudades=ciudades)

@app.route('/ver/<int:id>')
def ver(id):
    """Ver detalles completos de un reporte"""
    reporte = obtener_reporte_completo(id)
    
    if reporte:
        return render_template('ver_relacional.html', reporte=reporte)
    else:
        flash('Reporte no encontrado', 'error')
        return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar un reporte existente"""
    if request.method == 'POST':
        try:
            reporte = obtener_reporte_completo(id)
            if not reporte:
                flash('Reporte no encontrado', 'error')
                return redirect(url_for('index'))
            
            # Actualizar propietario
            propietario_data = {
                'nombre': request.form['nombre_propietario'],
                'apellido': request.form['apellido_propietario'],
                'email': request.form.get('email', ''),
                'telefono': request.form['telefono_propietario'],
                'direccion': request.form.get('direccion', ''),
                'ciudad_id': int(request.form['ciudad_propietario'])
            }
            
            requests.patch(
                f'{SUPABASE_URL}/rest/v1/propietarios?id=eq.{reporte["propietario"]["id"]}',
                headers=HEADERS,
                json=propietario_data
            )
            
            # Actualizar mascota
            mascota_data = {
                'nombre': request.form['nombre_mascota'],
                'tipo': request.form['tipo'],
                'raza': request.form.get('raza', ''),
                'color': request.form['color'],
                'edad': int(request.form['edad']) if request.form.get('edad') else None,
                'descripcion': request.form.get('descripcion', '')
            }
            
            requests.patch(
                f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{reporte["mascota_id"]}',
                headers=HEADERS,
                json=mascota_data
            )
            
            # Actualizar reporte
            fecha_id = crear_o_obtener_fecha(request.form['fecha_perdida'])
            
            reporte_data = {
                'fecha_perdida_id': fecha_id,
                'ciudad_perdida_id': int(request.form['ciudad_perdida']),
                'ubicacion_detallada': request.form['ubicacion_detallada'],
                'estado': request.form.get('estado', 'Perdida')
            }
            
            requests.patch(
                f'{SUPABASE_URL}/rest/v1/reportes_perdida?id=eq.{id}',
                headers=HEADERS,
                json=reporte_data
            )
            
            flash('Reporte actualizado exitosamente', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # GET - Cargar datos
    reporte = obtener_reporte_completo(id)
    ciudades = obtener_ciudades()
    
    if reporte:
        return render_template('editar_relacional.html', reporte=reporte, ciudades=ciudades)
    else:
        flash('Reporte no encontrado', 'error')
        return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    """Eliminar un reporte (cascada elimina mascota)"""
    try:
        response = requests.delete(
            f'{SUPABASE_URL}/rest/v1/reportes_perdida?id=eq.{id}',
            headers=HEADERS
        )
        
        if response.status_code in [200, 204]:
            flash('Reporte eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el reporte', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))



if __name__ == '__main__':
    print("🚀 Aplicación con relaciones iniciada")
    print("📊 Base de datos: Supabase (API REST)")
    app.run(debug=True)