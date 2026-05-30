# generate_dashboard.py — reads jobs from DB, writes docs/index.html

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import get_engine, get_session_factory, init_db
from store import fetch_all_jobs

OUTPUT_PATH = Path(__file__).parent / "docs" / "index.html"


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
        records.append({
            "title":      j.title,
            "company":    j.company,
            "location":   j.location,
            "source":     j.source,
            "job_type":   j.job_type,
            "salary":     j.salary or "Not listed",
            "score":      j.score,
            "date_posted": j.date_posted.isoformat() if j.date_posted else datetime.now(timezone.utc).isoformat(),
            "job_url":    j.job_url,
            "category":   categorise(j.title),
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
      --bg:        #FAFAF9;
      --surface:   #FFFFFF;
      --surface-2: #F4F3EF;
      --border:    rgba(0,0,0,0.10);
      --border-2:  rgba(0,0,0,0.18);
      --text:      #1C1C1A;
      --muted:     #6B6B68;
      --hint:      #A0A09C;
      --green:     #1D9E75;
      --green-bg:  #E1F5EE;
      --green-dk:  #0F6E56;
      --blue-bg:   #E6F1FB;
      --blue-dk:   #185FA5;
      --amber-bg:  #FAEEDA;
      --amber-dk:  #854F0B;
      --coral-bg:  #FAECE7;
      --coral-dk:  #993C1D;
      --gray-bg:   #F1EFE8;
      --gray-dk:   #5F5E5A;
      --radius:    12px;
      --radius-sm: 8px;
    }}

    body {{
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      font-size: 15px;
      line-height: 1.5;
    }}

    .container {{ max-width: 860px; margin: 0 auto; padding: 0 1.25rem 4rem; }}

    /* Header */
    .header {{ padding: 2rem 0 1.5rem; border-bottom: 0.5px solid var(--border); margin-bottom: 1.5rem; }}
    .header-row {{ display: flex; align-items: baseline; justify-content: space-between; }}
    .logo {{ font-size: 20px; font-weight: 500; letter-spacing: -0.5px; }}
    .logo span {{ color: var(--green); }}
    .updated {{ font-size: 12px; color: var(--hint); }}
    .tagline {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

    /* Stats */
    .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.5rem; }}
    .stat {{ background: var(--surface-2); border-radius: var(--radius-sm); padding: 0.875rem 1rem; }}
    .stat-label {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
    .stat-value {{ font-size: 22px; font-weight: 500; }}

    /* Controls */
    .controls {{ display: flex; gap: 10px; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }}
    .search-wrap {{ position: relative; flex: 1; min-width: 200px; }}
    .search-wrap i {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); font-size: 16px; color: var(--hint); pointer-events: none; }}
    #search {{
      width: 100%; padding-left: 34px; height: 36px; font-size: 14px;
      border: 0.5px solid var(--border-2); border-radius: 20px;
      background: var(--surface); color: var(--text); outline: none;
    }}
    #search:focus {{ border-color: var(--green); }}
    select {{
      height: 36px; font-size: 13px; padding: 0 10px;
      border-radius: var(--radius-sm); border: 0.5px solid var(--border-2);
      background: var(--surface); color: var(--text); cursor: pointer; outline: none;
    }}

    /* Pills */
    .pills {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 1.25rem; }}
    .pill {{
      background: none; border: 0.5px solid var(--border-2); border-radius: 20px;
      padding: 5px 14px; font-size: 13px; cursor: pointer; color: var(--muted);
      transition: all 0.15s; font-family: inherit;
    }}
    .pill.active {{ background: var(--green-bg); border-color: var(--green); color: var(--green-dk); font-weight: 500; }}

    /* Job cards */
    .jobs-list {{ display: flex; flex-direction: column; gap: 8px; }}
    .job-card {{
      background: var(--surface); border: 0.5px solid var(--border);
      border-radius: var(--radius); padding: 1rem 1.25rem;
      display: flex; align-items: flex-start; gap: 1rem;
      text-decoration: none; color: inherit; transition: border-color 0.15s;
    }}
    .job-card:hover {{ border-color: var(--border-2); }}
    .job-icon {{
      width: 38px; height: 38px; border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; font-size: 18px;
    }}
    .job-body {{ flex: 1; min-width: 0; }}
    .job-title {{ font-size: 15px; font-weight: 500; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .job-meta {{ font-size: 13px; color: var(--muted); margin-bottom: 8px; }}
    .job-meta span {{ margin-right: 12px; }}
    .job-meta i {{ font-size: 13px; vertical-align: -1px; margin-right: 3px; }}
    .tags {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .tag {{ font-size: 11px; padding: 3px 9px; border-radius: 20px; font-weight: 500; }}
    .tag-indeed  {{ background: var(--amber-bg); color: var(--amber-dk); }}
    .tag-linkedin {{ background: var(--blue-bg); color: var(--blue-dk); }}
    .tag-type {{ background: var(--green-bg); color: var(--green-dk); }}
    .tag-score {{ background: var(--gray-bg); color: var(--gray-dk); }}
    .job-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 8px; flex-shrink: 0; }}
    .job-date {{ font-size: 12px; color: var(--hint); }}
    .apply-btn {{
      font-size: 13px; padding: 5px 14px; border-radius: 20px;
      background: var(--green); color: #fff; border: none; cursor: pointer;
      font-weight: 500; white-space: nowrap; font-family: inherit; text-decoration: none;
      display: inline-block;
    }}
    .apply-btn:hover {{ background: var(--green-dk); }}

    /* Icons per category */
    .icon-retail      {{ background: #EAF3DE; color: #3B6D11; }}
    .icon-hospitality {{ background: var(--coral-bg); color: var(--coral-dk); }}
    .icon-warehouse   {{ background: var(--blue-bg); color: var(--blue-dk); }}
    .icon-security    {{ background: var(--amber-bg); color: var(--amber-dk); }}
    .icon-other       {{ background: var(--gray-bg); color: var(--gray-dk); }}

    /* Pagination */
    .pagination {{
      display: flex; justify-content: space-between; align-items: center;
      margin-top: 1.5rem; padding-top: 1rem; border-top: 0.5px solid var(--border);
    }}
    .page-info {{ font-size: 13px; color: var(--muted); }}
    .page-btns {{ display: flex; gap: 6px; }}
    .page-btn {{
      height: 32px; padding: 0 14px; font-size: 13px;
      border-radius: var(--radius-sm); border: 0.5px solid var(--border-2);
      background: var(--surface); color: var(--text); cursor: pointer; font-family: inherit;
    }}
    .page-btn:disabled {{ opacity: 0.35; cursor: default; }}
    .page-btn:not(:disabled):hover {{ background: var(--surface-2); }}

    .empty {{ text-align: center; padding: 3rem 1rem; color: var(--muted); font-size: 14px; }}

    @media (max-width: 600px) {{
      .stats {{ grid-template-columns: repeat(2, 1fr); }}
      .job-right {{ display: none; }}
      .header-row {{ flex-direction: column; gap: 4px; }}
    }}
  </style>
</head>
<body>
<div class="container">

  <header class="header">
    <div class="header-row">
      <div class="logo">Dublin <span>Job Radar</span></div>
      <div class="updated">Updated {generated_at}</div>
    </div>
    <div class="tagline">Part-time jobs in Dublin — refreshed every 6 hours</div>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-label">Total jobs</div><div class="stat-value" id="s-total">—</div></div>
    <div class="stat"><div class="stat-label">New today</div><div class="stat-value" id="s-new">—</div></div>
    <div class="stat"><div class="stat-label">Companies</div><div class="stat-value" id="s-companies">—</div></div>
    <div class="stat"><div class="stat-label">Sources</div><div class="stat-value" id="s-sources">—</div></div>
  </div>

  <div class="controls">
    <div class="search-wrap">
      <i class="ti ti-search"></i>
      <input id="search" type="text" placeholder="Search job title or company...">
    </div>
    <select id="sort">
      <option value="date">Latest first</option>
      <option value="score">Best match</option>
    </select>
  </div>

  <div class="pills" id="pills">
    <button class="pill active" data-cat="all">All</button>
    <button class="pill" data-cat="retail">Retail</button>
    <button class="pill" data-cat="hospitality">Hospitality</button>
    <button class="pill" data-cat="warehouse">Warehouse</button>
    <button class="pill" data-cat="security">Security</button>
    <button class="pill" data-cat="other">Other</button>
  </div>

  <div id="job-list"></div>

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
const PER_PAGE = 10;
let page = 0;
let filtered = [];

const ICONS = {{
  retail:      {{cls:'icon-retail',      icon:'ti-shopping-cart'}},
  hospitality: {{cls:'icon-hospitality', icon:'ti-coffee'}},
  warehouse:   {{cls:'icon-warehouse',   icon:'ti-package'}},
  security:    {{cls:'icon-security',    icon:'ti-shield-check'}},
  other:       {{cls:'icon-other',       icon:'ti-briefcase'}},
}};

function daysAgo(d) {{
  const diff = Math.floor((Date.now() - new Date(d)) / 86400000);
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Yesterday';
  return diff + 'd ago';
}}

function getFiltered() {{
  const q = document.getElementById('search').value.toLowerCase();
  const cat = document.querySelector('.pill.active').dataset.cat;
  const sort = document.getElementById('sort').value;
  let jobs = ALL_JOBS.filter(j => {{
    const matchQ = !q || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q);
    const matchCat = cat === 'all' || j.category === cat;
    return matchQ && matchCat;
  }});
  jobs.sort((a, b) => sort === 'score'
    ? b.score - a.score
    : new Date(b.date_posted) - new Date(a.date_posted));
  return jobs;
}}

function renderStats(jobs) {{
  document.getElementById('s-total').textContent = jobs.length;
  const now = Date.now();
  document.getElementById('s-new').textContent = jobs.filter(j => new Date(j.date_posted) > new Date(now - 86400000)).length;
  document.getElementById('s-companies').textContent = new Set(jobs.map(j => j.company)).size;
  document.getElementById('s-sources').textContent = new Set(jobs.map(j => j.source)).size;
}}

function renderJobs() {{
  filtered = getFiltered();
  renderStats(filtered);
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));
  if (page >= totalPages) page = totalPages - 1;
  const slice = filtered.slice(page * PER_PAGE, (page + 1) * PER_PAGE);

  const list = document.getElementById('job-list');
  if (!slice.length) {{
    list.innerHTML = '<div class="empty"><i class="ti ti-search-off" style="font-size:24px;display:block;margin-bottom:8px"></i>No jobs match your filters.</div>';
  }} else {{
    list.innerHTML = '<div class="jobs-list">' + slice.map(j => {{
      const ic = ICONS[j.category];
      const srcTag = j.source === 'indeed'
        ? '<span class="tag tag-indeed">Indeed</span>'
        : '<span class="tag tag-linkedin">LinkedIn</span>';
      const salary = j.salary && j.salary !== 'Not listed'
        ? `<span><i class="ti ti-currency-euro"></i>${{j.salary}}</span>` : '';
      return `<a class="job-card" href="${{j.job_url}}" target="_blank" rel="noopener">
        <div class="job-icon ${{ic.cls}}"><i class="ti ${{ic.icon}}"></i></div>
        <div class="job-body">
          <div class="job-title">${{j.title}}</div>
          <div class="job-meta">
            <span><i class="ti ti-building"></i>${{j.company}}</span>
            <span><i class="ti ti-map-pin"></i>${{j.location}}</span>
            ${{salary}}
          </div>
          <div class="tags">
            ${{srcTag}}
            <span class="tag tag-type">${{j.job_type}}</span>
            <span class="tag tag-score">score ${{j.score}}</span>
          </div>
        </div>
        <div class="job-right">
          <div class="job-date">${{daysAgo(j.date_posted)}}</div>
          <a class="apply-btn" href="${{j.job_url}}" target="_blank" rel="noopener">Apply &#8599;</a>
        </div>
      </a>`;
    }}).join('') + '</div>';
  }}

  const start = total ? page * PER_PAGE + 1 : 0;
  const end = Math.min((page + 1) * PER_PAGE, total);
  document.getElementById('page-info').textContent = total
    ? `Showing ${{start}}–${{end}} of ${{total}} jobs` : 'No results';
  document.getElementById('prev-btn').disabled = page === 0;
  document.getElementById('next-btn').disabled = page >= totalPages - 1;
}}

function changePage(dir) {{ page += dir; renderJobs(); }}

document.getElementById('search').addEventListener('input', () => {{ page = 0; renderJobs(); }});
document.getElementById('sort').addEventListener('change', () => {{ page = 0; renderJobs(); }});
document.getElementById('pills').addEventListener('click', e => {{
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  page = 0;
  renderJobs();
}});
document.getElementById('prev-btn').addEventListener('click', () => changePage(-1));
document.getElementById('next-btn').addEventListener('click', () => changePage(1));

renderJobs();
</script>
</body>
</html>"""


def main():
    engine = get_engine()
    init_db(engine)
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
