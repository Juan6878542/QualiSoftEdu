from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
from pathlib import Path
from datetime import datetime
import csv, io, os

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'qualisofitedu.db'

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET','cambia_esta_clave')

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/normas')
def normas():
    return render_template('normas.html')

@app.route('/modelos')
def modelos():
    return render_template('modelos.html')

@app.route('/estandares')
def estandares():
    return render_template('estandares.html')

@app.route('/codigo')
def codigo():
    return render_template('codigo.html')

@app.route('/pruebas')
def pruebas():
    return render_template('pruebas.html')

@app.route('/conclusiones')
def conclusiones():
    return render_template('conclusiones.html')

@app.route('/recomendaciones')
def recomendaciones():
    return render_template('recomendaciones.html')

@app.route('/recursos')
def recursos():
    conn = get_db_conn()
    rows = conn.execute('SELECT * FROM recursos ORDER BY tipo, titulo').fetchall()
    conn.close()
    return render_template('recursos.html', recursos=rows)

# Aplicativos CRUD
@app.route('/aplicativos')
def aplicativos():
    conn = get_db_conn()
    rows = conn.execute('SELECT * FROM aplicativos ORDER BY fecha_creacion DESC').fetchall()
    conn.close()
    return render_template('aplicativos.html', aplicativos=rows)

@app.route('/aplicativos/new', methods=('GET','POST'))
def aplicativo_create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion','')
        autor = request.form.get('autor','')
        link_publico = request.form.get('link_publico','')
        conn = get_db_conn()
        conn.execute('INSERT INTO aplicativos (nombre, descripcion, autor, link_publico, fecha_creacion) VALUES (?, ?, ?, ?, ?)',
                     (nombre, descripcion, autor, link_publico, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        flash('Aplicativo creado.', 'message')
        return redirect(url_for('aplicativos'))
    return render_template('aplicativo_form.html', aplicativo=None)

@app.route('/aplicativos/<int:id>/edit', methods=('GET','POST'))
def aplicativo_edit(id):
    conn = get_db_conn()
    app_row = conn.execute('SELECT * FROM aplicativos WHERE id_aplicativo = ?', (id,)).fetchone()
    if not app_row:
        conn.close()
        flash('Aplicativo no existe.', 'error')
        return redirect(url_for('aplicativos'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion','')
        autor = request.form.get('autor','')
        link_publico = request.form.get('link_publico','')
        conn.execute('UPDATE aplicativos SET nombre=?, descripcion=?, autor=?, link_publico=? WHERE id_aplicativo=?',
                     (nombre, descripcion, autor, link_publico, id))
        conn.commit()
        conn.close()
        flash('Aplicativo actualizado.', 'message')
        return redirect(url_for('aplicativos'))
    conn.close()
    return render_template('aplicativo_form.html', aplicativo=app_row)

@app.route('/aplicativos/<int:id>/delete', methods=('POST',))
def aplicativo_delete(id):
    conn = get_db_conn()
    conn.execute('DELETE FROM aplicativos WHERE id_aplicativo = ?', (id,))
    conn.commit()
    conn.close()
    flash('Aplicativo eliminado.', 'message')
    return redirect(url_for('aplicativos'))

# Evaluador: escala 0-5 basada en ISO/IEC 25010 características
@app.route('/evaluar', methods=('GET','POST'))
def evaluar():
    conn = get_db_conn()
    apps = conn.execute('SELECT id_aplicativo, nombre FROM aplicativos ORDER BY nombre').fetchall()
    conn.close()
    if request.method == 'POST':
        try:
            id_app = int(request.form['id_aplicativo'])
            funcionalidad = float(request.form.get('funcionalidad', 0))
            fiabilidad = float(request.form.get('fiabilidad', 0))
            usabilidad = float(request.form.get('usabilidad', 0))
            eficiencia = float(request.form.get('eficiencia', 0))
            mantenibilidad = float(request.form.get('mantenibilidad', 0))
            portabilidad = float(request.form.get('portabilidad', 0))
        except Exception as e:
            flash('Valores inválidos: ' + str(e), 'error')
            return redirect(url_for('evaluar'))

        for v,name in [(funcionalidad,'funcionalidad'),(fiabilidad,'fiabilidad'),(usabilidad,'usabilidad'),
                       (eficiencia,'eficiencia'),(mantenibilidad,'mantenibilidad'),(portabilidad,'portabilidad')]:
            if v < 0 or v > 5:
                flash(f'El campo {name} debe estar entre 0 y 5.', 'error')
                return redirect(url_for('evaluar'))

        weights = {
            'funcionalidad': 0.20,
            'fiabilidad': 0.20,
            'usabilidad': 0.15,
            'eficiencia': 0.15,
            'mantenibilidad': 0.15,
            'portabilidad': 0.15
        }

        score_0_5 = round(
            funcionalidad*weights['funcionalidad'] +
            fiabilidad*weights['fiabilidad'] +
            usabilidad*weights['usabilidad'] +
            eficiencia*weights['eficiencia'] +
            mantenibilidad*weights['mantenibilidad'] +
            portabilidad*weights['portabilidad'], 2
        )

        total_percent = round((score_0_5 / 5.0) * 100, 2)

        evaluador = request.form.get('evaluador','Anónimo')
        comentarios = request.form.get('comentarios','')

        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO evaluaciones (id_aplicativo, funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad,
                                      total_percent, score_0_5, evaluador, fecha_eval, comentarios)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_app, funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad, total_percent, score_0_5, evaluador, datetime.now().isoformat(), comentarios))
        last_id = cur.lastrowid
        conn.commit()
        conn.close()
        flash(f'Evaluación registrada. Calificación: {score_0_5}/5', 'message')
        return redirect(url_for('resultado', eval_id=last_id))

    return render_template('evaluar.html', aplicativos=apps)

@app.route('/resultado/<int:eval_id>')
def resultado(eval_id):
    conn = get_db_conn()
    ev = conn.execute('SELECT e.*, a.nombre as aplicativo FROM evaluaciones e JOIN aplicativos a ON a.id_aplicativo=e.id_aplicativo WHERE id_evaluacion=?', (eval_id,)).fetchone()
    conn.close()
    if not ev:
        flash('Evaluación no encontrada.', 'error')
        return redirect(url_for('index'))
    sc = ev['score_0_5']
    if sc >= 4.5:
        label = 'Excelente'
    elif sc >= 3.5:
        label = 'Bueno'
    elif sc >= 2.5:
        label = 'Regular'
    elif sc >= 1.0:
        label = 'Deficiente'
    else:
        label = 'Muy deficiente'
    return render_template('resultado.html', ev=ev, label=label)

@app.route('/historico')
def historico():
    conn = get_db_conn()
    rows = conn.execute('SELECT e.*, a.nombre as aplicativo FROM evaluaciones e JOIN aplicativos a ON a.id_aplicativo=e.id_aplicativo ORDER BY fecha_eval DESC').fetchall()
    conn.close()
    return render_template('historico.html', rows=rows)

@app.route('/historico/export')
def historico_export():
    conn = get_db_conn()
    rows = conn.execute('SELECT e.id_evaluacion, a.nombre as aplicativo, e.funcionalidad, e.fiabilidad, e.usabilidad, e.eficiencia, e.mantenibilidad, e.portabilidad, e.total_percent, e.score_0_5, e.evaluador, e.fecha_eval FROM evaluaciones e JOIN aplicativos a ON a.id_aplicativo=e.id_aplicativo ORDER BY e.fecha_eval DESC').fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id','aplicativo','funcionalidad','fiabilidad','usabilidad','eficiencia','mantenibilidad','portabilidad','total_percent','score_0_5','evaluador','fecha_eval'])
    for r in rows:
        writer.writerow([r['id_evaluacion'], r['aplicativo'], r['funcionalidad'], r['fiabilidad'], r['usabilidad'], r['eficiencia'], r['mantenibilidad'], r['portabilidad'], r['total_percent'], r['score_0_5'], r['evaluador'], r['fecha_eval']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='historico_evaluaciones.csv')

@app.route('/anexos')
def anexos():
    return render_template('anexos.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
