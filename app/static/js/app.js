async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

function renderJSON(targetId, data) {
  document.getElementById(targetId).textContent = JSON.stringify(data, null, 2);
}

async function loadOccupations() {
  const res = await fetch('/api/occupations');
  const data = await res.json();
  const list = document.getElementById('occupations-list');
  list.innerHTML = '';
  data.occupations.forEach(o => {
    const div = document.createElement('div');
    div.className = 'occupation';
    div.innerHTML = `<strong>${o.name}</strong><br/>${o.description}<br/><small>Skills: ${o.required_skills.join(', ')}</small>`;
    list.appendChild(div);
  });
}

function wireForms() {
  document.getElementById('assessment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const payload = {
      interests: form.interests.value,
      skills: form.skills.value,
      education: form.education.value,
      experience: form.experience.value
    };
    const data = await postJSON('/api/assess', payload);
    renderJSON('assessment-output', data);
  });

  document.getElementById('match-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const payload = {
      skills: form.skills.value,
      interests: form.interests.value,
      top_k: parseInt(form.top_k.value || '5', 10)
    };
    const data = await postJSON('/api/match', payload);
    renderJSON('match-output', data);
  });

  const chatBox = document.getElementById('chat-box');
  document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = e.target.message;
    const msg = input.value.trim();
    if (!msg) return;
    addChat('user', msg);
    const data = await postJSON('/api/chat', { message: msg });
    addChat('assistant', data.message);
    input.value = '';
  });

  function addChat(role, text) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.textContent = `${role === 'user' ? 'You' : 'Guide'}: ${text}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  wireForms();
  loadOccupations();
});
