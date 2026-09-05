# Fénix SQL Lab

Laboratorio web en español para aprender SQL mediante práctica progresiva y escenarios de soporte TI.

## Versión de desarrollo 0.3.0

- 150 ejercicios distribuidos en 10 módulos.
- Cinco tablas relacionadas: departamentos, usuarios, equipos, incidentes y mantenimientos.
- Evaluación automática por resultado, columnas, filas, orden y cláusulas requeridas.
- Tres pistas graduales por ejercicio.
- Modos ruta, práctica aleatoria y refuerzo de errores.
- Progreso almacenado localmente en el navegador.
- Interfaz adaptable a escritorio y celular.

## Ruta de aprendizaje

1. `SELECT` y `FROM`
2. Filtros con `WHERE`
3. `ORDER BY` y `LIMIT`
4. Condiciones combinadas
5. Texto y valores `NULL`
6. Funciones agregadas
7. `GROUP BY` y `HAVING`
8. Relaciones y `JOIN`
9. Subconsultas
10. CTE y funciones de ventana

## Seguridad

- Solo acepta consultas que comiencen con `SELECT` o `WITH`.
- Utiliza una conexión SQLite en modo de solo lectura.
- El autorizador bloquea operaciones de escritura y cambios de esquema.
- Permite una sola consulta por ejecución.
- Limita tiempo de ejecución y cantidad de filas.
- Las soluciones de referencia permanecen en el servidor.
- Bases de datos, entornos virtuales y credenciales están excluidos de Git.

## Ejecución de desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
gunicorn --workers 1 --threads 2 --bind 127.0.0.1:5038 app:app
```

La rama `main` contiene la versión estable. El desarrollo de la ruta completa se realiza en `feature/150-exercises`.
