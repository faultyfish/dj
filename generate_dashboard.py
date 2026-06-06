# generate_dashboard.py — reads jobs from DB, writes docs/index.html

from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import get_engine, get_session_factory, init_db, migrate_db
from store import fetch_all_jobs

OUTPUT_PATH = Path(__file__).parent / "docs" / "index.html"


def is_dublin(location: str) -> bool:
    """Check if job location is in Dublin."""
    loc = location.lower()
    dublin_keywords = ["dublin", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9",
                       "d10", "d11", "d12", "d13", "d14", "d15", "d16", "d17", "d18",
                       "d20", "d24"]
    return any(keyword in loc for keyword in dublin_keywords)


def categorise(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["retail", "shop assistant", "cashier", "sales assistant", "store"]):
        return "retail"
    if any(k in t for k in ["barista", "bar ", "waiter", "waitress", "chef", "cook",
                              "hotel", "restaurant", "hospitality", "cafe", "café"]):
        return "hospitality"
    if any(k in t for k in ["warehouse", "picker", "packer", "forklift", "logistics", "stock"]):
        return "warehouse"
    if any(k in t for k in ["security", "guard", "door supervisor", "concierge"]):
        return "security"
    return "other"


def jobs_to_json(jobs) -> str:
    records = []
    for j in jobs:
        # Double-check: filter to Dublin only
        if not is_dublin(j.location):
            continue
        records.append({
            "title":       j.title,
            "company":     j.company,
            "location":    j.location,
            "source":      j.source,
            "job_type":    j.job_type,
            "salary":      j.salary or "Not listed",
            "score":       j.score,
            "date_posted": j.date_posted.isoformat() if j.date_posted else datetime.now(timezone.utc).isoformat(),
            "job_url":     j.job_url,
            "category":    categorise(j.title),
        })
    return json.dumps(records, ensure_ascii=False)


def build_html(jobs_json: str, generated_at: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dublin Part-Time Job Radar</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.0.0/tabler-icons.min.css">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:       #FAFAF9;
      --surface:  #FFFFFF;
      --sf2:      #F4F3EF;
      --border:   rgba(0,0,0,0.09);
      --border2:  rgba(0,0,0,0.16);
      --text:     #1C1C1A;
      --muted:    #6B6B68;
      --hint:     #A0A09C;
      --green:    #1D9E75;
      --green-bg: #E1F5EE;
      --green-dk: #0F6E56;
      --radius:   10px;
    }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; line-height: 1.5; }}
    a {{ color: inherit; text-decoration: none; }}

    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 1.25rem 4rem; }}

    /* Header */
    .header {{ padding: 1.75rem 0 1.25rem; border-bottom: 0.5px solid var(--border); margin-bottom: 1.25rem; display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 6px; }}
    .logo {{ font-size: 18px; font-weight: 500; letter-spacing: -0.4px; }}
    .logo span {{ color: var(--green); }}
    .header-right {{ font-size: 12px; color: var(--hint); }}
    .tagline {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}

    /* Stats */
    .stats {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; margin-bottom: 1.25rem; }}
    .stat {{ background: var(--sf2); border-radius: 8px; padding: 0.75rem 1rem; }}
    .stat-label {{ font-size: 11px; color: var(--muted); margin-bottom: 3px; }}
    .stat-value {{ font-size: 20px; font-weight: 500; }}

    /* Controls */
    .controls {{ display: flex; gap: 8px; margin-bottom: 0.875rem; flex-wrap: wrap; align-items: center; }}
    .search-wrap {{ position: relative; flex: 1; min-width: 180px; }}
    .search-wrap i {{ position: absolute; left: 9px; top: 50%; transform: translateY(-50%); font-size: 15px; color: var(--hint); pointer-events: none; }}
    #search {{ width: 100%; padding-left: 30px; height: 34px; font-size: 13px; border: 0.5px solid var(--border2); border-radius: 20px; background: var(--surface); color: var(--text); outline: none; font-family: inherit; }}
    #search:focus {{ border-color: var(--green); }}
    select {{ height: 34px; font-size: 13px; padding: 0 10px; border-radius: 8px; border: 0.5px solid var(--border2); background: var(--surface); color: var(--text); cursor: pointer; outline: none; font-family: inherit; }}

    /* Pills */
    .pills {{ display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 1rem; }}
    .pill {{ background: none; border: 0.5px solid var(--border2); border-radius: 20px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: var(--muted); font-family: inherit; transition: all 0.12s; }}
    .pill.active {{ background: var(--green-bg); border-color: var(--green); color: var(--green-dk); font-weight: 500; }}

    /* Table */
    .table-wrap {{ overflow-x: auto; border: 0.5px solid var(--border); border-radius: var(--radius); background: var(--surface); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    thead th {{ background: var(--sf2); padding: 9px 12px; text-align: left; font-weight: 500; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 0.5px solid var(--border); white-space: nowrap; cursor: pointer; user-select: none; }}
    thead th:hover {{ color: var(--text); }}
    thead th .sort-icon {{ font-size: 10px; margin-left: 3px; opacity: 0.4; }}
    thead th.sorted .sort-icon {{ opacity: 1; color: var(--green); }}
    tbody tr {{ border-bottom: 0.5px solid var(--border); transition: background 0.1s; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: #F7F6F2; }}
    td {{ padding: 9px 12px; vertical-align: middle; }}

    /* Column specific */
    .col-title {{ min-width: 180px; max-width: 260px; }}
    .col-title a {{ font-weight: 500; color: var(--text); }}
    .col-title a:hover {{ color: var(--green); }}
    .col-company {{ min-width: 130px; color: var(--muted); }}
    .col-location {{ min-width: 130px; color: var(--muted); font-size: 12px; }}
    .col-category {{ white-space: nowrap; }}
    .col-source {{ white-space: nowrap; }}
    .col-salary {{ white-space: nowrap; color: var(--muted); font-size: 12px; }}
    .col-date {{ white-space: nowrap; color: var(--hint); font-size: 12px; text-align: right; }}
    .col-apply {{ text-align: right; white-space: nowrap; }}

    /* Badges */
    .badge {{ display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 500; }}
    .cat-academic    {{ background: #EAF3DE; color: #3B6D11; }}
    .cat-admin       {{ background: #E6F1FB; color: #185FA5; }}
    .cat-support     {{ background: #FAEEDA; color: #854F0B; }}
    .cat-retail      {{ background: #EAF3DE; color: #3B6D11; }}
    .cat-hospitality {{ background: #FAECE7; color: #993C1D; }}
    .cat-warehouse   {{ background: #E6F1FB; color: #185FA5; }}
    .cat-security    {{ background: #FAEEDA; color: #854F0B; }}
    .cat-other       {{ background: #F1EFE8; color: #5F5E5A; }}
    .src-indeed   {{ background: #FFF3E0; color: #B45309; }}
    .src-linkedin {{ background: #E0F0FF; color: #1256A3; }}

    .apply-btn {{ font-size: 12px; padding: 4px 12px; border-radius: 20px; background: var(--green); color: #fff; border: none; cursor: pointer; font-weight: 500; font-family: inherit; display: inline-block; }}
    .apply-btn:hover {{ background: var(--green-dk); }}

    /* Pagination */
    .pagination {{ display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; }}
    .page-info {{ font-size: 12px; color: var(--muted); }}
    .page-btns {{ display: flex; gap: 5px; }}
    .page-btn {{ height: 30px; padding: 0 12px; font-size: 12px; border-radius: 8px; border: 0.5px solid var(--border2); background: var(--surface); color: var(--text); cursor: pointer; font-family: inherit; }}
    .page-btn:disabled {{ opacity: 0.35; cursor: default; }}
    .page-btn:not(:disabled):hover {{ background: var(--sf2); }}

    .empty {{ text-align: center; padding: 3rem; color: var(--muted); font-size: 13px; }}

    @media (max-width: 640px) {{
      .stats {{ grid-template-columns: repeat(2,1fr); }}
      .col-location, .col-salary, .col-source {{ display: none; }}
    }}
  </style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div>
      <div class="logo">Dublin <span>Job Radar</span></div>
      <div class="tagline">Part-time jobs in Dublin — refreshed every 6 hours</div>
    </div>
    <div class="header-right">Updated {generated_at}</div>
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-label">Total jobs</div><div class="stat-value" id="s-total">—</div></div>
    <div class="stat"><div class="stat-label">New today</div><div class="stat-value" id="s-new">—</div></div>
    <div class="stat"><div class="stat-label">Companies</div><div class="stat-value" id="s-companies">—</div></div>
    <div class="stat"><div class="stat-label">Sources</div><div class="stat-value" id="s-sources">—</div></div>
  </div>

  <div class="controls">
    <div class="search-wrap">
      <i class="ti ti-search"></i>
      <input id="search" type="text" placeholder="Search title or company...">
    </div>
    <select id="sort">
      <option value="date">Latest first</option>
      <option value="score">Best match</option>
      <option value="company">Company A–Z</option>
    </select>
  </div>

  <div class="pills" id="pills">
    <button class="pill active" data-cat="all">All</button>
    <button class="pill" data-cat="academic">Academic</button>
    <button class="pill" data-cat="admin">Admin</button>
    <button class="pill" data-cat="support">Support</button>
    <button class="pill" data-cat="retail">Retail</button>
    <button class="pill" data-cat="hospitality">Hospitality</button>
    <button class="pill" data-cat="warehouse">Warehouse</button>
    <button class="pill" data-cat="security">Security</button>
    <button class="pill" data-cat="other">Other</button>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th class="col-title"   data-col="title">Role <span class="sort-icon">↕</span></th>
          <th class="col-company" data-col="company">Company <span class="sort-icon">↕</span></th>
          <th class="col-location">Location</th>
          <th class="col-category" data-col="category">Category <span class="sort-icon">↕</span></th>
          <th class="col-source">Source</th>
          <th class="col-salary" data-col="salary">Salary <span class="sort-icon">↕</span></th>
          <th class="col-date"  data-col="date">Posted <span class="sort-icon">↕</span></th>
          <th class="col-apply"></th>
        </tr>
      </thead>
      <tbody id="job-tbody"></tbody>
    </table>
  </div>

  <div class="pagination">
    <div class="page-info" id="page-info"></div>
    <div class="page-btns">
      <button class="page-btn" id="prev-btn" disabled>&#8249; Prev</button>
      <button class="page-btn" id="next-btn">Next &#8250;</button>
    </div>
  </div>

</div>
<script>
const ALL_JOBS = {jobs_json};
const PER_PAGE = 25;
let page = 0;
let filtered = [];
let sortCol = 'date';
let sortDir = -1;

function daysAgo(d) {{
  const diff = Math.floor((Date.now() - new Date(d)) / 86400000);
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Yesterday';
  return diff + 'd ago';
}}

function shortLoc(loc) {{
  if (!loc) return '';
  const parts = loc.split(',');
  return parts[0].trim();
}}

function getFiltered() {{
  const q = document.getElementById('search').value.toLowerCase();
  const cat = document.querySelector('.pill.active').dataset.cat;
  let jobs = ALL_JOBS.filter(j => {{
    const mq = !q || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q);
    const mc = cat === 'all' || j.category === cat;
    return mq && mc;
  }});
  jobs.sort((a, b) => {{
    let av, bv;
    if (sortCol === 'date')    {{ av = new Date(a.date_posted); bv = new Date(b.date_posted); }}
    else if (sortCol === 'score')   {{ av = a.score; bv = b.score; }}
    else if (sortCol === 'company') {{ av = a.company.toLowerCase(); bv = b.company.toLowerCase(); }}
    else if (sortCol === 'title')   {{ av = a.title.toLowerCase(); bv = b.title.toLowerCase(); }}
    else if (sortCol === 'category'){{ av = a.category; bv = b.category; }}
    else if (sortCol === 'salary')  {{ av = a.salary || ''; bv = b.salary || ''; }}
    else {{ av = 0; bv = 0; }}
    if (av < bv) return sortDir;
    if (av > bv) return -sortDir;
    return 0;
  }});
  return jobs;
}}

function renderStats(jobs) {{
  document.getElementById('s-total').textContent = jobs.length;
  document.getElementById('s-new').textContent = jobs.filter(j => new Date(j.date_posted) > new Date(Date.now()-86400000)).length;
  document.getElementById('s-companies').textContent = new Set(jobs.map(j=>j.company)).size;
  document.getElementById('s-sources').textContent = new Set(jobs.map(j=>j.source)).size;
}}

function renderTable() {{
  filtered = getFiltered();
  renderStats(filtered);

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));
  if (page >= totalPages) page = totalPages - 1;
  const slice = filtered.slice(page * PER_PAGE, (page+1) * PER_PAGE);

  const tbody = document.getElementById('job-tbody');
  if (!slice.length) {{
    tbody.innerHTML = '<tr><td colspan="8" class="empty">No jobs match your filters.</td></tr>';
  }} else {{
    tbody.innerHTML = slice.map(j => {{
      const salary = j.salary ? j.salary : '<span style="color:var(--hint)">—</span>';
      const loc = shortLoc(j.location);
      return `<tr>
        <td class="col-title"><a href="${{j.job_url}}" target="_blank" rel="noopener">${{j.title}}</a></td>
        <td class="col-company">${{j.company}}</td>
        <td class="col-location">${{loc}}</td>
        <td class="col-category"><span class="badge cat-${{j.category}}">${{j.category}}</span></td>
        <td class="col-source"><span class="badge src-${{j.source}}">${{j.source}}</span></td>
        <td class="col-salary">${{salary}}</td>
        <td class="col-date">${{daysAgo(j.date_posted)}}</td>
        <td class="col-apply"><a class="apply-btn" href="${{j.job_url}}" target="_blank" rel="noopener">Apply ↗</a></td>
      </tr>`;
    }}).join('');
  }}

  const start = total ? page * PER_PAGE + 1 : 0;
  const end = Math.min((page+1) * PER_PAGE, total);
  document.getElementById('page-info').textContent = total ? `Showing ${{start}}–${{end}} of ${{total}} jobs` : 'No results';
  document.getElementById('prev-btn').disabled = page === 0;
  document.getElementById('next-btn').disabled = page >= totalPages - 1;

  // Update sort indicators
  document.querySelectorAll('thead th').forEach(th => {{
    th.classList.toggle('sorted', th.dataset.col === sortCol);
    const icon = th.querySelector('.sort-icon');
    if (icon && th.dataset.col === sortCol) icon.textContent = sortDir === -1 ? '↓' : '↑';
    else if (icon) icon.textContent = '↕';
  }});
}}

// Column sort
document.querySelectorAll('thead th[data-col]').forEach(th => {{
  th.addEventListener('click', () => {{
    if (sortCol === th.dataset.col) sortDir *= -1;
    else {{ sortCol = th.dataset.col; sortDir = -1; }}
    if (th.dataset.col === 'date') sortCol = 'date';
    page = 0;
    renderTable();
  }});
}});

// Sort dropdown
document.getElementById('sort').addEventListener('change', e => {{
  sortCol = e.target.value === 'date' ? 'date' : e.target.value === 'score' ? 'score' : 'company';
  sortDir = -1;
  page = 0;
  renderTable();
}});

document.getElementById('search').addEventListener('input', () => {{ page = 0; renderTable(); }});
document.getElementById('pills').addEventListener('click', e => {{
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  page = 0;
  renderTable();
}});
document.getElementById('prev-btn').addEventListener('click', () => {{ page--; renderTable(); }});
document.getElementById('next-btn').addEventListener('click', () => {{ page++; renderTable(); }});

renderTable();
</script>
</body>
</html>"""


def main():
    engine = get_engine()
    init_db(engine)
    migrate_db(engine)
    SessionFactory = get_session_factory(engine)

    with SessionFactory() as session:
        jobs = fetch_all_jobs(session, min_score=10)

    print(f"Fetched {len(jobs)} jobs from database")

    jobs_json = jobs_to_json(jobs)
    generated_at = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    html = build_html(jobs_json, generated_at)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
