import sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parent / 'qualisofitedu.db'

sql_create = """
CREATE TABLE IF NOT EXISTS aplicativos (
  id_aplicativo INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT,
  descripcion TEXT,
  autor TEXT,
  link_publico TEXT,
  fecha_creacion TEXT
);
CREATE TABLE IF NOT EXISTS recursos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT,
  descripcion TEXT,
  enlace TEXT,
  tipo TEXT
);
CREATE TABLE IF NOT EXISTS evaluaciones (
  id_evaluacion INTEGER PRIMARY KEY AUTOINCREMENT,
  id_aplicativo INTEGER,
  funcionalidad REAL,
  fiabilidad REAL,
  usabilidad REAL,
  eficiencia REAL,
  mantenibilidad REAL,
  portabilidad REAL,
  total_percent REAL,
  score_0_5 REAL,
  evaluador TEXT,
  fecha_eval TEXT,
  comentarios TEXT,
  FOREIGN KEY(id_aplicativo) REFERENCES aplicativos(id_aplicativo)
);
"""

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.executescript(sql_create)

# sample aplicativos
cur.execute('INSERT INTO aplicativos (nombre, descripcion, autor, link_publico, fecha_creacion) VALUES (?,?,?,?,?)',
            ("PortalCursos","Portal de cursos para práctica académica: módulos, evaluaciones y seguimiento.","Autor Ejemplo","https://demo-portal/","2025-01-01T00:00:00"))
cur.execute('INSERT INTO aplicativos (nombre, descripcion, autor, link_publico, fecha_creacion) VALUES (?,?,?,?,?)',
            ("GestorTareas","Aplicación para gestión de tareas y actividades académicas.","Autor Ejemplo","https://gestortareas/","2025-01-01T00:00:00"))

recursos = [
    ("ISO/IEC 25010","Modelo de calidad del producto de software: funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad.","https://www.iso.org","norma"),
    ("ISO/IEC 12207","Procesos del ciclo de vida del software: desarrollo, operación y mantenimiento.","https://www.iso.org","norma"),
    ("IEEE 829","Estructura para documentación de pruebas y reporte de resultados.","https://ieee.org","estandar")
]
for r in recursos:
    cur.execute('INSERT INTO recursos (titulo, descripcion, enlace, tipo) VALUES (?, ?, ?, ?)', r)

# sample evaluations (0-5)
cur.execute('INSERT INTO evaluaciones (id_aplicativo, funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad, total_percent, score_0_5, evaluador, fecha_eval, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (1,4.5,4.0,4.2,3.8,4.0,4.1, round(((4.5+4.0+4.2+3.8+4.0+4.1)/6)/5*100,2), round((4.5+4.0+4.2+3.8+4.0+4.1)/6,2), 'Profesor Ejemplo', datetime.now().isoformat(), 'Evaluación de ejemplo 1'))
cur.execute('INSERT INTO evaluaciones (id_aplicativo, funcionalidad, fiabilidad, usabilidad, eficiencia, mantenibilidad, portabilidad, total_percent, score_0_5, evaluador, fecha_eval, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (2,3.5,3.8,3.6,3.2,3.4,3.5, round(((3.5+3.8+3.6+3.2+3.4+3.5)/6)/5*100,2), round((3.5+3.8+3.6+3.2+3.4+3.5)/6,2), 'Estudiante Ejemplo', datetime.now().isoformat(), 'Evaluación de ejemplo 2'))

conn.commit()
conn.close()
print("DB creada:", DB)
