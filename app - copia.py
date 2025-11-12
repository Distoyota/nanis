# app.py - Versión con Supabase REST API
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_mascotas_2024'

# Configuración de Supabase API
# Obtén estos datos de: Settings > API
SUPABASE_URL = 'https://rexjcxtxbxjgdbblslfu.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJleGpjeHR4YnhqZ2RiYmxzbGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MjExODYsImV4cCI6MjA3ODM5NzE4Nn0.GfERK-lud6Kef9jDKouA7b5ICwHI8EFvXthFddiIXug'  # Copia el "anon public" key

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Ruta principal - Mostrar todas las mascotas
@app.route('/')
def index():
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/mascotas?order=fecha_perdida.desc',
            headers=HEADERS
        )
        
        if response.status_code == 200:
            mascotas = response.json()
            return render_template('index.html', mascotas=mascotas)
        else:
            flash(f'Error al cargar mascotas: {response.status_code}', 'error')
            return render_template('index.html', mascotas=[])
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'error')
        return render_template('index.html', mascotas=[])

# Crear nueva mascota
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        mascota_data = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'raza': request.form.get('raza', ''),
            'color': request.form['color'],
            'edad': int(request.form['edad']) if request.form.get('edad') else None,
            'fecha_perdida': request.form['fecha_perdida'],
            'ubicacion': request.form['ubicacion'],
            'descripcion': request.form.get('descripcion', ''),
            'contacto': request.form['contacto'],
            'telefono': request.form['telefono']
        }
        
        try:
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/mascotas',
                headers=HEADERS,
                json=mascota_data
            )
            
            if response.status_code in [200, 201]:
                flash('Mascota registrada exitosamente', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Error al registrar: {response.text}', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')
    
    return render_template('crear.html')

# Leer/Ver detalles de una mascota
@app.route('/ver/<int:id>')
def ver(id):
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{id}',
            headers=HEADERS
        )
        
        if response.status_code == 200:
            mascotas = response.json()
            if mascotas:
                return render_template('ver.html', mascota=mascotas[0])
            else:
                flash('Mascota no encontrada', 'error')
                return redirect(url_for('index'))
        else:
            flash('Error al cargar mascota', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'error')
        return redirect(url_for('index'))

# Actualizar mascota
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        mascota_data = {
            'nombre': request.form['nombre'],
            'tipo': request.form['tipo'],
            'raza': request.form.get('raza', ''),
            'color': request.form['color'],
            'edad': int(request.form['edad']) if request.form.get('edad') else None,
            'fecha_perdida': request.form['fecha_perdida'],
            'ubicacion': request.form['ubicacion'],
            'descripcion': request.form.get('descripcion', ''),
            'contacto': request.form['contacto'],
            'telefono': request.form['telefono']
        }
        
        try:
            response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{id}',
                headers=HEADERS,
                json=mascota_data
            )
            
            if response.status_code == 200:
                flash('Mascota actualizada exitosamente', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Error al actualizar: {response.text}', 'error')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'error')
    
    # GET - Cargar datos para editar
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{id}',
            headers=HEADERS
        )
        
        if response.status_code == 200:
            mascotas = response.json()
            if mascotas:
                return render_template('editar.html', mascota=mascotas[0])
            else:
                flash('Mascota no encontrada', 'error')
                return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'error')
        return redirect(url_for('index'))

# Eliminar mascota
@app.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        response = requests.delete(
            f'{SUPABASE_URL}/rest/v1/mascotas?id=eq.{id}',
            headers=HEADERS
        )
        
        if response.status_code in [200, 204]:
            flash('Mascota eliminada exitosamente', 'success')
        else:
            flash('Error al eliminar la mascota', 'error')
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 Aplicación iniciada en http://127.0.0.1:5000")
    print("⚠️  Asegúrate de configurar SUPABASE_URL y SUPABASE_KEY")
    app.run(debug=True)