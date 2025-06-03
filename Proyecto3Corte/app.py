from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import os
import calendar

app = Flask(__name__)

carpeta_datos = r'C:\Users\Ajmg0\OneDrive\Documentos\Universidad\Estructura de datos\Proyecto3Corte\datos'
if not os.path.exists(carpeta_datos):
    os.makedirs(carpeta_datos)

DATA_FILE = r'C:\Users\Ajmg0\OneDrive\Documentos\Universidad\Estructura de datos\Proyecto3Corte\datos\tareas.json'
    
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as file:
        tareas = json.load(file)
else:
    tareas = {}
    
@app.route('/')
def index():
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))

    cal = calendar.monthcalendar(year, month)
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    month_name = meses_es[month - 1]

    tareas_mes = {}
    for fecha, lista in tareas.items():
        f = datetime.strptime(fecha, '%Y-%m-%d')
        if f.year == year and f.month == month:
            dia = f.day
            tareas_mes[dia] = {
                'tareas': lista,
                'completadas': sum(1 for t in lista if t.get('completada')),
                'pendientes': sum(1 for t in lista if not t.get('completada'))
            }
    hoy = datetime.now()
    dia_actual = hoy.day if hoy.month == month and hoy.year == year else None

    return render_template('index.html', cal=cal, year=year, month=month, month_name=month_name, tareas_mes=tareas_mes, dia_actual=dia_actual)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    fecha_predefinida = request.args.get('fecha_predefinida', '')

    if request.method == 'POST':
        fecha = request.form['fecha']
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']

        if fecha not in tareas:
            tareas[fecha] = []

        if titulo.strip():
            tareas[fecha].append({
                'titulo': titulo,
                'descripcion': descripcion,
                'completada': False
            })

            with open(DATA_FILE, 'w') as file:
                json.dump(tareas, file, indent=4)

        return redirect(url_for('index'))

    return render_template('agregar.html', fecha_predefinida=fecha_predefinida)

@app.route('/ver/<fecha>')
def ver(fecha):
    tareas_dia = tareas.get(fecha, [])
    total = len(tareas_dia)
    completadas = sum(1 for t in tareas_dia if t.get('completada'))
    pendientes = total - completadas

    return render_template('ver_tareas.html', fecha=fecha, tareas=tareas_dia, total=total, completadas=completadas, pendientes=pendientes)

@app.route('/eliminar/<fecha>/<int:indice>', methods=['POST'])
def eliminar(fecha, indice):
    if fecha in tareas and 0 <= indice < len(tareas[fecha]):
        tareas[fecha].pop(indice)
        if not tareas[fecha]:
            del tareas[fecha]
        with open(DATA_FILE, 'w') as file:
            json.dump(tareas, file, indent=4)
    return redirect(url_for('ver', fecha=fecha))

@app.route('/completar/<fecha>/<int:indice>', methods=['POST'])
def completar(fecha, indice):
    if fecha in tareas and 0 <= indice < len(tareas[fecha]):
        tareas[fecha][indice]['completada'] = True
        with open(DATA_FILE, 'w') as file:
            json.dump(tareas, file, indent=4)
    return redirect(url_for('ver', fecha=fecha))

@app.route('/buscar')
def buscar():
    consulta = request.args.get('q', '').strip().lower()
    resultados = []

    if consulta:
        for fecha, lista in tareas.items():
            for i, tarea in enumerate(lista):
                if consulta in tarea['titulo'].lower():
                    resultados.append({
                        'fecha': fecha,
                        'indice': i,    
                        'titulo': tarea['titulo'],
                        'descripcion': tarea['descripcion'],
                        'completada': tarea.get('completada', False)
                    })

    return render_template('buscar.html', consulta=consulta, resultados=resultados)

@app.route('/todas')
def todas():
    tareas_ordenadas = sorted(tareas.items())
    return render_template('todas.html', tareas_ordenadas=tareas_ordenadas)

if __name__ == '__main__':  
    app.run(debug=True)