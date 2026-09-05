from __future__ import annotations

import re
import sqlite3
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from catalog import CATALOG, MODULES, public_catalog

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB = DATA_DIR / "training.db"
MAX_ROWS = 100
app = Flask(__name__)

DEPARTAMENTOS = [(1,"Soporte TI"),(2,"Infraestructura"),(3,"Ventas"),(4,"Recursos Humanos"),(5,"Finanzas")]
USUARIOS = [
 (1,"Felipe","felipe@portalfenix.cl",None,1,1),(2,"Andrea","andrea@portalfenix.cl","991111111",4,1),
 (3,"Carlos","carlos@portalfenix.cl","992222222",3,1),(4,"Ana","ana@portalfenix.cl",None,2,1),
 (5,"Beatriz","beatriz@portalfenix.cl","993333333",5,1),(6,"Diego","diego@portalfenix.cl",None,1,0),
]
EQUIPOS = [
 (1,"PC-SOP-01","Notebook","Operativo","Soporte TI","Felipe",1,1),(2,"PC-RRHH-02","Escritorio","En mantenimiento","Recursos Humanos","Andrea",4,2),
 (3,"SW-CORE-01","Switch","Operativo","Infraestructura",None,2,None),(4,"NB-VTA-04","Notebook","Fuera de servicio","Ventas","Carlos",3,3),
 (5,"SRV-ARCH-01","Servidor","Operativo","Infraestructura",None,2,None),(6,"PC-FIN-01","Escritorio","Operativo","Finanzas","Beatriz",5,5),
 (7,"RT-EDGE-01","Router","Operativo","Infraestructura","Ana",2,4),(8,"NB-SOP-02","Notebook","Operativo","Soporte TI","Diego",1,6),
 (9,"PC-VTA-02","Escritorio","Retirado","Ventas",None,3,None),(10,"AP-WIFI-01","Access Point","Operativo","Infraestructura",None,2,None),
 (11,"NB-RRHH-03","Notebook","Operativo","Recursos Humanos","Andrea",4,2),(12,"SRV-DB-01","Servidor","En mantenimiento","Infraestructura","Ana",2,4),
 (13,"PC-SOP-03","Escritorio","Operativo","Soporte TI","Felipe",1,1),(14,"FW-CORE-01","Firewall","Operativo","Infraestructura",None,2,None),
 (15,"NB-FIN-02","Notebook","Fuera de servicio","Finanzas",None,5,None),(16,"PC-VTA-05","Escritorio","Operativo","Ventas","Carlos",3,3),
 (17,"SW-ACCESS-02","Switch","Operativo","Infraestructura",None,2,None),(18,"NB-SOP-05","Notebook","En mantenimiento","Soporte TI",None,1,None),
 (19,"SRV-WEB-02","Servidor","Operativo","Infraestructura","Ana",2,4),(20,"PC-FIN-06","Escritorio","Operativo","Finanzas","Beatriz",5,5),
]
INCIDENTES = [
 (1,4,"Equipo no inicia","Abierto",3,"2026-08-01",None),(2,3,"Pérdida intermitente de red","Cerrado",2,"2026-08-02","2026-08-03"),
 (3,12,"Base de datos sin respuesta","Abierto",4,"2026-08-05",None),(4,1,"Error de impresora de red","Cerrado",1,"2026-08-06","2026-08-06"),
 (5,15,"Pantalla azul","En progreso",3,"2026-08-08",None),(6,7,"Latencia de red","Cerrado",2,"2026-08-09","2026-08-10"),
 (7,3,"Puerto de red caído","Abierto",3,"2026-08-11",None),(8,18,"Batería degradada","En progreso",2,"2026-08-12",None),
 (9,5,"Espacio en disco bajo","Cerrado",2,"2026-08-13","2026-08-14"),(10,10,"Cobertura de red débil","Abierto",2,"2026-08-15",None),
]
MANTENIMIENTOS = [
 (1,1,"Preventivo","Fenix TI",45000,"2026-07-01"),(2,3,"Correctivo","Redes Sur",120000,"2026-07-03"),
 (3,4,"Correctivo","Fenix TI",85000,"2026-07-05"),(4,5,"Preventivo","Servidores Maule",150000,"2026-07-08"),
 (5,7,"Preventivo","Redes Sur",60000,"2026-07-10"),(6,12,"Correctivo","Servidores Maule",240000,"2026-07-12"),
 (7,15,"Correctivo","Fenix TI",95000,"2026-07-15"),(8,18,"Preventivo","Fenix TI",35000,"2026-07-18"),
 (9,3,"Preventivo","Redes Sur",70000,"2026-07-20"),(10,19,"Preventivo","Servidores Maule",130000,"2026-07-22"),
]

def initialize_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as c:
        version = c.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            c.executescript("""
            DROP TABLE IF EXISTS mantenimientos; DROP TABLE IF EXISTS incidentes;
            DROP TABLE IF EXISTS equipos; DROP TABLE IF EXISTS usuarios; DROP TABLE IF EXISTS departamentos;
            CREATE TABLE departamentos(id INTEGER PRIMARY KEY, nombre TEXT UNIQUE NOT NULL);
            CREATE TABLE usuarios(id INTEGER PRIMARY KEY,nombre TEXT NOT NULL,email TEXT,telefono TEXT,departamento_id INTEGER,activo INTEGER NOT NULL,FOREIGN KEY(departamento_id) REFERENCES departamentos(id));
            CREATE TABLE equipos(id INTEGER PRIMARY KEY,nombre TEXT UNIQUE NOT NULL,tipo TEXT NOT NULL,estado TEXT NOT NULL,departamento TEXT NOT NULL,usuario_asignado TEXT,departamento_id INTEGER,usuario_id INTEGER,FOREIGN KEY(departamento_id) REFERENCES departamentos(id),FOREIGN KEY(usuario_id) REFERENCES usuarios(id));
            CREATE TABLE incidentes(id INTEGER PRIMARY KEY,equipo_id INTEGER,descripcion TEXT,estado TEXT,prioridad INTEGER,fecha_apertura TEXT,fecha_cierre TEXT,FOREIGN KEY(equipo_id) REFERENCES equipos(id));
            CREATE TABLE mantenimientos(id INTEGER PRIMARY KEY,equipo_id INTEGER,tipo TEXT,proveedor TEXT,costo INTEGER,fecha TEXT,FOREIGN KEY(equipo_id) REFERENCES equipos(id));
            PRAGMA user_version=3;
            """)
            c.executemany("INSERT INTO departamentos VALUES (?,?)", DEPARTAMENTOS)
            c.executemany("INSERT INTO usuarios VALUES (?,?,?,?,?,?)", USUARIOS)
            c.executemany("INSERT INTO equipos VALUES (?,?,?,?,?,?,?,?)", EQUIPOS)
            c.executemany("INSERT INTO incidentes VALUES (?,?,?,?,?,?,?)", INCIDENTES)
            c.executemany("INSERT INTO mantenimientos VALUES (?,?,?,?,?,?)", MANTENIMIENTOS)

def safe(sql):
    q=sql.strip(); body=q[:-1].strip() if q.endswith(';') else q
    if not q: return False,"Escribe una consulta."
    if len(q)>3000: return False,"La consulta es demasiado extensa."
    if ';' in body: return False,"Ejecuta una sola consulta a la vez."
    if not re.match(r"^(SELECT|WITH)\b",body,re.I): return False,"Solo se permiten SELECT y WITH."
    return True,""

def authorizer(action,*_):
    return sqlite3.SQLITE_OK if action in {sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE} else sqlite3.SQLITE_DENY

def run_sql(sql):
    start=time.perf_counter(); c=sqlite3.connect(f"file:{DB}?mode=ro",uri=True); c.row_factory=sqlite3.Row
    c.set_authorizer(authorizer); c.set_progress_handler(lambda: 1 if time.perf_counter()-start>1 else 0,1000)
    try:
        cur=c.execute(sql); cols=[d[0] for d in cur.description or []]; rows=cur.fetchmany(MAX_ROWS+1)
        return cols, [[row[col] for col in cols] for row in rows[:MAX_ROWS]], len(rows)>MAX_ROWS
    finally: c.close()

def friendly_sql_error(exc):
    message = str(exc)
    near = re.search(r'near "([^"]+)": syntax error', message, re.I)
    if near:
        token = near.group(1)
        return f'Error de sintaxis cerca de "{token}". Revisa comas, palabras clave y el punto y coma final.'
    missing_column = re.search(r'no such column: (.+)', message, re.I)
    if missing_column:
        return f'La columna "{missing_column.group(1)}" no existe. Revisa las columnas de la tabla seleccionada.'
    missing_table = re.search(r'no such table: (.+)', message, re.I)
    if missing_table:
        return f'La tabla "{missing_table.group(1)}" no existe. Revisa las tablas disponibles.'
    ambiguous = re.search(r'ambiguous column name: (.+)', message, re.I)
    if ambiguous:
        return f'La columna "{ambiguous.group(1)}" existe en más de una tabla. Indica su alias, por ejemplo e.nombre.'
    if 'incomplete input' in message.lower():
        return 'La consulta está incompleta. Revisa si falta una columna, tabla, condición o paréntesis.'
    return f'La consulta no pudo ejecutarse: {message}'

@app.get('/')
def index(): return render_template('index.html')

@app.get('/health')
def health(): return jsonify(status='ok',service='fenix-sql-lab',version='0.3.0',exercises=len(CATALOG))

@app.get('/api/lessons')
def lessons(): return jsonify(modules=[{'id':i+1,'name':n} for i,n in enumerate(MODULES)],lessons=public_catalog(CATALOG),total=len(CATALOG))

@app.get('/api/schema')
def schema():
    with sqlite3.connect(DB) as c:
        result={}
        for table in ('equipos','usuarios','departamentos','incidentes','mantenimientos'):
            result[table]=[{'name':x[1],'type':x[2]} for x in c.execute(f'PRAGMA table_info({table})')]
    return jsonify(tables=result)

@app.get('/api/hint/<int:lesson_id>/<int:level>')
def hint(lesson_id,level):
    if not 1<=lesson_id<=len(CATALOG): return jsonify(error='Ejercicio inexistente'),404
    level=max(1,min(level,3)); return jsonify(hint=CATALOG[lesson_id-1].hints[level-1],level=level)

@app.post('/api/query')
def query():
    p=request.get_json(silent=True) or {}; sql=str(p.get('sql',''))
    try: lesson_id=int(p.get('lesson_id',0) or 0)
    except (TypeError,ValueError): lesson_id=0
    if not 1<=lesson_id<=len(CATALOG): return jsonify(ok=False,error='Ejercicio inexistente'),400
    ok,error=safe(sql)
    if not ok:return jsonify(ok=False,error=error),400
    lesson=CATALOG[lesson_id-1]
    try:
        cols,rows,truncated=run_sql(sql); ecols,erows,_=run_sql(lesson.solution_sql)
        missing=[term for term in lesson.required if term.upper() not in sql.upper()]
        passed=not missing and cols==ecols and rows==erows
        if missing: message=f"La consulta funciona, pero debes practicar: {', '.join(missing)}."
        elif cols!=ecols: message='Revisa los nombres y el orden de las columnas solicitadas.'
        elif rows!=erows: message='Las columnas son correctas; revisa filtros, orden o agrupación.'
        else: message=f'¡Correcto! Ejercicio {lesson_id} completado.'
        return jsonify(ok=True,columns=cols,rows=rows,row_count=len(rows),truncated=truncated,evaluation={'passed':passed,'message':message})
    except sqlite3.Error as exc:return jsonify(ok=False,error=friendly_sql_error(exc)),400

initialize_database()
if __name__=='__main__': app.run(host='127.0.0.1',port=5038,debug=False)
