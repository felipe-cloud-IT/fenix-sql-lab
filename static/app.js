const editor = document.querySelector('#sqlEditor');
const runButton = document.querySelector('#runButton');
const hintButton = document.querySelector('#hintButton');
const feedback = document.querySelector('#feedback');
const resultTable = document.querySelector('#resultTable');
const sourceTable = document.querySelector('#sourceTable');
const schemaBox = document.querySelector('#schema');
const emptyResult = document.querySelector('#emptyResult');
const metrics = document.querySelector('#metrics');

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

async function loadSchema() {
  const response = await fetch('api/schema');
  const data = await response.json();
  schemaBox.replaceChildren();
  data.columns.forEach(column => {
    const chip = document.createElement('span');
    chip.innerHTML = `<b>${column.name}</b> · ${column.type}`;
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
    const response = await fetch('api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({sql: editor.value})
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
      localStorage.setItem('fenixSqlLesson1', 'completed');
      document.querySelector('#progressBar').style.width = '10%';
      document.querySelector('#progressText').textContent = '10%';
    }
  } catch (error) {
    showFeedback('error', 'No se pudo conectar con el laboratorio.');
  } finally {
    runButton.disabled = false;
    runButton.textContent = 'Ejecutar consulta';
  }
});

hintButton.addEventListener('click', () => {
  showFeedback('hint', "Pista: comienza con SELECT nombre, estado FROM equipos y agrega una condición WHERE sobre la columna estado.");
});
document.querySelector('#refreshSchema').addEventListener('click', loadSchema);

if (localStorage.getItem('fenixSqlLesson1') === 'completed') {
  document.querySelector('#progressBar').style.width = '10%';
  document.querySelector('#progressText').textContent = '10%';
}
loadSchema();
