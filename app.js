// Load & sort entries by newest first
async function loadQuotes() {
  const res = await fetch('quotes.json');
  const data = await res.json();
  return data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

// Render the Ticker Bar
function renderTicker(entries) {
  const ticker = document.getElementById('ticker');
  ticker.innerHTML = '';
  entries
    .filter(e => ['announcement','decree','quote_of_the_day'].includes(e.type))
    .slice(0, 10)
    .forEach(e => {
      const btn = document.createElement('button');
      btn.textContent = `${new Date(e.createdAt).toLocaleString('en-GB').replace(',', '')} – ${e.text}`;
      btn.onclick = () => alert(`${e.text}\n\n— ${e.role}`);
      ticker.appendChild(btn);
      ticker.append('  ');
    });
}

// Render the Archive List
function renderArchive(entries) {
  const archive = document.getElementById('archive');
  archive.innerHTML = '';
  entries.forEach(e => {
    const card = document.createElement('div');
    card.className = 'entry-card';

    if (e.imageUrl) {
      const img = document.createElement('img');
      img.src = e.imageUrl;
      card.appendChild(img);
    }

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = `${new Date(e.createdAt).toLocaleString('en-GB').replace(',', '')} | ${e.type}`;
    card.appendChild(meta);

    const txt = document.createElement('div');
    txt.className = 'text';
    txt.textContent = e.text;
    card.appendChild(txt);

    const role = document.createElement('div');
    role.className = 'role';
    role.textContent = `— ${e.role}`;
    card.appendChild(role);

    archive.appendChild(card);
  });
}

// Initialize
(async () => {
  const entries = await loadQuotes();
  renderTicker(entries);
  renderArchive(entries);
})();
