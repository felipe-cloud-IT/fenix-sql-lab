const editor = document.querySelector('#sqlEditor');
const runButton = document.querySelector('#runButton');
const hintButton = document.querySelector('#hintButton');
const feedback = document.querySelector('#feedback');
const resultTable = document.querySelector('#resultTable');
const sourceTable = document.querySelector('#sourceTable');
const schemaBox = document.querySelector('#schema');
const emptyResult = document.querySelector('#emptyResult');
const metrics = document.querySelector('#metrics');

const lessons = {
  1: {
    title: 'Consultar equipos fuera de servicio',
    description: 'Usaremos SELECT para elegir columnas, FROM para indicar la tabla y WHERE para filtrar filas.',
    concepts: [['SELECT', 'Qué columnas mostrar'], ['FROM', 'En qué tabla buscar'], ['WHERE', 'Qué condición cumplir']],
    challenge: 'Muestra solamente nombre y estado de los equipos cuyo estado sea Fuera de servicio.',
    starter: "SELECT nombre, estado\nFROM equipos\nWHERE estado = 'Operativo';",
    hint: 'Pista: selecciona nombre y estado desde equipos y aplica WHERE sobre estado con el texto exacto Fuera de servicio.'
  },
  2: {
    title: 'Ordenar equipos por nombre',
    description: 'ORDER BY organiza las filas devueltas. ASC ordena de A a Z y es el valor predeterminado; DESC invierte el orden.',
    concepts: [['SELECT', 'Qué columnas mostrar'], ['FROM', 'En qué tabla buscar'], ['ORDER BY', 'Cómo ordenar las filas']],
    challenge: 'Muestra nombre, tipo y estado de todos los equipos, ordenados alfabéticamente por nombre.',
    starter: 'SELECT nombre, tipo, estado\nFROM equipos;',
    hint: 'Pista: después de FROM equipos agrega ORDER BY nombre. Puedes escribir ASC de forma explícita.'
  }
};

let currentLesson = localStorage.getItem('fenixSqlLesson1') === 'completed' ? 2 : 1;

function renderTable(table, columns, rows) {
  table.replaceChildren();
  if (!columns.length) return;
  const head = table.createTHead().insertRow();
  columns.forEach(column => {
    const th = document.createElement('th');
    th.textContent = column;
    head.appendChild(th);
  });
  const body = table.createTBody();
  rows.forEach(row => {
    const tr = body.insertRow();
    columns.forEach((_, index) => {
      const td = tr.insertCell();
      td.textContent = row[index] ?? 'NULL';
    });
  });
}

function showFeedback(type, message) {
  feedback.className = `feedback ${type}`;
  feedback.textContent = message;
}

function updateProgress() {
  const completed = [1, 2].filter(id => localStorage.getItem(`fenixSqlLesson${id}`) === 'completed').length;
  const percent = completed * 10;
  document.querySelector('#progressBar').style.width = `${percent}%`;
  document.querySelector('#progressText').textContent = `${percent}%`;
  document.querySelectorAll('.lesson[data-lesson]').forEach(button => {
    const id = Number(button.dataset.lesson);
    const status = button.querySelector('small');
    status.textContent = localStorage.getItem(`fenixSqlLesson${id}`) === 'completed' ? 'Completada' : (id === currentLesson ? 'En curso' : 'Disponible');
  });
}

function selectLesson(id) {
  currentLesson = id;
  const lesson = lessons[id];
  document.querySelector('#lessonTag').textContent = `LECCIÓN ${id}`;
  document.querySelector('#lessonTitle').textContent = lesson.title;
  document.querySelector('#lessonDescription').textContent = lesson.description;
  document.querySelector('#challengeText').textContent = lesson.challenge;
  const grid = document.querySelector('#conceptGrid');
  grid.replaceChildren();
  lesson.concepts.forEach(([keyword, meaning]) => {
    const item = document.createElement('div');
    const code = document.createElement('code');
    const span = document.createElement('span');
    code.textContent = keyword;
    span.textContent = meaning;
    item.append(code, span);
    grid.appendChild(item);
  });
  editor.value = lesson.starter;
  feedback.className = 'feedback hidden';
  resultTable.replaceChildren();
  emptyResult.classList.remove('hidden');
  metrics.textContent = 'Sin ejecutar';
  document.querySelectorAll('.lesson[data-lesson]').forEach(button => button.classList.toggle('active', Number(button.dataset.lesson) === id));
  updateProgress();
}

async function loadSchema() {
  const response = await fetch('/api/schema');
  const data = await response.json();
  document.querySelector('#tableName').textContent = data.table;
  schemaBox.replaceChildren();
  data.columns.forEach(column => {
    const chip = document.createElement('span');
    const name = document.createElement('b');
    name.textContent = column.name;
    chip.append(name, ` · ${column.type}`);
    schemaBox.appendChild(chip);
  });
  const columns = data.columns.map(column => column.name);
  const rows = data.rows.map(row => columns.map(column => row[column]));
  renderTable(sourceTable, columns, rows);
}

runButton.addEventListener('click', async () => {
  runButton.disabled = true;
  runButton.textContent = 'Ejecutando…';
  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({sql: editor.value, lesson_id: currentLesson})
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      resultTable.replaceChildren();
      emptyResult.classList.remove('hidden');
      metrics.textContent = 'Consulta con error';
      showFeedback('error', data.error || 'No fue posible ejecutar la consulta.');
      return;
    }
    emptyResult.classList.add('hidden');
    renderTable(resultTable, data.columns, data.rows);
    metrics.textContent = `${data.row_count} fila(s) · ${data.elapsed_ms} ms${data.truncated ? ' · resultado limitado' : ''}`;
    showFeedback(data.evaluation.passed ? 'ok' : 'hint', data.evaluation.message);
    if (data.evaluation.passed) {
      localStorage.setItem(`fenixSqlLesson${currentLesson}`, 'completed');
      updateProgress();
    }
  } catch (error) {
    showFeedback('error', 'No se pudo conectar con el laboratorio.');
  } finally {
    runButton.disabled = false;
    runButton.textContent = 'Ejecutar consulta';
  }
});

hintButton.addEventListener('click', () => showFeedback('hint', lessons[currentLesson].hint));
document.querySelector('#refreshSchema').addEventListener('click', loadSchema);
document.querySelectorAll('.lesson[data-lesson]').forEach(button => button.addEventListener('click', () => selectLesson(Number(button.dataset.lesson))));

selectLesson(currentLesson);
loadSchema();
