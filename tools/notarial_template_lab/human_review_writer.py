from __future__ import annotations

import html
import json
from pathlib import Path


def write_human_review_html(artifacts_dir: str | Path) -> Path:
    output_dir = Path(artifacts_dir)
    profile = read_json(output_dir / "02_document_profile.json", {})
    proposals = read_json(output_dir / "03_field_proposals_llm.json", [])
    document_map = read_json(output_dir / "01_document_map.json", {})
    output_path = output_dir / "05_human_review.html"
    output_path.write_text(render_human_review_html(profile, proposals, document_map), encoding="utf-8")
    return output_path


def render_human_review_html(profile: dict, proposals: list[dict], document_map: dict) -> str:
    source_filename = document_map.get("source_filename") or "Documento"
    quality = document_map.get("quality") if isinstance(document_map.get("quality"), dict) else {}
    proposal_payload = json.dumps(normalize_proposals(proposals), ensure_ascii=False)
    profile_payload = json.dumps(profile, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Revision humana - Notarial Template Lab</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #162033; background: #f7f9fc; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .toolbar, .summary, .proposal {{ background: #fff; border: 1px solid #d8e0ea; border-radius: 8px; padding: 14px; margin-bottom: 12px; }}
    .toolbar {{ display: grid; grid-template-columns: repeat(6, minmax(120px, 1fr)); gap: 10px; align-items: end; }}
    label {{ display: block; font-size: 12px; font-weight: 700; color: #40516a; margin-bottom: 4px; }}
    input, select, button {{ width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #bac6d6; border-radius: 6px; background: #fff; }}
    button {{ cursor: pointer; font-weight: 700; }}
    .export {{ background: #0f766e; color: #fff; border-color: #0f766e; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }}
    .metric {{ background: #edf3f8; border-radius: 6px; padding: 10px; }}
    .proposal {{ display: grid; grid-template-columns: 220px 1fr; gap: 12px; }}
    .decision {{ border-right: 1px solid #e2e8f0; padding-right: 12px; }}
    .meta {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; font-size: 12px; margin-bottom: 8px; }}
    .pill {{ display: inline-block; padding: 3px 7px; border-radius: 999px; background: #e8eef6; margin-right: 4px; }}
    .context {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px; margin: 8px 0; font-size: 12px; }}
    .occ {{ border-top: 1px solid #e2e8f0; padding-top: 6px; margin-top: 6px; font-size: 12px; }}
    code {{ background: #edf3f8; padding: 2px 4px; border-radius: 4px; }}
    .hidden {{ display: none; }}
  </style>
</head>
<body>
  <h1>Revision humana de propuestas</h1>
  <div class="summary">
    <h2>{esc(source_filename)}</h2>
    <div class="grid">
      <div class="metric"><strong id="proposalCount">{len(proposals)}</strong><br/>Propuestas LLM</div>
      <div class="metric"><strong>{esc(profile.get("document_type", "no_determinado"))}</strong><br/>Tipo</div>
      <div class="metric"><strong>{esc(profile.get("recommended_mode", "no_determinado"))}</strong><br/>Modo</div>
      <div class="metric"><strong>{esc(", ".join(profile.get("acts_detected") or []))}</strong><br/>Actos</div>
      <div class="metric"><strong>{esc(quality.get("total_blocks", ""))}</strong><br/>Bloques</div>
    </div>
  </div>

  <div class="toolbar">
    <div><label>Tipo</label><select id="typeFilter"><option value="">Todos</option></select></div>
    <div><label>Confianza minima</label><input id="confidenceFilter" type="number" min="0" max="1" step="0.05" value="0" /></div>
    <div><label>Rol</label><select id="roleFilter"><option value="">Todos</option></select></div>
    <div><label>Scope</label><select id="scopeFilter"><option value="">Todos</option></select></div>
    <div><label>Buscar</label><input id="searchFilter" type="search" placeholder="Texto, marcador, evidencia" /></div>
    <div><label>Exportar</label><button class="export" id="exportButton">Descargar review_decisions.json</button></div>
  </div>

  <div id="proposalList"></div>

  <script>
    const profile = {profile_payload};
    const proposals = {proposal_payload};
    const decisions = new Map();

    function init() {{
      fillSelect("typeFilter", unique(proposals.map(p => p.proposal_type)));
      fillSelect("roleFilter", unique(proposals.map(p => p.role || "")));
      fillSelect("scopeFilter", unique(proposals.map(p => p.scope || "")));
      ["typeFilter", "confidenceFilter", "roleFilter", "scopeFilter", "searchFilter"].forEach(id => {{
        document.getElementById(id).addEventListener("input", render);
      }});
      document.getElementById("exportButton").addEventListener("click", exportDecisions);
      proposals.forEach(p => decisions.set(p.id, defaultDecision(p)));
      render();
    }}

    function fillSelect(id, values) {{
      const select = document.getElementById(id);
      values.filter(Boolean).forEach(value => {{
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }});
    }}

    function unique(values) {{
      return [...new Set(values)].sort();
    }}

    function defaultDecision(proposal) {{
      return {{
        field_key: proposal.field_key,
        value: proposal.value,
        decision: "review_required",
        marker: proposal.marker,
        apply_strategy: proposal.apply_strategy === "all_occurrences" ? "all_occurrences" : "selected_occurrences",
        occurrence_ids: proposal.occurrences.map(o => o.occurrence_id).filter(Boolean),
        notes: ""
      }};
    }}

    function passesFilters(proposal) {{
      const type = document.getElementById("typeFilter").value;
      const role = document.getElementById("roleFilter").value;
      const scope = document.getElementById("scopeFilter").value;
      const confidence = parseFloat(document.getElementById("confidenceFilter").value || "0");
      const search = document.getElementById("searchFilter").value.trim().toLowerCase();
      if (type && proposal.proposal_type !== type) return false;
      if (role && (proposal.role || "") !== role) return false;
      if (scope && (proposal.scope || "") !== scope) return false;
      if ((proposal.confidence || 0) < confidence) return false;
      if (search) {{
        const haystack = JSON.stringify(proposal).toLowerCase();
        if (!haystack.includes(search)) return false;
      }}
      return true;
    }}

    function render() {{
      const list = document.getElementById("proposalList");
      list.innerHTML = "";
      const filtered = proposals.filter(passesFilters);
      document.getElementById("proposalCount").textContent = filtered.length + " / " + proposals.length;
      filtered.forEach(proposal => list.appendChild(renderProposal(proposal)));
    }}

    function renderProposal(proposal) {{
      const decision = decisions.get(proposal.id);
      const article = document.createElement("article");
      article.className = "proposal";
      article.innerHTML = `
        <div class="decision">
          <label>Decision</label>
          <select data-action="decision">
            <option value="confirm">Confirmar</option>
            <option value="reject">Rechazar</option>
            <option value="review_required">Review required</option>
          </select>
          <label>Marker final</label>
          <input data-action="marker" value="${{escapeAttr(decision.marker)}}" />
          <label>Estrategia</label>
          <select data-action="strategy">
            <option value="all_occurrences">all_occurrences</option>
            <option value="selected_occurrences">selected_occurrences</option>
            <option value="review_required">review_required</option>
          </select>
          <label>Notas</label>
          <input data-action="notes" value="${{escapeAttr(decision.notes || "")}}" />
        </div>
        <div>
          <h2>${{escapeHtml(proposal.label)}} <code>${{escapeHtml(proposal.field_key)}}</code></h2>
          <div class="meta">
            <span><strong>Tipo:</strong> ${{escapeHtml(proposal.proposal_type)}}</span>
            <span><strong>Confianza:</strong> ${{Number(proposal.confidence || 0).toFixed(2)}}</span>
            <span><strong>Rol:</strong> ${{escapeHtml(proposal.role || "")}}</span>
            <span><strong>Scope:</strong> ${{escapeHtml(proposal.scope || "")}}</span>
          </div>
          <p><strong>Value:</strong> ${{escapeHtml(proposal.value)}}</p>
          <p><strong>Marker:</strong> <code>${{escapeHtml(proposal.marker)}}</code></p>
          <p><strong>Reason:</strong> ${{escapeHtml(proposal.reason || "")}}</p>
          <p>${{(proposal.evidence || []).map(item => `<span class="pill">${{escapeHtml(item)}}</span>`).join("")}}</p>
          <div>${{proposal.occurrences.map(o => renderOccurrence(proposal, o, decision)).join("")}}</div>
        </div>
      `;
      article.querySelector('[data-action="decision"]').value = decision.decision;
      article.querySelector('[data-action="strategy"]').value = decision.apply_strategy;
      article.querySelector('[data-action="decision"]').addEventListener("change", event => updateDecision(proposal, "decision", event.target.value));
      article.querySelector('[data-action="marker"]').addEventListener("input", event => updateDecision(proposal, "marker", event.target.value));
      article.querySelector('[data-action="strategy"]').addEventListener("change", event => updateDecision(proposal, "apply_strategy", event.target.value));
      article.querySelector('[data-action="notes"]').addEventListener("input", event => updateDecision(proposal, "notes", event.target.value));
      article.querySelectorAll('[data-occurrence-id]').forEach(input => {{
        input.addEventListener("change", event => toggleOccurrence(proposal, event.target.dataset.occurrenceId, event.target.checked));
      }});
      return article;
    }}

    function renderOccurrence(proposal, occurrence, decision) {{
      const id = occurrence.occurrence_id || `${{proposal.id}}:${{occurrence.block_id}}:${{occurrence.start}}`;
      const checked = decision.occurrence_ids.includes(id) ? "checked" : "";
      return `
        <div class="occ">
          <label><input type="checkbox" data-occurrence-id="${{escapeAttr(id)}}" ${{checked}} /> seleccionar ocurrencia</label>
          <div><strong>block_id:</strong> <code>${{escapeHtml(occurrence.block_id || "")}}</code></div>
          <div><strong>location:</strong> ${{escapeHtml(occurrence.location || "")}}</div>
          <div><strong>start/end:</strong> ${{occurrence.start}} / ${{occurrence.end}}</div>
          <div class="context">${{escapeHtml(occurrence.before || "")}} <strong>${{escapeHtml(occurrence.text || proposal.value)}}</strong> ${{escapeHtml(occurrence.after || "")}}</div>
        </div>
      `;
    }}

    function updateDecision(proposal, key, value) {{
      const decision = decisions.get(proposal.id);
      decision[key] = value;
      decisions.set(proposal.id, decision);
    }}

    function toggleOccurrence(proposal, occurrenceId, checked) {{
      const decision = decisions.get(proposal.id);
      const selected = new Set(decision.occurrence_ids);
      if (checked) selected.add(occurrenceId);
      else selected.delete(occurrenceId);
      decision.occurrence_ids = [...selected];
      decisions.set(proposal.id, decision);
    }}

    function exportDecisions() {{
      const payload = {{ decisions: [...decisions.values()] }};
      const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "review_decisions.json";
      link.click();
      URL.revokeObjectURL(url);
    }}

    function escapeHtml(value) {{
      return String(value || "").replace(/[&<>"']/g, char => ({{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}}[char]));
    }}

    function escapeAttr(value) {{
      return escapeHtml(value).replace(/`/g, "&#96;");
    }}

    init();
  </script>
</body>
</html>"""


def normalize_proposals(proposals: list[dict]) -> list[dict]:
    normalized = []
    for index, proposal in enumerate(proposals):
        item = dict(proposal)
        item["id"] = proposal_id(item, index)
        occurrences = item.get("occurrences") if isinstance(item.get("occurrences"), list) else []
        normalized_occurrences = []
        for occurrence_index, occurrence in enumerate(occurrences):
            if not isinstance(occurrence, dict):
                continue
            normalized_occurrence = dict(occurrence)
            if not normalized_occurrence.get("occurrence_id"):
                normalized_occurrence["occurrence_id"] = f"{item['id']}_occ_{occurrence_index + 1}"
            normalized_occurrences.append(normalized_occurrence)
        item["occurrences"] = normalized_occurrences
        normalized.append(item)
    return normalized


def proposal_id(proposal: dict, index: int) -> str:
    return f"{proposal.get('field_key') or 'proposal'}_{index + 1}"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value) -> str:
    return html.escape(str(value or ""))
