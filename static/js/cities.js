// Worldwide autocomplete using free Nominatim (OpenStreetMap) search API.
// Debounced fetch to avoid spamming the API.

function debounce(fn, wait){ let t; return function(...args){ clearTimeout(t); t=setTimeout(()=>fn.apply(this,args), wait); }; }

function buildDatalist(input){
  const listId = input.id + '-list';
  let list = document.getElementById(listId);
  if (!list) {
    list = document.createElement('datalist');
    list.id = listId;
    document.body.appendChild(list);
    input.setAttribute('list', listId);
  }
  return list;
}

async function queryPlaces(q){
  const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&addressdetails=1&limit=10&q=${encodeURIComponent(q)}`;
  const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) return [];
  return await res.json();
}

function formatPlace(p){
  const a = p.address || {};
  const city = a.city || a.town || a.village || a.hamlet || a.municipality || '';
  const state = a.state || a.county || '';
  const country = a.country || '';
  const parts = [city, state, country].filter(Boolean);
  return parts.join(', ') || p.display_name;
}

function setupAutocomplete(inputId){
  const input = document.getElementById(inputId);
  if (!input) return;
  const list = buildDatalist(input);

  const update = debounce(async ()=>{
    const q = input.value.trim();
    if (q.length < 2) return;
    const data = await queryPlaces(q);
    list.innerHTML='';
    const seen = new Set();
    data.forEach(p=>{
      const label = formatPlace(p);
      if (!label || seen.has(label)) return;
      seen.add(label);
      const opt = document.createElement('option');
      opt.value = label;
      list.appendChild(opt);
    });
  }, 300);

  input.addEventListener('input', update);
}

window.TravelAutocomplete = { setupAutocomplete };


