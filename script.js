const STORAGE_KEY = 'azure-github-task-manager-v1';
const form = document.querySelector('#task-form');
const input = document.querySelector('#task-input');
const list = document.querySelector('#task-list');
const remaining = document.querySelector('#remaining');
const emptyState = document.querySelector('#empty-state');
const clearCompleted = document.querySelector('#clear-completed');
let tasks = [];
try {
  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  if (Array.isArray(saved)) tasks = saved.filter(task => task && typeof task.text === 'string' && typeof task.id === 'string');
} catch (_) { tasks = []; }
function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks)); }
  catch (_) { /* App still works if local storage is unavailable. */ }
}
function render() {
  list.replaceChildren();
  for (const task of tasks) {
    const item = document.createElement('li');
    if (task.done) item.classList.add('done');
    const label = document.createElement('label');
    const check = document.createElement('input');
    check.type = 'checkbox';
    check.checked = !!task.done;
    check.addEventListener('change', () => { task.done = check.checked; save(); render(); });
    const text = document.createElement('span');
    text.textContent = task.text;
    label.append(check, text);
    const del = document.createElement('button');
    del.type = 'button';
    del.className = 'delete';
    del.textContent = 'Delete';
    del.setAttribute('aria-label', `Delete ${task.text}`);
    del.addEventListener('click', () => { tasks = tasks.filter(t => t.id !== task.id); save(); render(); });
    item.append(label, del);
    list.append(item);
  }
  const count = tasks.filter(task => !task.done).length;
  remaining.textContent = `${count} task${count === 1 ? '' : 's'} remaining`;
  emptyState.classList.toggle('hidden', tasks.length > 0);
  clearCompleted.disabled = !tasks.some(task => task.done);
}
form.addEventListener('submit', event => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  tasks.push({ id: crypto.randomUUID(), text, done: false });
  input.value = '';
  save(); render(); input.focus();
});
clearCompleted.addEventListener('click', () => { tasks = tasks.filter(task => !task.done); save(); render(); });
render();

// Test-record CRUD uses the Flask Python API; never insert user text as HTML.
const recordForm = document.querySelector('#record-form');
const recordRows = document.querySelector('#record-rows');
const recordStatus = document.querySelector('#record-status');
async function api(path, options = {}) {
  const response = await fetch(path, options);
  let data;
  try { data = await response.json(); } catch { throw Error('Invalid server response'); }
  if (!response.ok) throw Error(data.error || 'Server error');
  return data;
}
async function loadRecords() {
  try {
    const data = await api('/api/records');
    recordRows.replaceChildren();
    for (const record of data) {
      const tr = document.createElement('tr');
      for (const key of ['id', 'name', 'email', 'notes']) {
        const td = document.createElement('td');
        td.textContent = String(record[key] ?? '');
        tr.append(td);
      }
      const action = document.createElement('td');
      const del = document.createElement('button');
      del.textContent = 'Delete';
      del.type = 'button';
      del.addEventListener('click', async () => {
        try {
          await api(`/api/records/${record.id}`, { method: 'DELETE' });
          recordStatus.textContent = 'Record deleted.';
          await loadRecords();
        } catch (err) { recordStatus.textContent = err.message; }
      });
      action.append(del);
      tr.append(action);
      recordRows.append(tr);
    }
  } catch (err) { recordStatus.textContent = `Unable to load records: ${err.message}`; }
}
recordForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    name: document.querySelector('#record-name').value.trim(),
    email: document.querySelector('#record-email').value.trim(),
    notes: document.querySelector('#record-notes').value.trim(),
  };
  try {
    await api('/api/records', {method:'POST', headers: {'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    recordForm.reset();
    recordStatus.textContent = 'Record added successfully.';
    await loadRecords();
  } catch (err) { recordStatus.textContent = err.message; }
});
loadRecords();
