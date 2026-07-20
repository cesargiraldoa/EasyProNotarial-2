import base64, pathlib
base = pathlib.Path('/home/user/EasyProNotarial-2/docs/ecosistema-notarial/prototipos')
wz = (base/'wizard-compraventa.html').read_text(encoding='utf-8')
ed = (base/'editor-vinculado.html').read_text(encoding='utf-8')

# --- patch wizard: el botón postea al parent (iframe) en vez de window.open ---
wz_old = """  g('btnEditor').addEventListener('click',function(){
    var ok=true;
    try{ localStorage.setItem('easypro_editor_handoff',JSON.stringify(buildHandoff())); }catch(e){ ok=false; }
    if(ok){ window.open('editor-vinculado.html','_blank'); }
    else { alert('No se pudo pasar al editor (almacenamiento del navegador no disponible en file://). Ábrelo desde un servidor local o el mismo origen.'); }
  });"""
wz_new = """  g('btnEditor').addEventListener('click',function(){
    try{ parent.postMessage({t:'ep-handoff',d:buildHandoff()},'*'); }catch(e){ window.open('editor-vinculado.html','_blank'); }
  });"""
assert wz_old in wz, 'WIZARD patch target not found'
wz = wz.replace(wz_old, wz_new)

# --- patch editor: recibe el borrador por postMessage ---
ed_anchor = "  /* init */"
ed_inject = """  function applyHandoff(d){ if(!d||!d.html) return; if(d.labels) for(var k in d.labels){ fieldMeta[k]={label:d.labels[k]}; } editor.innerHTML='<h4>Escritura p\\u00fablica \\u2014 borrador recibido del asistente de captura</h4>'+d.html; g('#note').textContent='Borrador recibido del wizard \\u2014 ed\\u00edtalo, vincula, inserta cl\\u00e1usulas o activa control de cambios'; snapshot(); rebuildPanel(); say('Documento cargado desde el wizard \\u2014 '+docFields().length+' campos vinculados'); }
  window.addEventListener('message',function(e){ if(e.data&&e.data.t==='ep-handoff'){ applyHandoff(e.data.d); } });
"""
assert ed_anchor in ed, 'EDITOR anchor not found'
ed = ed.replace(ed_anchor, ed_inject + ed_anchor, 1)

def b64(s): return base64.b64encode(s.encode('utf-8')).decode('ascii')
wz_b64, ed_b64 = b64(wz), b64(ed)

combined = """<title>Ecosistema Notarial — Demo: captura → editor</title>
<style>
  :root{ --paper:#FBFAF7; --ink:#1B1E23; --ink-soft:#4A5058; --chrome:#26314B; --accent:#31456E; --line:#E4E1D8; --gold:#C9A400; }
  @media (prefers-color-scheme:dark){:root{ --paper:#181A1E; --ink:#E8E6E0; --ink-soft:#B4B7BD; --chrome:#0F1116; --accent:#8FA6D6; --line:#2B2E35; }}
  :root[data-theme="light"]{ --paper:#FBFAF7; --ink:#1B1E23; --chrome:#26314B; --accent:#31456E; --line:#E4E1D8; }
  :root[data-theme="dark"]{ --paper:#181A1E; --ink:#E8E6E0; --chrome:#0F1116; --accent:#8FA6D6; --line:#2B2E35; }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;}
  body{background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;display:flex;flex-direction:column;height:100vh;}
  .bar{background:var(--chrome);color:#EDEFF4;padding:10px 16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
  .bar .brand{font-family:Georgia,"Times New Roman",serif;font-weight:600;font-size:15px;letter-spacing:.01em;}
  .bar .brand span{color:#B9C1D4;font-weight:400;font-size:12.5px;margin-left:8px;}
  .tabs{display:flex;gap:6px;margin-left:auto;}
  .tab{font:inherit;font-size:13px;font-weight:600;color:#D7DEEC;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:6px 14px;cursor:pointer;}
  .tab[aria-selected="true"]{background:var(--paper);color:var(--chrome);border-color:var(--paper);}
  .tab:focus-visible{outline:2px solid var(--gold);outline-offset:2px;}
  .hint{width:100%;font-size:11.5px;color:#9FA9C0;margin-top:-2px;}
  .stage{flex:1;position:relative;min-height:0;}
  iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:var(--paper);}
  iframe[hidden]{display:none;}
</style>

<div class="bar">
  <div class="brand">Ecosistema Notarial<span>Compraventa + Hipoteca · demo de flujo</span></div>
  <div class="tabs" role="tablist">
    <button class="tab" role="tab" id="tab-wz" aria-selected="true" aria-controls="fr-wz">1 · Captura (wizard)</button>
    <button class="tab" role="tab" id="tab-ed" aria-selected="false" aria-controls="fr-ed">2 · Editor del protocolista</button>
  </div>
  <div class="hint">En “Captura”, ajusta los datos y pulsa <b>“Abrir en el editor”</b>: el borrador —con los campos ya vinculados— salta a la pestaña “Editor”.</div>
</div>
<div class="stage">
  <iframe id="fr-wz" title="Wizard de captura"></iframe>
  <iframe id="fr-ed" title="Editor del protocolista" hidden></iframe>
</div>

<script>
(function(){
  function dec(b){ return new TextDecoder('utf-8').decode(Uint8Array.from(atob(b), function(c){return c.charCodeAt(0);})); }
  var WZ="__WZ__", ED="__ED__";
  var frW=document.getElementById('fr-wz'), frE=document.getElementById('fr-ed');
  frW.srcdoc=dec(WZ); frE.srcdoc=dec(ED);
  var tabW=document.getElementById('tab-wz'), tabE=document.getElementById('tab-ed');
  function show(which){
    var ed = which==='ed';
    frW.hidden=ed; frE.hidden=!ed;
    tabW.setAttribute('aria-selected', ed?'false':'true');
    tabE.setAttribute('aria-selected', ed?'true':'false');
  }
  tabW.addEventListener('click',function(){ show('wz'); });
  tabE.addEventListener('click',function(){ show('ed'); });
  window.addEventListener('message',function(e){
    if(e.data && e.data.t==='ep-handoff'){
      try{ frE.contentWindow.postMessage(e.data,'*'); }catch(err){}
      show('ed');
    }
  });
})();
</script>
"""
combined = combined.replace('__WZ__', wz_b64).replace('__ED__', ed_b64)
out = pathlib.Path('/tmp/claude-0/-home-user-EasyProNotarial-2/2dec81cd-eef8-542f-90f5-b5edd0dceedf/scratchpad/demo-ecosistema-notarial.html')
out.write_text(combined, encoding='utf-8')
print('OK', out, len(combined), 'bytes')
