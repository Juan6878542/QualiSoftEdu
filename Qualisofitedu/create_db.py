import sqlite3
from pathlib import Path
from datetime import datetime
DB = Path(__file__).resolve().parent / 'qualisofitedu.db'
sql_create = """CREATE TABLE IF NOT EXISTS aplicativos (
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
  normas REAL,
  modelos REAL,
  estandares REAL,
  codigo REAL,
  pruebas REAL,
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
# sample data
cur.execute('INSERT INTO aplicativos (nombre, descripcion, autor, link_publico, fecha_creacion) VALUES (?,?,?,?,?)',
            ("PortalCursos","Mini portal de cursos demo","Juan Mora","https://demo-portal/", datetime.now().isoformat()))
cur.execute('INSERT INTO aplicativos (nombre, descripcion, autor, link_publico, fecha_creacion) VALUES (?,?,?,?,?)',
            ("GestorTareas","App para gestión de tareas académicas","Maria Perez","https://gestortareas/", datetime.now().isoformat()))
recursos = [
    ("ISO/IEC 25010","Modelo de calidad del producto de software.","https://www.iso.org", "norma"),
    ("ISO/IEC 12207","Procesos del ciclo de vida del software.","https://www.iso.org","norma"),
    ("IEEE 829","Estructura para documentación de pruebas.","https://ieee.org","estandar")
]
for r in recursos:
    cur.execute('INSERT INTO recursos (titulo, descripcion, enlace, tipo) VALUES (?, ?, ?, ?)', r)
cur.execute('INSERT INTO evaluaciones (id_aplicativo, normas, modelos, estandares, codigo, pruebas, total_percent, score_0_5, evaluador, fecha_eval, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (1,90,85,80,70,75,77.75,3.89,'Profesor A', datetime.now().isoformat(), 'Caso ejemplo A'))
cur.execute('INSERT INTO evaluaciones (id_aplicativo, normas, modelos, estandares, codigo, pruebas, total_percent, score_0_5, evaluador, fecha_eval, comentarios) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (1,60,65,55,50,45,53.75,2.69,'Estudiante B', datetime.now().isoformat(), 'Caso ejemplo B'))
conn.commit()
conn.close()
print("DB creada:", DB)
