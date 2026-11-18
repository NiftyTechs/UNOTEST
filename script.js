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
