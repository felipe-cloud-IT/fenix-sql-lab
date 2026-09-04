# Fénix SQL Lab v0.1.0

Laboratorio local para aprender SQL con escenarios de soporte TI.

## Incluye

- Flask y SQLite.
- Base ficticia de equipos.
- Primera lección sobre `SELECT`, `FROM` y `WHERE`.
- Editor SQL real con acceso de solo lectura.
- Límite de una consulta, 100 filas y un segundo de ejecución.
- Evaluación por resultado y pistas progresivas.
- Progreso inicial en el navegador.

## Ejecución de prueba

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
gunicorn --workers 1 --threads 2 --bind 127.0.0.1:5037 app:app
```

## Consulta que aprueba la primera lección

```sql
SELECT nombre, estado
FROM equipos
WHERE estado = 'Fuera de servicio';
```

No contiene información real de empresas ni usuarios.
