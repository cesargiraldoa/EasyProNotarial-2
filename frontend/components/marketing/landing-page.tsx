const landingStyles = `
.ecosistema-landing {
  --navy: #101418;
  --navy2: #171c22;
  --navy3: #242a33;
  --mint: #d89b45;
  --mint2: #b87333;
  --white: #ffffff;
  --gray: #d7dee8;
  --gray2: #9aa6b2;
  --card: #1b222b;
  --border: rgba(216,155,69,0.24);
  min-height: 100vh;
  background: var(--navy);
  color: var(--white);
  font-family: -apple-system, 'Segoe UI', system-ui, sans-serif;
  overflow-x: hidden;
}
.ecosistema-landing * { margin:0; padding:0; box-sizing:border-box; }
.ecosistema-landing nav {
  position:fixed; top:0; left:0; right:0; z-index:100;
  display:flex; align-items:center; justify-content:space-between;
  padding:1.2rem 4rem;
  background:rgba(16,20,24,0.96);
  backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);
}
.ecosistema-landing .logo { font-family: 'Segoe UI', system-ui, sans-serif; font-weight:800; font-size:1.4rem; letter-spacing:-.02em; }
.ecosistema-landing .logo span { color:var(--mint); }
.ecosistema-landing nav ul { list-style:none; display:flex; gap:2.5rem; }
.ecosistema-landing nav ul a { color:#a0b8cc; text-decoration:none; font-size:.9rem; transition:.2s; font-weight:500; }
.ecosistema-landing nav ul a:hover { color:var(--mint); }
.ecosistema-landing .nav-btn { background:var(--mint); color:var(--navy); border:none; padding:.6rem 1.4rem; border-radius:2rem; font-weight:700; font-size:.9rem; cursor:pointer; font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; text-decoration:none; }
.ecosistema-landing .listening-claim {
  display:block;
  max-width:760px;
  color:var(--mint);
  font-family:'Segoe UI', system-ui, sans-serif;
  font-size:clamp(1.35rem, 2.4vw, 2rem);
  line-height:1.2;
  font-weight:800;
  letter-spacing:-.02em;
  margin:0 0 1.1rem;
}
.ecosistema-landing .final-listening {
  position:relative;
  z-index:2;
  color:var(--mint);
  font-family:'Segoe UI', system-ui, sans-serif;
  font-size:clamp(1.4rem, 2.5vw, 2.2rem);
  line-height:1.2;
  font-weight:800;
  letter-spacing:-.02em;
  margin:3.2rem auto 1rem;
  max-width:900px;
}
.ecosistema-landing .hero {
  min-height:100vh; display:flex; align-items:center;
  padding:8rem 4rem 4rem; position:relative; overflow:hidden;
}
.ecosistema-landing .hero-glow {
  position:absolute; top:-200px; right:-200px;
  width:800px; height:800px;
  background:radial-gradient(circle, rgba(216,155,69,0.11) 0%, transparent 70%);
  pointer-events:none;
}
.ecosistema-landing .hero-content { max-width:700px; position:relative; z-index:2; }
.ecosistema-landing .hero-visual {
  position:absolute;
  right:4rem;
  bottom:3rem;
  width:min(38vw, 520px);
  max-height:72vh;
  object-fit:cover;
  border-radius:22px;
  border:1px solid var(--border);
  box-shadow:0 32px 90px rgba(0,0,0,0.42);
  z-index:1;
}
.ecosistema-landing .badge {
  display:inline-flex; align-items:center; gap:.5rem;
  background:rgba(216,155,69,0.14); border:1px solid var(--border);
  color:var(--mint); padding:.4rem 1rem; border-radius:2rem;
  font-size:.8rem; font-weight:600; margin-bottom:2rem;
}
.ecosistema-landing .badge-dot { width:7px; height:7px; border-radius:50%; background:var(--mint); animation:ecosistemaPulse 2s infinite; }
@keyframes ecosistemaPulse { 0%,100%{opacity:1}50%{opacity:.3} }
.ecosistema-landing h1 { font-family: 'Segoe UI', system-ui, sans-serif; font-size:4.2rem; font-weight:800; line-height:1.05; margin-bottom:1.5rem; letter-spacing:-.03em; }
.ecosistema-landing h1 em { color:var(--mint); font-style:normal; }
.ecosistema-landing .hero-sub { color:var(--gray); font-size:1.1rem; line-height:1.75; margin-bottom:2.5rem; max-width:540px; font-weight:400; }
.ecosistema-landing .hero-btns { display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:3.5rem; }
.ecosistema-landing .btn-primary { background:var(--mint); color:var(--navy); padding:.9rem 2.2rem; border-radius:2rem; font-weight:700; font-size:1rem; border:none; cursor:pointer; transition:.2s; font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; }
.ecosistema-landing .btn-primary:hover { background:var(--mint2); transform:translateY(-2px); }
.ecosistema-landing .btn-secondary { background:transparent; color:var(--white); padding:.9rem 2.2rem; border-radius:2rem; font-weight:500; font-size:1rem; border:1px solid rgba(255,255,255,0.2); cursor:pointer; transition:.2s; font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; }
.ecosistema-landing .btn-secondary:hover { border-color:var(--mint); color:var(--mint); }
.ecosistema-landing .hero-stats { display:flex; gap:3rem; }
.ecosistema-landing .stat-val { font-family: 'Segoe UI', system-ui, sans-serif; font-size:1.8rem; font-weight:800; color:var(--mint); }
.ecosistema-landing .stat-label { font-size:.82rem; color:#a0b8cc; margin-top:.2rem; font-weight:500; }
.ecosistema-landing section { padding:6rem 4rem; }
.ecosistema-landing .section-tag { display:inline-block; color:var(--mint); font-size:.78rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; margin-bottom:1rem; }
.ecosistema-landing h2 { font-family: 'Segoe UI', system-ui, sans-serif; font-size:2.8rem; font-weight:800; line-height:1.12; margin-bottom:1rem; letter-spacing:-.02em; }
.ecosistema-landing .section-sub { color:var(--gray); font-size:1rem; line-height:1.75; max-width:560px; margin-bottom:3rem; font-weight:400; }
.ecosistema-landing .dolor-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; }
.ecosistema-landing .dolor-card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:1.8rem; transition:.25s; }
.ecosistema-landing .dolor-card:hover { border-color:var(--mint); transform:translateY(-3px); }
.ecosistema-landing .dolor-icon { font-size:1.8rem; margin-bottom:1rem; }
.ecosistema-landing .dolor-title { font-family: 'Segoe UI', system-ui, sans-serif; font-weight:700; font-size:1rem; margin-bottom:.6rem; }
.ecosistema-landing .dolor-text { color:var(--gray); font-size:.9rem; line-height:1.65; }
.ecosistema-landing .dolor-badge { display:inline-block; margin-top:.9rem; background:rgba(239,68,68,0.14); color:#fca5a5; border:1px solid rgba(239,68,68,0.25); border-radius:2rem; padding:.25rem .8rem; font-size:.78rem; font-weight:600; }
.ecosistema-landing .flujo-section { background:var(--navy2); }
.ecosistema-landing .flujo-steps { display:flex; align-items:stretch; margin-top:1rem; }
.ecosistema-landing .flujo-step { flex:1; background:var(--card); border:1px solid var(--border); padding:2rem 1.5rem; transition:.25s; }
.ecosistema-landing .flujo-step:first-child { border-radius:16px 0 0 16px; }
.ecosistema-landing .flujo-step:last-child { border-radius:0 16px 16px 0; }
.ecosistema-landing .flujo-step:hover { background:#252d38; border-color:var(--mint); z-index:2; position:relative; }
.ecosistema-landing .flujo-num { font-family: 'Segoe UI', system-ui, sans-serif; font-size:2.5rem; font-weight:800; color:rgba(216,155,69,0.16); margin-bottom:.8rem; line-height:1; }
.ecosistema-landing .flujo-icon { font-size:1.6rem; margin-bottom:.7rem; }
.ecosistema-landing .flujo-title { font-family: 'Segoe UI', system-ui, sans-serif; font-weight:700; font-size:.95rem; margin-bottom:.5rem; color:var(--mint); }
.ecosistema-landing .flujo-desc { color:var(--gray); font-size:.84rem; line-height:1.65; }
.ecosistema-landing .flujo-who { display:inline-block; margin-top:.8rem; background:rgba(216,155,69,0.12); color:var(--mint); border-radius:2rem; padding:.2rem .75rem; font-size:.76rem; font-weight:600; }
.ecosistema-landing .arrow-connector { display:flex; align-items:center; justify-content:center; width:28px; flex-shrink:0; color:var(--mint); font-size:1.1rem; background:var(--navy2); }
.ecosistema-landing .tabla-wrap { overflow-x:auto; border-radius:16px; border:1px solid var(--border); }
.ecosistema-landing table { width:100%; border-collapse:collapse; }
.ecosistema-landing thead tr { background:rgba(216,155,69,0.08); }
.ecosistema-landing th { padding:1.1rem 1.4rem; text-align:left; font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; font-size:.85rem; font-weight:700; color:var(--gray); border-bottom:1px solid var(--border); }
.ecosistema-landing th.col-ecosistema { color:var(--mint); }
.ecosistema-landing .feature-width { width:23%; }
.ecosistema-landing td { padding:.95rem 1.4rem; font-size:.88rem; line-height:1.55; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:top; color:var(--gray); font-weight:400; }
.ecosistema-landing td.feature { color:var(--white); font-weight:600; }
.ecosistema-landing td.col-no { color:#8fb3d0; }
.ecosistema-landing td.col-parcial { color:#fbbf24; font-weight:500; }
.ecosistema-landing td.col-si { color:var(--mint); font-weight:600; }
.ecosistema-landing tr:last-child td { border-bottom:none; }
.ecosistema-landing tr:hover td { background:rgba(255,255,255,0.018); }
.ecosistema-landing .col-ecosistema-cell { background:rgba(216,155,69,0.06); }
.ecosistema-landing .ventajas-section { padding-top:0; }
.ecosistema-landing .ventajas-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1.2rem; }
.ecosistema-landing .ventaja-card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:1.5rem; transition:.2s; }
.ecosistema-landing .ventaja-card:hover { border-color:var(--mint); }
.ecosistema-landing .ventaja-icon { font-size:1.5rem; margin-bottom:.8rem; }
.ecosistema-landing .ventaja-title { font-family: 'Segoe UI', system-ui, sans-serif; font-weight:700; font-size:.9rem; margin-bottom:.4rem; }
.ecosistema-landing .ventaja-desc { color:var(--gray); font-size:.84rem; line-height:1.65; }
.ecosistema-landing .impl-section { background:var(--navy2); }
.ecosistema-landing .impl-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; }
.ecosistema-landing .impl-card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:2rem; text-align:center; }
.ecosistema-landing .impl-card.highlight { border-color:var(--mint); background:rgba(216,155,69,0.08); }
.ecosistema-landing .impl-label { font-size:.75rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#a0b8cc; margin-bottom:.8rem; }
.ecosistema-landing .impl-time { font-family: 'Segoe UI', system-ui, sans-serif; font-size:2.4rem; font-weight:800; color:var(--mint); margin-bottom:.6rem; }
.ecosistema-landing .impl-warning { color:#fbbf24; }
.ecosistema-landing .impl-desc { color:var(--gray); font-size:.88rem; line-height:1.65; }
.ecosistema-landing .impl-bad { color:#f87171; }
.ecosistema-landing .proceso-section { background:var(--navy); position:relative; overflow:hidden; }
.ecosistema-landing .proceso-section::before {
  content:'';
  position:absolute; top:8%; right:-160px;
  width:420px; height:420px;
  background:radial-gradient(circle, rgba(216,155,69,0.10) 0%, transparent 68%);
  pointer-events:none;
}
.ecosistema-landing .proceso-grid {
  position:relative;
  z-index:2;
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:1.4rem;
  margin-top:1rem;
}
.ecosistema-landing .proceso-card {
  position:relative;
  background:linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.01)), var(--card);
  border:1px solid var(--border);
  border-radius:18px;
  padding:2rem 1.5rem;
  min-height:230px;
  transition:.25s;
}
.ecosistema-landing .proceso-card:hover { border-color:var(--mint); transform:translateY(-4px); }
.ecosistema-landing .proceso-num {
  font-family:'Segoe UI', system-ui, sans-serif;
  font-size:2.6rem;
  line-height:1;
  font-weight:800;
  color:rgba(216,155,69,0.22);
  margin-bottom:1rem;
}
.ecosistema-landing .proceso-icon { font-size:2rem; margin-bottom:.85rem; }
.ecosistema-landing .proceso-title {
  font-family:'Segoe UI', system-ui, sans-serif;
  font-size:1.05rem;
  line-height:1.25;
  font-weight:800;
  color:var(--white);
  margin-bottom:.65rem;
}
.ecosistema-landing .proceso-desc { color:var(--gray); font-size:.88rem; line-height:1.65; }
.ecosistema-landing .proceso-card.highlight { border-color:var(--mint); background:rgba(216,155,69,0.07); }
.ecosistema-landing .proceso-line {
  position:absolute;
  top:3.1rem;
  left:4.6rem;
  right:-1.4rem;
  height:1px;
  background:linear-gradient(90deg, var(--border), transparent);
}
.ecosistema-landing .proceso-card:last-child .proceso-line { display:none; }
.ecosistema-landing .pasos-section {
  background: linear-gradient(135deg, #101418 0%, #171c22 50%, #101418 100%);
  position:relative; overflow:hidden;
  text-align:center;
}
.ecosistema-landing .pasos-section::before {
  content:'';
  position:absolute; top:0; left:0; right:0; bottom:0;
  background:radial-gradient(ellipse at center, rgba(216,155,69,0.10) 0%, transparent 65%);
  pointer-events:none;
}
.ecosistema-landing .over-glow { position:relative; z-index:2; }
.ecosistema-landing .pasos-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1.4rem; max-width:1120px; margin:0 auto 3rem; position:relative; z-index:2; }
.ecosistema-landing .paso-card { background:var(--card); border:1px solid var(--border); border-radius:20px; padding:2.2rem 1.5rem; text-align:center; transition:.3s; }
.ecosistema-landing .paso-card:hover { border-color:var(--mint); transform:translateY(-4px); }
.ecosistema-landing .paso-card.highlight { border-color:var(--mint); background:rgba(216,155,69,0.08); }
.ecosistema-landing .paso-num { font-family: 'Segoe UI', system-ui, sans-serif; font-size:3rem; font-weight:800; color:var(--mint); opacity:.3; margin-bottom:.5rem; }
.ecosistema-landing .paso-icon-big { font-size:2.5rem; margin-bottom:1rem; }
.ecosistema-landing .paso-title { font-family: 'Segoe UI', system-ui, sans-serif; font-weight:800; font-size:1.2rem; margin-bottom:.6rem; }
.ecosistema-landing .paso-desc { color:var(--gray); font-size:.9rem; line-height:1.65; }
.ecosistema-landing .paso-date { display:inline-block; margin-top:1rem; background:rgba(216,155,69,0.16); color:var(--mint); border-radius:2rem; padding:.3rem 1rem; font-size:.82rem; font-weight:700; }
.ecosistema-landing .rocket-container {
  position:relative; z-index:2;
  display:flex; flex-direction:column; align-items:center;
  margin-top:1rem; margin-bottom:3rem;
}
.ecosistema-landing .rocket-wrap { position:relative; width:80px; height:160px; animation: ecosistemaRocketLaunch 3s ease-in-out infinite; }
@keyframes ecosistemaRocketLaunch {
  0%   { transform: translateY(0px) rotate(0deg); }
  20%  { transform: translateY(-8px) rotate(-1deg); }
  40%  { transform: translateY(-20px) rotate(1deg); }
  60%  { transform: translateY(-12px) rotate(-0.5deg); }
  80%  { transform: translateY(-25px) rotate(0.5deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}
.ecosistema-landing .rocket-svg { width:80px; filter: drop-shadow(0 0 20px rgba(216,155,69,0.55)); }
.ecosistema-landing .flame {
  position:absolute; bottom:-18px; left:50%; transform:translateX(-50%);
  width:24px; height:40px;
  background:linear-gradient(to bottom, #d89b45, #b87333, #fbbf24, transparent);
  border-radius:50% 50% 70% 70%;
  animation:ecosistemaFlamePulse 0.15s ease-in-out infinite alternate;
  filter:blur(3px);
}
.ecosistema-landing .flame2 {
  position:absolute; bottom:-10px; left:50%; transform:translateX(-50%);
  width:14px; height:25px;
  background:linear-gradient(to bottom, white, #d89b45, transparent);
  border-radius:50% 50% 70% 70%;
  animation:ecosistemaFlamePulse2 0.12s ease-in-out infinite alternate;
  filter:blur(1px);
}
@keyframes ecosistemaFlamePulse { from{height:38px;opacity:.9;} to{height:48px;opacity:1;} }
@keyframes ecosistemaFlamePulse2 { from{height:22px;} to{height:32px;} }
.ecosistema-landing .stars {
  position:absolute; top:0; left:50%; transform:translateX(-50%);
  width:200px; height:160px; pointer-events:none;
}
.ecosistema-landing .star {
  position:absolute; width:3px; height:3px; border-radius:50%;
  background:var(--mint); opacity:0;
  animation:ecosistemaStarAppear 2s ease-in-out infinite;
}
.ecosistema-landing .star:nth-child(1) { top:20%; left:10%; animation-delay:0s; }
.ecosistema-landing .star:nth-child(2) { top:10%; left:70%; animation-delay:.3s; }
.ecosistema-landing .star:nth-child(3) { top:40%; left:85%; animation-delay:.6s; }
.ecosistema-landing .star:nth-child(4) { top:60%; left:15%; animation-delay:.9s; }
.ecosistema-landing .star:nth-child(5) { top:30%; left:50%; animation-delay:1.2s; }
.ecosistema-landing .star:nth-child(6) { top:70%; left:60%; animation-delay:1.5s; }
@keyframes ecosistemaStarAppear {
  0%{opacity:0;transform:scale(0)}
  50%{opacity:1;transform:scale(1)}
  100%{opacity:0;transform:scale(0)}
}
.ecosistema-landing .rocket-tagline { font-family: 'Segoe UI', system-ui, sans-serif; font-size:1.1rem; font-weight:700; color:var(--mint); margin-top:1.5rem; letter-spacing:.05em; }
.ecosistema-landing footer { text-align:center; padding:2rem; color:#a0b8cc; font-size:.82rem; border-top:1px solid var(--border); }
@media(max-width:1100px) {
  .ecosistema-landing .hero-visual { opacity:.22; right:1.5rem; width:min(58vw, 420px); }
}
@media(max-width:900px) {
  .ecosistema-landing nav { padding:1rem 1.5rem; }
  .ecosistema-landing nav ul { display:none; }
  .ecosistema-landing h1 { font-size:2.6rem; }
  .ecosistema-landing section { padding:4rem 1.5rem; }
  .ecosistema-landing .hero { padding:7rem 1.5rem 3rem; }
  .ecosistema-landing .hero-visual { display:none; }
  .ecosistema-landing .dolor-grid,.ecosistema-landing .ventajas-grid,.ecosistema-landing .impl-grid,.ecosistema-landing .proceso-grid,.ecosistema-landing .pasos-grid { grid-template-columns:1fr; }
  .ecosistema-landing .flujo-steps { flex-direction:column; }
  .ecosistema-landing .flujo-step:first-child { border-radius:16px 16px 0 0; }
  .ecosistema-landing .flujo-step:last-child { border-radius:0 0 16px 16px; }
  .ecosistema-landing .arrow-connector { display:none; }
  .ecosistema-landing .proceso-line { display:none; }
  .ecosistema-landing .hero-stats { flex-direction:column; gap:1.2rem; }
}
`;

export function LandingPage() {
  return (
    <main className="ecosistema-landing">
      <style>{landingStyles}</style>

      <nav>
        <div className="logo">Ecosistema<span> Notarial</span></div>
        <ul>
          <li><a href="#dolores">El problema</a></li>
          <li><a href="#flujo">Cómo funciona</a></li>
          <li><a href="#comparativa">Comparativa</a></li>
          <li><a href="#proceso-implementacion">Implementación</a></li>
          <li><a href="#pasos">Próximos pasos</a></li>
        </ul>
        <a className="nav-btn" href="/login">Iniciar sesión →</a>
      </nav>

      <section className="hero">
        <img
          className="hero-visual"
          src="/images/ecosistema-notarial-hero.png"
          alt="Ecosistema Notarial con sello Notarías de Colombia y documentos notariales"
        />
        <div className="hero-glow" />
        <div className="hero-content">
          <div className="badge"><span className="badge-dot" /> Plataforma notarial de nueva generación</div>
          <div className="listening-claim">Construido escuchando a las notarías colombianas</div>
          <h1>La notaría del futuro,<br />operando <em>hoy.</em></h1>
          <p className="hero-sub">Ecosistema Notarial digitaliza cada acto notarial con IA: escrituras, poderes, permisos y declaraciones. Sin etiquetado manual, sin plantillas rígidas, con las plantillas que cada notaría ya usa.</p>
          <div className="hero-btns">
            <a className="btn-primary" href="/login">Iniciar sesión →</a>
            <a className="btn-secondary" href="#flujo">Cómo funciona</a>
          </div>
          <div className="hero-stats">
            <div><div className="stat-val">−80%</div><div className="stat-label">tiempo por minuta</div></div>
            <div><div className="stat-val">5–8 min</div><div className="stat-label">minuta compleja</div></div>
            <div><div className="stat-val">20 min</div><div className="stat-label">implementación por persona</div></div>
          </div>
        </div>
      </section>

      <section id="dolores">
        <div className="section-tag">El problema hoy</div>
        <h2>Así trabaja hoy<br />un protocolista</h2>
        <p className="section-sub">Trabajo repetitivo, agotador y propenso a errores — que el Ecosistema Notarial resuelve.</p>
        <div className="dolor-grid">
          <div className="dolor-card">
            <div className="dolor-icon">⏱️</div>
            <div className="dolor-title">35–45 min por minuta</div>
            <div className="dolor-text">Busca dato por dato, copia el nombre 7–10 veces, escribe valores en letras a mano. Al final del día: 8–10 minutas y la jornada agotada.</div>
            <span className="dolor-badge">Tiempo perdido</span>
          </div>
          <div className="dolor-card">
            <div className="dolor-icon">⚠️</div>
            <div className="dolor-title">Errores de género y concordancia</div>
            <div className="dolor-text">Un "domiciliado" donde debía decir "domiciliada". Un valor en millones mal escrito. El error se detecta cuando el documento ya está firmado.</div>
            <span className="dolor-badge">Error costoso</span>
          </div>
          <div className="dolor-card">
            <div className="dolor-icon">🔁</div>
            <div className="dolor-title">Trabajo 100% repetitivo</div>
            <div className="dolor-text">No requiere criterio jurídico — solo copiar, pegar y cambiar datos. Carga laboral insostenible y horas extras para cumplir el volumen del día.</div>
            <span className="dolor-badge">Desmotivador</span>
          </div>
          <div className="dolor-card">
            <div className="dolor-icon">👤</div>
            <div className="dolor-title">Dependencia de quien "sabe"</div>
            <div className="dolor-text">Si la persona que conoce las plantillas falta, la operación se paraliza. Sin trazabilidad — nadie sabe quién hizo qué ni cuándo.</div>
            <span className="dolor-badge">Riesgo operativo</span>
          </div>
          <div className="dolor-card">
            <div className="dolor-icon">🏷️</div>
            <div className="dolor-title">Plantillas rígidas o etiquetado manual</div>
            <div className="dolor-text">Cuando el sistema exige marcar campos manualmente, cada plantilla toma tiempo adicional y un error en el etiquetado puede afectar todas las minutas generadas.</div>
            <span className="dolor-badge">Arranque lento</span>
          </div>
          <div className="dolor-card">
            <div className="dolor-icon">📁</div>
            <div className="dolor-title">Sin historial ni versiones</div>
            <div className="dolor-text">Las minutas viven en carpetas del PC. No hay versiones, no hay trazabilidad, no hay forma de saber qué cambió entre una versión y otra.</div>
            <span className="dolor-badge">Sin control</span>
          </div>
        </div>
      </section>

      <section id="flujo" className="flujo-section">
        <div className="section-tag">Cómo funciona</div>
        <h2>5 pasos. De documento<br />a minuta lista.</h2>
        <p className="section-sub">El protocolista supervisa y valida. La IA detecta, analiza y genera.</p>
        <div className="flujo-steps">
          <div className="flujo-step">
            <div className="flujo-num">01</div>
            <div className="flujo-icon">📄</div>
            <div className="flujo-title">Escoger plantilla propia de biblioteca</div>
            <div className="flujo-desc">Selecciona una plantilla propia guardada en la biblioteca notarial. El protocolista parte de documentos reales de la notaría, sin etiquetas ni preparación previa.</div>
            <span className="flujo-who">Protocolista</span>
          </div>
          <div className="arrow-connector">→</div>
          <div className="flujo-step">
            <div className="flujo-num">02</div>
            <div className="flujo-icon">🤖</div>
            <div className="flujo-title">IA analiza y detecta</div>
            <div className="flujo-desc">La IA lee el documento y detecta automáticamente personas, roles, valores, inmueble y notaría. Confianza del análisis en tiempo real.</div>
            <span className="flujo-who">IA</span>
          </div>
          <div className="arrow-connector">→</div>
          <div className="flujo-step">
            <div className="flujo-num">03</div>
            <div className="flujo-icon">📝</div>
            <div className="flujo-title">Formulario dinámico</div>
            <div className="flujo-desc">El protocolista revisa y completa. Género, nacionalidad y estado civil se ajustan automáticamente en cascada. Valores en letras al digitar.</div>
            <span className="flujo-who">IA + Protocolista</span>
          </div>
          <div className="arrow-connector">→</div>
          <div className="flujo-step">
            <div className="flujo-num">04</div>
            <div className="flujo-icon">⚡</div>
            <div className="flujo-title">Generar</div>
            <div className="flujo-desc">La IA reemplaza datos, aplica concordancia de género por persona, escribe valores en letras y genera el documento final en segundos.</div>
            <span className="flujo-who">IA</span>
          </div>
          <div className="arrow-connector">→</div>
          <div className="flujo-step">
            <div className="flujo-num">05</div>
            <div className="flujo-icon">✅</div>
            <div className="flujo-title">Verificar y ajustar</div>
            <div className="flujo-desc">Abre en el editor integrado. Revisa, comenta, ajusta y descarga el .docx listo para firma — sin salir del sistema.</div>
            <span className="flujo-who">Protocolista + Notario</span>
          </div>
        </div>
      </section>

      <section id="comparativa">
        <div className="section-tag">Evolución</div>
        <h2>Sin sistema → proceso rígido → Ecosistema Notarial</h2>
        <p className="section-sub">Construido escuchando a las notarías colombianas — con foco en lo que realmente necesita la operación diaria.</p>
        <div className="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th className="feature-width">Característica</th>
                <th>Sin sistema</th>
                <th>Proceso rígido</th>
                <th className="col-ecosistema">Ecosistema Notarial ✦</th>
              </tr>
            </thead>
            <tbody>
              <tr><td className="feature">Tiempo por minuta</td><td className="col-no">35–45 min</td><td className="col-parcial">20–25 min + 15 min etiquetado</td><td className="col-si col-ecosistema-cell">5–8 min</td></tr>
              <tr><td className="feature">Modo B1 — Plantilla en blanco</td><td className="col-no">Manual 100%</td><td className="col-parcial">Requiere etiquetado previo</td><td className="col-si col-ecosistema-cell">Sube su plantilla, usa desde el primer día</td></tr>
              <tr><td className="feature">Modo B2 — Documento diligenciado</td><td className="col-no">Copia y pega dato por dato</td><td className="col-no">No soportado</td><td className="col-si col-ecosistema-cell">IA detecta datos y genera formulario dinámico</td></tr>
              <tr><td className="feature">Etiquetado en Word</td><td className="col-no">No aplica</td><td className="col-no">Marcadores manuales — error = falla en todo</td><td className="col-si col-ecosistema-cell">Word limpio — sin etiquetas ni marcadores</td></tr>
              <tr><td className="feature">Detección de personas y roles</td><td className="col-no">Manual</td><td className="col-parcial">Plantilla fija etiquetada</td><td className="col-si col-ecosistema-cell">IA detecta automático</td></tr>
              <tr><td className="feature">Género y concordancia</td><td className="col-no">Manual — errores frecuentes</td><td className="col-parcial">Parcial</td><td className="col-si col-ecosistema-cell">Automático por persona</td></tr>
              <tr><td className="feature">Nacionalidad automática</td><td className="col-no">No</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — 25 gentilicios en cascada</td></tr>
              <tr><td className="feature">Valores en letras</td><td className="col-no">A mano — error frecuente</td><td className="col-no">A mano</td><td className="col-si col-ecosistema-cell">Tiempo real al digitar el número</td></tr>
              <tr><td className="feature">Editor dentro del sistema</td><td className="col-no">Word externo</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — edita sin salir del Ecosistema Notarial</td></tr>
              <tr><td className="feature">Comentarios y notas</td><td className="col-no">No</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — dentro del documento</td></tr>
              <tr><td className="feature">Chat de revisión</td><td className="col-no">WhatsApp / llamada</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — protocolista y notario en tiempo real</td></tr>
              <tr><td className="feature">Guardar y continuar después</td><td className="col-no">No</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — retoma donde quedó</td></tr>
              <tr><td className="feature">Versiones del documento</td><td className="col-no">No</td><td className="col-no">No</td><td className="col-si col-ecosistema-cell">Sí — historial completo</td></tr>
              <tr><td className="feature">Plantillas más usadas</td><td className="col-no">Carpeta en el PC</td><td className="col-parcial">Guardadas pero etiquetadas</td><td className="col-si col-ecosistema-cell">Guardadas limpias, listas para usar</td></tr>
              <tr><td className="feature">Implementación</td><td className="col-no">Sin sistema</td><td className="col-no">2 semanas + curva de aprendizaje</td><td className="col-si col-ecosistema-cell">20 minutos por persona</td></tr>
              <tr><td className="feature">Carga del protocolista</td><td className="col-no">Alta — repetitivo y agotador</td><td className="col-parcial">Media — más pasos</td><td className="col-si col-ecosistema-cell">Baja — supervisa y valida</td></tr>
              <tr><td className="feature">Errores post-firma</td><td className="col-no">Frecuentes</td><td className="col-parcial">Ocasionales + riesgo etiquetado</td><td className="col-si col-ecosistema-cell">Mínimos</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="ventajas-section">
        <div className="section-tag">Editor integrado</div>
        <h2>Todo en un solo lugar</h2>
        <p className="section-sub">El editor de documentos dentro del Ecosistema Notarial — sin necesidad de Word externo.</p>
        <div className="ventajas-grid">
          <div className="ventaja-card"><div className="ventaja-icon">✏️</div><div className="ventaja-title">Edición completa</div><div className="ventaja-desc">Formato Word completo — negritas, tablas, márgenes — directamente en el navegador.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">💬</div><div className="ventaja-title">Comentarios y chat</div><div className="ventaja-desc">Protocolista y notario revisan juntos con comentarios en el documento y chat integrado.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">🕓</div><div className="ventaja-title">Versiones e historial</div><div className="ventaja-desc">Cada cambio queda registrado. Vuelve a cualquier versión anterior con un clic.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">💾</div><div className="ventaja-title">Guarda y retoma</div><div className="ventaja-desc">Guarda el borrador y continúa después — sin perder nada, desde cualquier dispositivo.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">📚</div><div className="ventaja-title">Plantillas guardadas</div><div className="ventaja-desc">Las plantillas más usadas quedan limpias y listas — sin buscar en carpetas del PC.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">📥</div><div className="ventaja-title">Descarga directa</div><div className="ventaja-desc">Descarga el .docx final listo para imprimir y firmar, en un clic.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">🔒</div><div className="ventaja-title">Trazabilidad</div><div className="ventaja-desc">Sabe quién hizo qué y cuándo. Auditoría completa de cada minuta generada.</div></div>
          <div className="ventaja-card"><div className="ventaja-icon">🌐</div><div className="ventaja-title">Sin instalar nada</div><div className="ventaja-desc">100% en el navegador — funciona en cualquier computador de la notaría.</div></div>
        </div>
      </section>

      <section id="implementacion" className="impl-section">
        <div className="section-tag">Implementación</div>
        <h2>De cero a operando<br />en 20 minutos</h2>
        <p className="section-sub">Construido escuchando a las notarías colombianas — con foco en lo que realmente necesita la operación diaria.</p>
        <div className="impl-grid">
          <div className="impl-card"><div className="impl-label">Sin sistema</div><div className="impl-time impl-bad">∞</div><div className="impl-desc">Proceso 100% manual. Sin sistema, sin trazabilidad, sin mejora posible.</div></div>
          <div className="impl-card"><div className="impl-label">Proceso rígido</div><div className="impl-time impl-warning">2 semanas</div><div className="impl-desc">Etiquetado manual de cada plantilla + curva de aprendizaje + riesgo de error.</div></div>
          <div className="impl-card highlight"><div className="impl-label">Ecosistema Notarial ✦</div><div className="impl-time">20 min</div><div className="impl-desc">Por persona. La notaría sube sus propias plantillas. Un ajuste inicial y opera el mismo día.</div></div>
        </div>
      </section>

      <section id="proceso-implementacion" className="proceso-section">
        <div className="section-tag">Proceso de implementación</div>
        <h2>Implementamos con orden,<br />confianza y control</h2>
        <p className="section-sub">Un proceso corto y acompañado para probar con seguridad, proteger la información y preparar el lanzamiento operativo.</p>
        <div className="proceso-grid">
          <div className="proceso-card highlight">
            <div className="proceso-line" />
            <div className="proceso-num">01</div>
            <div className="proceso-icon">🤝</div>
            <div className="proceso-title">Reunión de presentación</div>
            <div className="proceso-desc">Presentamos el alcance del Ecosistema Notarial, resolvemos inquietudes y alineamos expectativas con el equipo de la notaría.</div>
          </div>
          <div className="proceso-card">
            <div className="proceso-line" />
            <div className="proceso-num">02</div>
            <div className="proceso-icon">🔐</div>
            <div className="proceso-title">Envío de acuerdo de confidencialidad</div>
            <div className="proceso-desc">Formalizamos la protección de la información, documentos, plantillas y datos que se usen durante la prueba.</div>
          </div>
          <div className="proceso-card">
            <div className="proceso-line" />
            <div className="proceso-num">03</div>
            <div className="proceso-icon">🗺️</div>
            <div className="proceso-title">Creación del plan de pruebas e implementación</div>
            <div className="proceso-desc">Definimos en conjunto plantillas, usuarios, casos de prueba, tiempos, responsables y criterios de validación.</div>
          </div>
          <div className="proceso-card highlight">
            <div className="proceso-num">04</div>
            <div className="proceso-icon">🚀</div>
            <div className="proceso-title">Lanzamiento Día D a la Hora H</div>
            <div className="proceso-desc">Arrancamos la operación controlada en la fecha y hora acordadas, con acompañamiento para asegurar adopción y ajustes rápidos.</div>
          </div>
        </div>
      </section>

      <section id="pasos" className="pasos-section">
        <div className="section-tag over-glow">Próximos pasos</div>
        <h2 className="over-glow">Listos para<br /><em>despegar juntos</em></h2>
        <div className="rocket-container">
          <div className="rocket-wrap">
            <div className="stars">
              <div className="star" /><div className="star" /><div className="star" />
              <div className="star" /><div className="star" /><div className="star" />
            </div>
            <svg className="rocket-svg" viewBox="0 0 80 160" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M40 8C40 8 20 30 18 70H62C60 30 40 8 40 8Z" fill="#d89b45" />
              <path d="M40 8C40 8 30 30 29 70H40V8Z" fill="#b87333" />
              <rect x="18" y="68" width="44" height="50" rx="4" fill="#242a33" stroke="#d89b45" strokeWidth="1.5" />
              <circle cx="40" cy="88" r="12" fill="#101418" stroke="#d89b45" strokeWidth="2" />
              <circle cx="40" cy="88" r="7" fill="#d89b45" opacity="0.3" />
              <circle cx="40" cy="88" r="4" fill="#d89b45" />
              <path d="M18 80L6 100L18 95Z" fill="#b87333" />
              <path d="M62 80L74 100L62 95Z" fill="#b87333" />
              <path d="M28 118L22 140L32 132L40 148L48 132L58 140L52 118Z" fill="#242a33" stroke="#d89b45" strokeWidth="1" />
            </svg>
            <div className="flame" />
            <div className="flame2" />
          </div>
          <div className="rocket-tagline">¡Listos para el lanzamiento!</div>
        </div>
        <div className="pasos-grid">
          <div className="paso-card highlight">
            <div className="paso-num">01</div>
            <div className="paso-icon-big">🎯</div>
            <div className="paso-title">Demo en vivo MVP</div>
            <div className="paso-desc">Mostramos el MVP funcionando con documentos reales y validamos el flujo completo de generación de minutas.</div>
            <span className="paso-date">Validación inicial</span>
          </div>
          <div className="paso-card highlight">
            <div className="paso-num">02</div>
            <div className="paso-icon-big">👩‍💼</div>
            <div className="paso-title">Uso con un protocolista</div>
            <div className="paso-desc">Un protocolista prueba el sistema en operación guiada, usando plantillas y casos reales de la notaría.</div>
            <span className="paso-date">Prueba operativa</span>
          </div>
          <div className="paso-card">
            <div className="paso-num">03</div>
            <div className="paso-icon-big">📝</div>
            <div className="paso-title">Recepción de recomendaciones</div>
            <div className="paso-desc">Recibimos observaciones del equipo: ajustes de flujo, campos, formatos, experiencia de uso y controles necesarios.</div>
            <span className="paso-date">Retroalimentación</span>
          </div>
          <div className="paso-card">
            <div className="paso-num">04</div>
            <div className="paso-icon-big">🔧</div>
            <div className="paso-title">Entrega de recomendaciones y ajuste</div>
            <div className="paso-desc">Consolidamos las recomendaciones, priorizamos cambios y entregamos una versión ajustada para avanzar con seguridad.</div>
            <span className="paso-date">Ajustes priorizados</span>
          </div>
        </div>
        <a className="btn-primary final-cta" href="/login">¿Cuándo comenzamos? →</a>
        <div className="final-listening">Construido escuchando a las notarías colombianas</div>
      </section>

      <footer>
        Ecosistema Notarial — Plataforma notarial de nueva generación
      </footer>
    </main>
  );
}
