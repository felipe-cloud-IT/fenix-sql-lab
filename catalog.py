from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Lesson:
    id: int
    module: int
    title: str
    challenge: str
    starter: str
    solution_sql: str
    required: tuple[str, ...]
    hints: tuple[str, str, str]


MODULES = [
    "SELECT y FROM", "Filtros con WHERE", "Orden y límites",
    "Condiciones combinadas", "Texto y valores NULL", "Funciones agregadas",
    "GROUP BY y HAVING", "Relaciones y JOIN", "Subconsultas",
    "CTE y funciones de ventana",
]


def build_catalog() -> list[Lesson]:
    lessons: list[Lesson] = []

    def add(module, title, challenge, starter, solution, required, hints):
        lessons.append(Lesson(len(lessons) + 1, module, title, challenge, starter,
                              solution, tuple(required), tuple(hints)))

    # Módulo 1: proyección de columnas y alias.
    selections = [
        ("nombre", "nombre"), ("nombre, tipo", "nombre y tipo"),
        ("nombre, estado", "nombre y estado"), ("id, nombre", "id y nombre"),
        ("tipo, estado", "tipo y estado"), ("nombre, departamento", "nombre y departamento"),
        ("nombre, usuario_asignado", "nombre y usuario asignado"),
        ("id, nombre, tipo", "id, nombre y tipo"),
        ("nombre, tipo, estado", "nombre, tipo y estado"),
        ("nombre, estado, departamento", "nombre, estado y departamento"),
        ("id, nombre, departamento", "id, nombre y departamento"),
        ("id, tipo, estado", "id, tipo y estado"),
        ("nombre AS equipo", "nombre con el alias equipo"),
        ("departamento AS area, nombre AS equipo", "departamento como area y nombre como equipo"),
        ("*", "todas las columnas"),
    ]
    for columns, wording in selections:
        add(1, f"Seleccionar {wording}", f"Muestra {wording} de la tabla equipos.",
            "SELECT\nFROM equipos;", f"SELECT {columns} FROM equipos;", ["SELECT", "FROM"],
            ("Identifica qué columnas pide el desafío.", "La tabla se llama equipos.", f"Completa SELECT con: {columns}."))

    # Módulo 2: comparaciones y filtros.
    filters = [
        ("estado = 'Operativo'", "estado Operativo"), ("estado = 'Fuera de servicio'", "estado Fuera de servicio"),
        ("tipo = 'Notebook'", "tipo Notebook"), ("tipo = 'Servidor'", "tipo Servidor"),
        ("departamento = 'Infraestructura'", "departamento Infraestructura"),
        ("departamento = 'Ventas'", "departamento Ventas"), ("id = 1", "id igual a 1"),
        ("id > 5", "id mayor que 5"), ("id >= 10", "id mayor o igual que 10"),
        ("id < 6", "id menor que 6"), ("id <= 3", "id menor o igual que 3"),
        ("estado <> 'Operativo'", "estado distinto de Operativo"),
        ("tipo <> 'Notebook'", "tipo distinto de Notebook"),
        ("departamento = 'Soporte TI'", "departamento Soporte TI"),
        ("usuario_asignado = 'Felipe'", "usuario asignado Felipe"),
    ]
    for clause, wording in filters:
        add(2, f"Filtrar por {wording}", f"Muestra id, nombre y estado de equipos con {wording}.",
            "SELECT id, nombre, estado\nFROM equipos;", f"SELECT id, nombre, estado FROM equipos WHERE {clause};", ["WHERE"],
            ("El filtro se escribe después de FROM.", "Usa WHERE y una comparación.", f"La condición necesaria es {clause}."))

    # Módulo 3: orden estable y límites.
    orders = [
        ("nombre ASC", "nombre de A a Z", ""), ("nombre DESC", "nombre de Z a A", ""),
        ("estado ASC, nombre ASC", "estado y luego nombre", ""),
        ("departamento ASC, nombre ASC", "departamento y luego nombre", ""),
        ("departamento DESC, nombre ASC", "departamento descendente y luego nombre", ""),
        ("tipo ASC, nombre ASC", "tipo y luego nombre", ""), ("id DESC", "id descendente", ""),
        ("id ASC", "id ascendente", "LIMIT 5"), ("nombre ASC", "nombre ascendente", "LIMIT 3"),
        ("estado ASC, id ASC", "estado y luego id", "LIMIT 8"),
        ("departamento ASC, id DESC", "departamento e id descendente", "LIMIT 10"),
        ("tipo DESC, nombre ASC", "tipo descendente y nombre", "LIMIT 7"),
        ("nombre ASC", "nombre ascendente", "LIMIT 1"), ("id DESC", "id descendente", "LIMIT 1"),
        ("estado DESC, nombre DESC", "estado y nombre descendentes", "LIMIT 6"),
    ]
    for order, wording, limit in orders:
        suffix = f" {limit}" if limit else ""
        req = ["ORDER BY"] + (["LIMIT"] if limit else [])
        add(3, f"Ordenar por {wording}", f"Muestra id, nombre, tipo y estado; ordena por {wording}{' y limita el resultado' if limit else ''}.",
            "SELECT id, nombre, tipo, estado\nFROM equipos;", f"SELECT id, nombre, tipo, estado FROM equipos ORDER BY {order}{suffix};", req,
            ("ORDER BY se escribe después de FROM y WHERE.", "Puedes ordenar por más de una columna usando comas.", f"El orden solicitado es {order}{suffix}."))

    # Los módulos 4 a 10 usan variantes profesionales definidas como desafío y SQL de referencia.
    advanced = {
      4: [
        ("AND", "Notebooks operativos", "tipo='Notebook' AND estado='Operativo'"),
        ("AND", "Equipos operativos de Infraestructura", "estado='Operativo' AND departamento='Infraestructura'"),
        ("OR", "Equipos de Ventas o Soporte TI", "departamento='Ventas' OR departamento='Soporte TI'"),
        ("IN", "Equipos de tres áreas", "departamento IN ('Ventas','Soporte TI','Infraestructura')"),
        ("NOT IN", "Excluir dos estados", "estado NOT IN ('Fuera de servicio','Retirado')"),
        ("BETWEEN", "Identificadores entre 3 y 10", "id BETWEEN 3 AND 10"),
        ("AND", "Servidores no retirados", "tipo='Servidor' AND estado<>'Retirado'"),
        ("OR", "Notebooks o escritorios", "tipo='Notebook' OR tipo='Escritorio'"),
        ("IN", "Equipos críticos", "tipo IN ('Servidor','Switch','Router')"),
        ("AND", "Rango excluyendo mantenimiento", "id>=5 AND estado<>'En mantenimiento'"),
        ("OR", "Dos estados de atención", "estado='Fuera de servicio' OR estado='En mantenimiento'"),
        ("AND", "Ventas con equipo operativo", "departamento='Ventas' AND estado='Operativo'"),
        ("NOT", "Equipos que no son notebooks", "NOT tipo='Notebook'"),
        ("BETWEEN", "Segundo rango de identificadores", "id BETWEEN 8 AND 15"),
        ("AND OR", "Condición empresarial combinada", "estado='Operativo' AND (tipo='Servidor' OR tipo='Switch')"),
      ],
      5: [
        ("LIKE", "Nombres que comienzan con PC-", "nombre LIKE 'PC-%'"), ("LIKE", "Nombres que comienzan con NB-", "nombre LIKE 'NB-%'"),
        ("LIKE", "Nombres que contienen CORE", "nombre LIKE '%CORE%'"), ("LIKE", "Áreas que contienen TI", "departamento LIKE '%TI%'"),
        ("IS NULL", "Equipos sin usuario", "usuario_asignado IS NULL"), ("IS NOT NULL", "Equipos con usuario", "usuario_asignado IS NOT NULL"),
        ("LIKE", "Usuarios que comienzan con A", "usuario_asignado LIKE 'A%'"), ("NOT LIKE", "Nombres que no comienzan con PC-", "nombre NOT LIKE 'PC-%'"),
        ("LIKE", "Nombres que terminan en 01", "nombre LIKE '%01'"), ("LIKE", "Tipos que contienen dor", "tipo LIKE '%dor%'"),
        ("IS NULL", "Incidentes sin cierre", "fecha_cierre IS NULL", "incidentes"), ("IS NOT NULL", "Incidentes cerrados", "fecha_cierre IS NOT NULL", "incidentes"),
        ("LIKE", "Incidentes de red", "descripcion LIKE '%red%'", "incidentes"), ("LIKE", "Correos corporativos", "email LIKE '%@portalfenix.cl'", "usuarios"),
        ("IS NULL", "Usuarios sin teléfono", "telefono IS NULL", "usuarios"),
      ],
    }
    for module, specs in advanced.items():
        for item in specs:
            keyword, title, condition, *table_arg = item; table = table_arg[0] if table_arg else "equipos"
            cols = "id, descripcion" if table == "incidentes" else ("id, nombre, email" if table == "usuarios" else "id, nombre, estado")
            add(module, title, f"Consulta {title.lower()}.", f"SELECT {cols}\nFROM {table};",
                f"SELECT {cols} FROM {table} WHERE {condition} ORDER BY id;", [keyword.split()[0], "WHERE"],
                ("Identifica el patrón o la ausencia buscada.", f"La condición se aplica con {keyword}.", f"Usa WHERE {condition}."))

    # Módulos 6-10: 75 consultas de análisis; se parametrizan para conservar consistencia.
    aggregate_specs = [
      ("COUNT(*)", "total_registros", "equipos"), ("COUNT(usuario_asignado)", "con_usuario", "equipos"),
      ("COUNT(DISTINCT departamento)", "total_areas", "equipos"), ("MIN(id)", "id_minimo", "equipos"),
      ("MAX(id)", "id_maximo", "equipos"), ("AVG(costo)", "costo_promedio", "mantenimientos"),
      ("SUM(costo)", "costo_total", "mantenimientos"), ("MIN(costo)", "costo_minimo", "mantenimientos"),
      ("MAX(costo)", "costo_maximo", "mantenimientos"), ("COUNT(*)", "total_incidentes", "incidentes"),
      ("COUNT(fecha_cierre)", "incidentes_cerrados", "incidentes"), ("AVG(prioridad)", "prioridad_promedio", "incidentes"),
      ("SUM(costo)", "costo_preventivo", "mantenimientos", "tipo='Preventivo'"),
      ("COUNT(*)", "equipos_operativos", "equipos", "estado='Operativo'"),
      ("COUNT(*)", "usuarios_activos", "usuarios", "activo=1"),
    ]
    for expr, alias, table, *where in aggregate_specs:
        condition = f" WHERE {where[0]}" if where else ""
        add(6, f"Calcular {alias}", f"Calcula {alias.replace('_',' ')} y usa exactamente ese alias.",
            f"SELECT\nFROM {table};", f"SELECT {expr} AS {alias} FROM {table}{condition};", [expr.split('(')[0], "AS"],
            ("Usa una función agregada.", f"La tabla es {table}.", f"La expresión comienza con {expr}."))

    group_specs = [
      ("equipos","estado","COUNT(*)","cantidad",""), ("equipos","tipo","COUNT(*)","cantidad",""),
      ("equipos","departamento","COUNT(*)","cantidad",""), ("incidentes","estado","COUNT(*)","cantidad",""),
      ("incidentes","prioridad","COUNT(*)","cantidad",""), ("mantenimientos","tipo","COUNT(*)","cantidad",""),
      ("mantenimientos","tipo","SUM(costo)","costo_total",""), ("mantenimientos","proveedor","AVG(costo)","promedio",""),
      ("usuarios","departamento_id","COUNT(*)","cantidad",""), ("equipos","estado","COUNT(*)","cantidad","HAVING COUNT(*) >= 2"),
      ("equipos","departamento","COUNT(*)","cantidad","HAVING COUNT(*) >= 2"), ("incidentes","equipo_id","COUNT(*)","cantidad","HAVING COUNT(*) > 1"),
      ("mantenimientos","equipo_id","SUM(costo)","total","HAVING SUM(costo) > 100000"),
      ("incidentes","estado","AVG(prioridad)","promedio","HAVING AVG(prioridad) >= 2"),
      ("equipos","tipo","COUNT(*)","cantidad","HAVING COUNT(*) BETWEEN 2 AND 5"),
    ]
    for table, group, expr, alias, having in group_specs:
        sql=f"SELECT {group}, {expr} AS {alias} FROM {table} GROUP BY {group} {having} ORDER BY {group};"
        req=["GROUP BY", expr.split('(')[0]] + (["HAVING"] if having else [])
        add(7, f"Agrupar por {group}", f"Agrupa {table} por {group} y calcula {alias}. {having}.",
            f"SELECT {group}\nFROM {table};", sql, req,
            ("Selecciona el campo agrupado y una función.", f"Agrupa mediante GROUP BY {group}.", "HAVING filtra grupos; WHERE filtra filas."))

    join_variants = [
      ("equipos e JOIN departamentos d ON e.departamento_id=d.id","e.nombre, d.nombre AS departamento"),
      ("equipos e LEFT JOIN usuarios u ON e.usuario_id=u.id","e.nombre, u.nombre AS usuario"),
      ("incidentes i JOIN equipos e ON i.equipo_id=e.id","i.id, e.nombre, i.estado"),
      ("mantenimientos m JOIN equipos e ON m.equipo_id=e.id","m.id, e.nombre, m.costo"),
      ("usuarios u JOIN departamentos d ON u.departamento_id=d.id","u.nombre, d.nombre AS departamento"),
    ]
    for cycle in range(3):
        for source, cols in join_variants:
            order = cols.split(',')[0]
            limit = ("", " LIMIT 5", " LIMIT 3")[cycle]
            add(8, f"Relacionar datos {len(lessons)+1}", f"Relaciona las tablas y muestra {cols}{'; limita a '+limit.split()[-1]+' filas' if limit else ''}.",
                f"SELECT {cols}\nFROM;", f"SELECT {cols} FROM {source} ORDER BY {order}{limit};", ["JOIN", "ON"] + (["LIMIT"] if limit else []),
                ("Busca las claves primaria y foránea.", "JOIN conecta las tablas y ON define la relación.", f"La relación parte desde {source}."))

    subqueries = [
      ("Equipos con incidentes", "SELECT nombre FROM equipos WHERE id IN (SELECT equipo_id FROM incidentes) ORDER BY nombre"),
      ("Equipos sin incidentes", "SELECT nombre FROM equipos WHERE id NOT IN (SELECT equipo_id FROM incidentes) ORDER BY nombre"),
      ("Costos sobre el promedio", "SELECT id, costo FROM mantenimientos WHERE costo > (SELECT AVG(costo) FROM mantenimientos) ORDER BY costo"),
      ("Incidentes de equipos operativos", "SELECT id, descripcion FROM incidentes WHERE equipo_id IN (SELECT id FROM equipos WHERE estado='Operativo') ORDER BY id"),
      ("Usuarios de Infraestructura", "SELECT nombre FROM usuarios WHERE departamento_id=(SELECT id FROM departamentos WHERE nombre='Infraestructura') ORDER BY nombre"),
    ]
    for cycle in range(3):
        for title, sql in subqueries:
            limit = ("", " LIMIT 5", " LIMIT 2")[cycle]
            add(9, f"{title} {cycle+1}", title + (f"; devuelve como máximo {limit.split()[-1]} filas." if limit else "."), "SELECT\nFROM;", sql + limit + ";", ["SELECT", "("] + (["LIMIT"] if limit else []),
                ("La consulta interior responde primero.", "Usa el resultado interior en WHERE.", "Identifica la tabla de la consulta principal y la secundaria."))

    windows = [
      ("CTE de equipos operativos", "WITH operativos AS (SELECT * FROM equipos WHERE estado='Operativo') SELECT id, nombre FROM operativos ORDER BY id", ["WITH"]),
      ("Numerar equipos", "SELECT nombre, ROW_NUMBER() OVER (ORDER BY nombre) AS numero FROM equipos ORDER BY nombre", ["OVER","ROW_NUMBER"]),
      ("Numerar por departamento", "SELECT nombre, departamento_id, ROW_NUMBER() OVER (PARTITION BY departamento_id ORDER BY nombre) AS numero FROM equipos ORDER BY departamento_id, numero", ["OVER","PARTITION BY"]),
      ("Costo acumulado", "SELECT id, costo, SUM(costo) OVER (ORDER BY id) AS acumulado FROM mantenimientos ORDER BY id", ["OVER","SUM"]),
      ("Promedio por tipo", "SELECT id, tipo, costo, AVG(costo) OVER (PARTITION BY tipo) AS promedio_tipo FROM mantenimientos ORDER BY id", ["OVER","AVG"]),
    ]
    for cycle in range(3):
        for title, sql, req in windows:
            limit = ("", " LIMIT 10", " LIMIT 5")[cycle]
            add(10, f"{title} {cycle+1}", title + (f"; limita a {limit.split()[-1]} filas." if limit else "."), "SELECT\nFROM;", sql + limit + ";", req + (["LIMIT"] if limit else []),
                ("Divide el problema en pasos.", "La solución conserva cada fila y añade contexto.", f"Practica {' y '.join(req)}."))

    validate_catalog(lessons)
    return lessons


def validate_catalog(lessons: list[Lesson]) -> None:
    assert len(lessons) == 150, f"Se esperaban 150 ejercicios y existen {len(lessons)}"
    assert [lesson.id for lesson in lessons] == list(range(1, 151))
    assert {lesson.module for lesson in lessons} == set(range(1, 11))
    assert all(lesson.solution_sql.strip() for lesson in lessons)
    assert len({lesson.solution_sql for lesson in lessons}) == 150
    assert all(len(lesson.hints) == 3 for lesson in lessons)


def public_catalog(lessons: list[Lesson]) -> list[dict]:
    hidden = {"solution_sql", "required", "hints"}
    return [{k: v for k, v in asdict(lesson).items() if k not in hidden} for lesson in lessons]


CATALOG = build_catalog()
