/**
 * Login handler — Node.js puro (cold start < 200ms vs 10-15s Python).
 * Usa apenas módulos built-in: crypto, https.
 * Compatível com hashes PBKDF2 gerados pelo backend Python anterior.
 */
"use strict";

const crypto = require("crypto");
const https  = require("https");

// ── Dados ─────────────────────────────────────────────────────────────────────

const SENHAS = { lider: "lider2026", admin: "admin2026", head: "head2026" };

const ASSESSORES = {
  A74621: "Lucas Landroni Cozzi",
  A68983: "Tatiane Cristina da Silva Cecchetti",
  A27157: "Felipe Fraga",
  A34003: "Bruno Seiji Ito",
  A74329: "Matheus Escoza Milani",
  A25261: "Alex Alves dos Santos",
  A53115: "Flavia Guedes de Souza",
  A55932: "Carolina Custodio Siqueira",
  A74638: "Andre Guilherme Leite Figueiredo",
  A22930: "Carlos Fernando Victor Bolivar Moreira Neto",
  A67952: "Giuseppe Hilario Neto",
  A72679: "Paulo Roberto Negreiros Sobrinho",
  A26364: "Felipe Santos Nishio",
  A56767: "Michael Ademilson Santos da Silva",
  A38890: "Marcelo Ramos Dias",
  A22075: "Denis Kinoshita",
};

// ── Upstash KV (via REST API) ─────────────────────────────────────────────────

function kvRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const url  = (process.env.KV_REST_API_URL || "").replace(/\/$/, "");
    const tok  = process.env.KV_REST_API_TOKEN || "";
    if (!url || !tok) { resolve(null); return; }

    const parsed = new URL(url + path);
    const opts = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method,
      headers: { Authorization: `Bearer ${tok}`, "Content-Type": "application/json" },
    };
    const payload = body ? JSON.stringify(body) : undefined;
    if (payload) opts.headers["Content-Length"] = Buffer.byteLength(payload);

    const req = https.request(opts, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(null); }
      });
    });
    req.on("error", () => resolve(null));
    if (payload) req.write(payload);
    req.end();
  });
}

function kvKey(name) { return `brauna:${name}`; }

async function kvGet(name) {
  const res = await kvRequest("GET", `/get/${kvKey(name)}`);
  if (res && res.result !== undefined) {
    const v = res.result;
    try { return typeof v === "string" ? JSON.parse(v) : v; }
    catch { return v; }
  }
  return null;
}

async function kvSet(name, data) {
  const payload = JSON.stringify(data);
  await kvRequest("POST", "", ["SET", kvKey(name), payload]);
}

async function loadSenhasPessoais() {
  const v = await kvGet("senhas_pessoais");
  return v || {};
}
async function saveSenhasPessoais(d) { await kvSet("senhas_pessoais", d); }
async function loadResetTokens() {
  const v = await kvGet("reset_tokens");
  return v || {};
}
async function saveResetTokens(d) { await kvSet("reset_tokens", d); }

// ── Senhas ────────────────────────────────────────────────────────────────────

function hashSenha(senha) {
  const salt = crypto.randomBytes(16).toString("hex");
  const h = crypto.pbkdf2Sync(senha, Buffer.from(salt, "hex"), 100000, 32, "sha256").toString("hex");
  return `${salt}$${h}`;
}

function verificaSenha(senha, guardado) {
  try {
    const [salt, h] = guardado.split("$");
    const calc = crypto.pbkdf2Sync(senha, Buffer.from(salt, "hex"), 100000, 32, "sha256").toString("hex");
    return crypto.timingSafeEqual(Buffer.from(calc, "hex"), Buffer.from(h, "hex"));
  } catch { return false; }
}

function entryHash(entry) {
  if (entry && typeof entry === "object") return entry.hash || "";
  return entry || "";
}

// ── HTML ──────────────────────────────────────────────────────────────────────

const HTML_RESET = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Braúna — Redefinir Senha</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#081F18;font-family:'Segoe UI',system-ui,sans-serif;color:#F0F0F0}
body{display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.card{background:#111;border:1px solid #1A4030;border-radius:16px;padding:36px 32px;width:100%;max-width:400px}
.logo{text-align:center;margin-bottom:28px}
.logo-title{font-size:20px;font-weight:800;color:#C9A96E;letter-spacing:2px}
.logo-sub{font-size:11px;color:#3A6A48;margin-top:4px}
h2{font-size:15px;color:#F0F0F0;margin-bottom:6px}
p.desc{font-size:12px;color:#3A6A48;margin-bottom:22px;line-height:1.5}
label{font-size:11px;color:#3A6A48;display:block;margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px}
input{width:100%;background:#0B2A1F;border:1px solid #1A4030;border-radius:8px;padding:11px 14px;color:#F0F0F0;font-size:14px;outline:none;margin-bottom:14px;transition:border-color .2s}
input:focus{border-color:#C9A96E}
.btn{width:100%;background:#C9A96E;color:#081F18;border:none;border-radius:10px;padding:13px;font-size:14px;font-weight:700;cursor:pointer;transition:opacity .2s}
.btn:hover{opacity:.85}.btn:disabled{opacity:.4;cursor:not-allowed}
.msg{font-size:12px;margin-top:12px;text-align:center;min-height:18px}
.msg.ok{color:#5DCAA5}.msg.err{color:#FF6B6B}
.back{display:block;text-align:center;margin-top:18px;font-size:12px;color:#3A6A48;text-decoration:none}
.back:hover{color:#C9A96E}
.spin{display:inline-block;width:16px;height:16px;border:2px solid #081F18;border-top-color:transparent;border-radius:50%;animation:sp .7s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="card" id="card">
  <div class="logo">
    <div class="logo-title">BRAÚNA INVESTIMENTOS</div>
    <div class="logo-sub">Redefinição de senha</div>
  </div>
  <div id="st-loading" style="text-align:center;padding:20px 0">
    <div class="spin" style="width:24px;height:24px;border-color:#C9A96E;border-top-color:transparent;display:inline-block"></div>
    <p style="color:#3A6A48;font-size:13px;margin-top:12px">Verificando link...</p>
  </div>
  <div id="st-invalido" style="display:none;text-align:center;padding:10px 0">
    <div style="font-size:36px;margin-bottom:12px">⚠️</div>
    <h2 style="color:#FF6B6B;margin-bottom:8px">Link inválido ou expirado</h2>
    <p style="font-size:12px;color:#888;line-height:1.5;margin-bottom:20px">Este link de redefinição já foi utilizado ou expirou.<br>Solicite um novo na tela de login.</p>
    <a href="/" class="btn" style="display:block;text-align:center;text-decoration:none;padding:13px">Voltar ao login</a>
  </div>
  <div id="st-form" style="display:none">
    <h2>Olá, <span id="nome-u"></span>!</h2>
    <p class="desc">Escolha uma nova senha para acessar o sistema.</p>
    <div><label>Nova senha</label><input type="password" id="nova-s" placeholder="Mínimo 4 caracteres" minlength="4"></div>
    <div><label>Confirmar senha</label><input type="password" id="conf-s" placeholder="Repita a senha"></div>
    <button class="btn" id="btn-salvar" onclick="salvar()">Salvar nova senha</button>
    <div class="msg" id="msg-form"></div>
  </div>
  <div id="st-sucesso" style="display:none;text-align:center;padding:10px 0">
    <div style="font-size:36px;margin-bottom:12px">✅</div>
    <h2 style="color:#5DCAA5;margin-bottom:8px">Senha redefinida!</h2>
    <p style="font-size:12px;color:#888;margin-bottom:20px">Sua nova senha foi salva com sucesso. Você já pode fazer login.</p>
    <a href="/" class="btn" style="display:block;text-align:center;text-decoration:none;padding:13px">Ir para o login</a>
  </div>
</div>
<script>
let tokenAtual='';
function estado(id){['st-loading','st-invalido','st-form','st-sucesso'].forEach(s=>{document.getElementById(s).style.display=s===id?'block':'none'});}
async function init(){
  const tok=new URLSearchParams(location.search).get('token')||'';
  tokenAtual=tok;
  if(!tok){estado('st-invalido');return;}
  try{
    const r=await fetch('/api/verificar-token-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:tok})});
    const d=await r.json();
    if(d.ok){document.getElementById('nome-u').textContent=d.nome;estado('st-form');}
    else estado('st-invalido');
  }catch{estado('st-invalido');}
}
async function salvar(){
  const btn=document.getElementById('btn-salvar');
  const msg=document.getElementById('msg-form');
  const s1=document.getElementById('nova-s').value;
  const s2=document.getElementById('conf-s').value;
  if(s1.length<4){msg.className='msg err';msg.textContent='A senha precisa ter ao menos 4 caracteres.';return;}
  if(s1!==s2){msg.className='msg err';msg.textContent='As senhas não coincidem.';return;}
  btn.disabled=true;btn.innerHTML='<span class="spin"></span>Salvando...';
  try{
    const r=await fetch('/api/confirmar-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:tokenAtual,senha:s1})});
    const d=await r.json();
    if(d.ok){estado('st-sucesso');}
    else{msg.className='msg err';msg.textContent=d.msg||'Erro ao redefinir senha.';}
  }catch{msg.className='msg err';msg.textContent='Erro de conexão.';}
  finally{btn.disabled=false;btn.textContent='Salvar nova senha';}
}
init();
</script>
</body></html>`;

const HTML_LOGIN = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Braúna Investimentos — Acesso</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#081F18;font-family:'Segoe UI',system-ui,sans-serif;color:#F0F0F0}
body{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.logo-area{text-align:center;margin-bottom:40px}
.logo-title{font-size:28px;font-weight:800;color:#C9A96E;letter-spacing:2px;text-transform:uppercase}
.logo-sub{font-size:13px;color:#2A5A3A;margin-top:6px;letter-spacing:1px}
.logo-line{width:60px;height:2px;background:linear-gradient(to right,transparent,#C9A96E,transparent);margin:14px auto 0}
.roles{display:flex;gap:16px;margin-bottom:36px;flex-wrap:wrap;justify-content:center}
.role-card{width:200px;padding:28px 20px;border-radius:16px;border:1.5px solid #1A4030;background:#111;cursor:pointer;text-align:center;transition:all .25s;position:relative;overflow:hidden}
.role-card:hover{border-color:#C9A96E;transform:translateY(-3px);box-shadow:0 8px 32px rgba(214,178,122,.12)}
.role-card.selected{transform:translateY(-3px)}
.role-card.assessor.selected{border-color:#C9A96E;box-shadow:0 8px 32px rgba(214,178,122,.18);background:#1A2E1A}
.role-card.assessor:hover{border-color:#C9A96E}
.role-card.lider.selected{border-color:#8B9FE8;box-shadow:0 8px 32px rgba(139,159,232,.18);background:#0D0D1F}
.role-card.lider:hover{border-color:#8B9FE8}
.role-card.head.selected{border-color:#D4B483;box-shadow:0 8px 32px rgba(232,201,107,.18);background:#1A1500}
.role-card.head:hover{border-color:#D4B483}
.head .role-check{background:#D4B483;color:#000}
.role-card.admin.selected{border-color:#5DCAA5;box-shadow:0 8px 32px rgba(93,202,165,.18);background:#081410}
.role-card.admin:hover{border-color:#5DCAA5}
.role-icon{font-size:36px;margin-bottom:12px;display:block}
.role-name{font-size:15px;font-weight:700;margin-bottom:4px}
.role-desc{font-size:11px;color:#3A6A48;line-height:1.4}
.role-check{position:absolute;top:10px;right:10px;width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:900;opacity:0;transition:opacity .2s}
.assessor .role-check{background:#C9A96E;color:#000}
.lider .role-check{background:#8B9FE8;color:#000}
.admin .role-check{background:#5DCAA5;color:#000}
.role-card.selected .role-check{opacity:1}
.senha-box{width:100%;max-width:380px;background:#111;border-radius:14px;padding:28px;border:1px solid #1A4030;animation:fadeUp .25s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.senha-label{font-size:11px;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.senha-label span{font-size:16px}
.senha-input-wrap{position:relative;margin-bottom:14px}
.senha-input{width:100%;background:#0A0A0A;border:1.5px solid #1C4A34;border-radius:10px;padding:13px 44px 13px 16px;color:#F0F0F0;font-size:16px;letter-spacing:4px;outline:none;transition:border .2s}
.senha-input::placeholder{letter-spacing:1px;font-size:13px;color:#1E4A30}
.senha-input:focus{border-color:var(--role-color)}
.toggle-pw{position:absolute;right:14px;top:50%;transform:translateY(-50%);background:none;border:none;color:#2A5A3A;cursor:pointer;font-size:16px;padding:0}
.btn-entrar{width:100%;padding:14px;border:none;border-radius:10px;font-size:14px;font-weight:800;cursor:pointer;letter-spacing:.5px;text-transform:uppercase;transition:all .2s;background:var(--role-color);color:#081F18}
.btn-entrar:hover{opacity:.88;transform:translateY(-1px)}
.btn-entrar:disabled{opacity:.3;cursor:not-allowed;transform:none}
.erro-msg{font-size:12px;color:#FF6B6B;text-align:center;margin-top:10px;height:18px;transition:opacity .2s}
.rodape{font-size:11px;color:#1C4A34;margin-top:32px;text-align:center}
</style>
</head>
<body>
<div class="logo-area">
  <div class="logo-title">Braúna Investimentos</div>
  <div class="logo-line"></div>
  <div class="logo-sub">Sistema de Análise de Carteiras</div>
</div>
<div class="roles">
  <div class="role-card assessor" onclick="selRole('assessor')" id="card-assessor">
    <div class="role-check">✓</div><span class="role-icon">📊</span>
    <div class="role-name" style="color:#C9A96E">Assessor</div>
    <div class="role-desc">Análise de carteiras e atendimento ao cliente</div>
  </div>
  <div class="role-card lider" onclick="selRole('lider')" id="card-lider">
    <div class="role-check">✓</div><span class="role-icon">👥</span>
    <div class="role-name" style="color:#8B9FE8">Líder</div>
    <div class="role-desc">Visão da equipe, OKRs e orientação aos assessores</div>
  </div>
  <div class="role-card head" onclick="selRole('head')" id="card-head">
    <div class="role-check">✓</div><span class="role-icon">🏛️</span>
    <div class="role-name" style="color:#D4B483">Head de Produtos</div>
    <div class="role-desc">Portfólios modelo, cenário macro e produtos em destaque</div>
  </div>
  <div class="role-card admin" onclick="selRole('admin')" id="card-admin">
    <div class="role-check">✓</div><span class="role-icon">⚙️</span>
    <div class="role-name" style="color:#5DCAA5">Administração</div>
    <div class="role-desc">Documentos estratégicos, cartas e configurações</div>
  </div>
</div>
<div id="senha-box" style="display:none"></div>
<div id="pessoal-box" style="display:none"></div>
<div id="reset-box" style="display:none"></div>
<p class="rodape">Braúna Investimentos · Uso interno · Acesso restrito</p>

<script>
const ROLES={
  assessor:{color:'#C9A96E',label:'ASSESSOR',icon:'📊',placeholder:'Código do assessor (ex: A74621)',dest:'/menu'},
  lider:{color:'#8B9FE8',label:'LÍDER',icon:'👥',placeholder:'Senha do perfil',dest:'/menu-lider'},
  head:{color:'#D4B483',label:'HEAD DE PRODUTOS',icon:'🏛️',placeholder:'Senha do perfil',dest:'/menu-head'},
  admin:{color:'#5DCAA5',label:'ADMINISTRAÇÃO',icon:'⚙️',placeholder:'Senha do perfil',dest:'/menu-admin'},
};
let roleAtual=null,_sessaoPendente=null;

function selRole(r){
  roleAtual=r;
  document.querySelectorAll('.role-card').forEach(c=>c.classList.remove('selected'));
  document.getElementById('card-'+r).classList.add('selected');
  const info=ROLES[r];
  document.documentElement.style.setProperty('--role-color',info.color);
  document.getElementById('pessoal-box').style.display='none';
  document.getElementById('reset-box').style.display='none';
  document.querySelector('.roles').style.opacity='1';
  document.querySelector('.roles').style.pointerEvents='auto';
  document.getElementById('senha-box').style.display='block';
  document.getElementById('senha-box').innerHTML=\`
    <div class="senha-box" style="--role-color:\${info.color}">
      <div class="senha-label"><span>\${info.icon}</span>\${info.label}</div>
      <div class="senha-input-wrap">
        <input class="senha-input" type="password" id="senha" placeholder="\${info.placeholder}" autocomplete="off">
        <button class="toggle-pw" onclick="toggleSenha()" type="button">👁</button>
      </div>
      <button class="btn-entrar" id="btn-entrar" onclick="continuar()">CONTINUAR</button>
      <div class="erro-msg" id="erro"></div>
    </div>
  \`;
  setTimeout(()=>document.getElementById('senha')?.focus(),50);
  document.getElementById('senha').addEventListener('keydown',e=>{if(e.key==='Enter')continuar();});
}

function toggleSenha(){const i=document.getElementById('senha');i.type=i.type==='password'?'text':'password';}

async function continuar(){
  const btn=document.getElementById('btn-entrar');
  const senha=document.getElementById('senha').value.trim();
  if(!senha){document.getElementById('erro').textContent='Informe o código ou senha.';return;}
  btn.disabled=true;btn.textContent='VERIFICANDO...';
  document.getElementById('erro').textContent='';
  let d=null;
  for(let t=0;t<5;t++){
    try{
      const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:roleAtual,senha})});
      const text=await r.text();
      try{d=JSON.parse(text);}catch{d=null;}
      if(d)break;
    }catch(e){d=null;}
    if(t<4){
      document.getElementById('erro').textContent=\`Servidor iniciando, aguarde... (\${t+1}/5)\`;
      await new Promise(res=>setTimeout(res,2000));
    }
  }
  btn.disabled=false;btn.textContent='CONTINUAR';
  if(!d){document.getElementById('erro').textContent='Serviço indisponível. Recarregue a página e tente novamente.';return;}
  if(d.ok&&d.etapa==='senha_pessoal'){
    _sessaoPendente={role:d.role,nome:d.nome,codigo:d.codigo,identity:d.identity};
    mostrarSenhaPessoal(d.precisa_criar);
  }else{
    document.getElementById('erro').textContent=d.msg||'Credencial inválida. Tente novamente.';
    document.getElementById('senha').value='';
  }
}

function mostrarSenhaPessoal(criar){
  const info=ROLES[roleAtual];
  document.querySelector('.roles').style.opacity='.4';
  document.querySelector('.roles').style.pointerEvents='none';
  document.getElementById('senha-box').style.display='none';
  document.getElementById('pessoal-box').style.display='block';
  document.getElementById('pessoal-box').innerHTML=\`
    <div class="senha-box" style="--role-color:\${info.color}">
      <div class="senha-label" style="margin-bottom:6px"><span>\${info.icon}</span>\${_sessaoPendente.nome}</div>
      \${criar?'<p style="font-size:11px;color:#3A6A48;margin-bottom:14px">Primeiro acesso — crie sua senha pessoal e informe seu e-mail @grupobrauna.com.br.</p>':'<p style="font-size:11px;color:#3A6A48;margin-bottom:14px">Digite sua senha pessoal para entrar.</p>'}
      \${criar?'<label style="font-size:11px;color:#3A6A48;text-transform:uppercase;letter-spacing:.5px">E-mail corporativo</label><div class="senha-input-wrap" style="margin-bottom:14px"><input class="senha-input" type="email" id="email-pessoal" placeholder="nome@grupobrauna.com.br" style="letter-spacing:normal;font-size:14px"></div>':''}
      <label style="font-size:11px;color:#3A6A48;text-transform:uppercase;letter-spacing:.5px">\${criar?'Nova senha pessoal':'Senha pessoal'}</label>
      <div class="senha-input-wrap"><input class="senha-input" type="password" id="senha-pessoal" placeholder="\${criar?'Mínimo 4 caracteres':'Sua senha pessoal'}" autocomplete="new-password"><button class="toggle-pw" onclick="togglePessoal('senha-pessoal')" type="button">👁</button></div>
      \${criar?'<label style="font-size:11px;color:#3A6A48;text-transform:uppercase;letter-spacing:.5px">Confirmar senha</label><div class="senha-input-wrap"><input class="senha-input" type="password" id="conf-pessoal" placeholder="Repita a senha" autocomplete="new-password"><button class="toggle-pw" onclick="togglePessoal(\\'conf-pessoal\\')" type="button">👁</button></div>':''}
      <button class="btn-entrar" id="btn-pessoal" onclick="entrarPessoal()" style="background:\${info.color};margin-top:4px">\${criar?'CRIAR E ENTRAR':'ENTRAR'}</button>
      <div class="erro-msg" id="erro-pessoal"></div>
      \${!criar?'<div style="text-align:center;margin-top:12px"><button onclick="esqueceuSenha()" style="background:none;border:none;color:#3A6A48;font-size:11px;cursor:pointer;text-decoration:underline">Esqueci minha senha</button></div>':''}
      <div style="text-align:center;margin-top:10px"><button onclick="voltarLogin()" style="background:none;border:none;color:#1C4A34;font-size:11px;cursor:pointer">← Voltar</button></div>
    </div>
  \`;
  setTimeout(()=>document.getElementById(criar?'email-pessoal':'senha-pessoal')?.focus(),50);
  document.getElementById('senha-pessoal').addEventListener('keydown',e=>{if(e.key==='Enter')entrarPessoal();});
}

async function entrarPessoal(){
  const btn=document.getElementById('btn-pessoal');
  const erro=document.getElementById('erro-pessoal');
  const criar=btn.textContent.includes('CRIAR');
  const senha=document.getElementById('senha-pessoal').value;
  const email=criar?(document.getElementById('email-pessoal')?.value||'').trim().toLowerCase():'';
  const conf=criar?(document.getElementById('conf-pessoal')?.value||''):'';
  if(criar&&!email){erro.textContent='Informe seu e-mail corporativo.';return;}
  if(criar&&!email.endsWith('@grupobrauna.com.br')){erro.textContent='Use seu e-mail corporativo @grupobrauna.com.br.';return;}
  if(!senha||senha.length<4){erro.textContent='A senha precisa ter ao menos 4 caracteres.';return;}
  if(criar&&senha!==conf){erro.textContent='As senhas não coincidem.';return;}
  btn.disabled=true;btn.textContent=criar?'Criando...':'Entrando...';
  erro.textContent='';
  let d2=null;
  for(let t=0;t<3;t++){
    try{
      const r2=await fetch('/api/login-pessoal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({identity:_sessaoPendente.identity,senha_pessoal:senha,criar,email})});
      const txt=await r2.text();try{d2=JSON.parse(txt);}catch{d2=null;}
      if(d2)break;
    }catch{d2=null;}
  }
  if(!d2){erro.textContent='Serviço indisponível. Tente novamente.';btn.disabled=false;btn.textContent=criar?'CRIAR E ENTRAR':'ENTRAR';return;}
  if(d2.ok){
    localStorage.setItem('brauna_role',_sessaoPendente.role);
    localStorage.setItem('brauna_role_ts',Date.now());
    if(_sessaoPendente.codigo)localStorage.setItem('brauna_codigo',_sessaoPendente.codigo);
    if(_sessaoPendente.nome)localStorage.setItem('brauna_nome',_sessaoPendente.nome);
    window.location.replace(ROLES[_sessaoPendente.role].dest);
  }else{
    erro.textContent=d2.msg||'Erro ao autenticar.';
    btn.disabled=false;btn.textContent=criar?'CRIAR E ENTRAR':'ENTRAR';
  }
}

function togglePessoal(id){const i=document.getElementById(id);i.type=i.type==='password'?'text':'password';}

function voltarLogin(){
  _sessaoPendente=null;
  document.getElementById('pessoal-box').style.display='none';
  document.getElementById('reset-box').style.display='none';
  document.getElementById('senha-box').style.display='block';
  document.querySelector('.roles').style.opacity='1';
  document.querySelector('.roles').style.pointerEvents='auto';
  document.getElementById('senha').value='';
  document.getElementById('senha').focus();
}

function esqueceuSenha(){
  document.getElementById('pessoal-box').style.display='none';
  document.getElementById('reset-box').style.display='block';
  document.getElementById('reset-box').innerHTML=\`
    <div class="senha-box">
      <div class="senha-label"><span>🔑</span>RECUPERAR SENHA</div>
      <p id="reset-aviso" style="font-size:12px;color:#3A6A48;margin-bottom:16px;line-height:1.5">Vamos enviar um link de redefinição para o e-mail cadastrado em "\${_sessaoPendente?.nome||''}".</p>
      <button class="btn-entrar" id="btn-reset" onclick="solicitarReset()" style="background:#C9A96E">ENVIAR LINK POR E-MAIL</button>
      <div class="erro-msg" id="erro-reset"></div>
      <div style="text-align:center;margin-top:10px"><button onclick="voltarLogin()" style="background:none;border:none;color:#1C4A34;font-size:11px;cursor:pointer">← Voltar</button></div>
    </div>
  \`;
}

async function solicitarReset(){
  if(!_sessaoPendente)return voltarLogin();
  const btn=document.getElementById('btn-reset');
  const erro=document.getElementById('erro-reset');
  btn.disabled=true;btn.textContent='Enviando...';erro.textContent='';
  try{
    const r=await fetch('/api/solicitar-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:_sessaoPendente.role,senha:_sessaoPendente.codigo||document.getElementById('senha').value})});
    const d=await r.json();
    if(d.ok){
      document.getElementById('reset-aviso').innerHTML=\`✅ Link enviado para <b>\${d.email_mascarado}</b>.<br><span style="color:#3A6A48">Verifique sua caixa de entrada.</span>\`;
      btn.style.display='none';
    }else{
      erro.textContent=d.msg||'Não foi possível enviar o e-mail.';
      btn.disabled=false;btn.textContent='TENTAR NOVAMENTE';
    }
  }catch(e){erro.textContent='Erro de conexão.';btn.disabled=false;btn.textContent='TENTAR NOVAMENTE';}
}

const saved=localStorage.getItem('brauna_role');
if(saved&&ROLES[saved])window.location.replace(ROLES[saved].dest);
</script>
</body></html>`;

// ── Handler principal ─────────────────────────────────────────────────────────

function readBody(req) {
  // Vercel pre-parses JSON bodies into req.body — stream events never fire
  if (req.body !== undefined && req.body !== null) {
    const b = req.body;
    return Promise.resolve(typeof b === "string" ? tryParse(b) : b);
  }
  return new Promise((resolve) => {
    let data = "";
    req.on("data", (c) => (data += c));
    req.on("end", () => resolve(tryParse(data)));
    req.on("error", () => resolve({}));
  });
}

function tryParse(s) {
  try { return JSON.parse(s); } catch { return {}; }
}

function sendJson(res, obj, status = 200) {
  const body = JSON.stringify(obj);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store",
  });
  res.end(body);
}

function sendHtml(res, html) {
  const body = Buffer.from(html, "utf-8");
  res.writeHead(200, {
    "Content-Type": "text/html; charset=utf-8",
    "Content-Length": body.length,
    "Cache-Control": "no-store",
  });
  res.end(body);
}

function err(res, msg, status = 400) {
  sendJson(res, { ok: false, msg }, status);
}

module.exports = async function handler(req, res) {
  try {
    const path   = (req.url || "/").split("?")[0].replace(/\/$/, "") || "/";
    const method = req.method.toUpperCase();

    // GET pages
    if (method === "GET" && path === "/") return sendHtml(res, HTML_LOGIN);
    if (method === "GET" && path === "/reset-senha") return sendHtml(res, HTML_RESET);

    // ping
    if (path === "/api/ping") return sendJson(res, { ok: true, ts: new Date().toISOString() });

    // POST /api/login
    if (method === "POST" && path === "/api/login") {
      const d     = await readBody(req);
      const role  = d.role || "";
      const senha = (d.senha || "").trim();

      let identity, nome, codigo;
      if (role === "assessor") {
        const cod = senha.toUpperCase();
        nome = ASSESSORES[cod];
        if (!nome) return err(res, "Código de assessor inválido", 401);
        identity = `assessor:${cod}`;
        codigo   = cod;
      } else if (["lider", "head", "admin"].includes(role)) {
        if (SENHAS[role] !== senha) return err(res, "Senha do perfil incorreta", 401);
        identity = role;
        nome     = role.charAt(0).toUpperCase() + role.slice(1);
        codigo   = null;
      } else {
        return err(res, "Perfil inválido", 401);
      }

      const senhas      = await loadSenhasPessoais();
      const precisa_criar = !(identity in senhas);
      return sendJson(res, { ok: true, etapa: "senha_pessoal", role, nome, codigo, identity, precisa_criar });
    }

    // POST /api/login-pessoal
    if (method === "POST" && path === "/api/login-pessoal") {
      const d        = await readBody(req);
      const identity = (d.identity || "").trim();
      const senha    = d.senha_pessoal || "";
      const criar    = !!d.criar;

      if (!identity) return err(res, "Sessão inválida. Recomece o login.");

      const senhas = await loadSenhasPessoais();
      if (criar) {
        if (identity in senhas) return err(res, "Senha já existe. Faça login normalmente.");
        if (senha.length < 4)   return err(res, "A senha precisa ter ao menos 4 caracteres.");
        const email = (d.email || "").trim().toLowerCase();
        if (!email.endsWith("@grupobrauna.com.br"))
          return err(res, "Use seu e-mail corporativo @grupobrauna.com.br.", 400);
        senhas[identity] = {
          hash:      hashSenha(senha),
          criada_em: new Date().toLocaleString("pt-BR"),
          email,
        };
        await saveSenhasPessoais(senhas);
        return sendJson(res, { ok: true, criada: true });
      }

      const guardado = senhas[identity];
      if (!guardado) return err(res, "Senha pessoal não cadastrada.", 400);
      if (verificaSenha(senha, entryHash(guardado)))
        return sendJson(res, { ok: true });
      return err(res, "Senha pessoal incorreta.", 401);
    }

    // POST /api/solicitar-reset
    if (method === "POST" && path === "/api/solicitar-reset") {
      const d     = await readBody(req);
      const role  = d.role || "assessor";
      const senha = (d.senha || "").trim().toUpperCase();

      let identity, nome;
      if (role === "assessor") {
        nome = ASSESSORES[senha];
        if (!nome) return err(res, "Código de assessor não encontrado", 404);
        identity = `assessor:${senha}`;
      } else if (["lider", "head", "admin"].includes(role)) {
        identity = role;
        nome     = role.charAt(0).toUpperCase() + role.slice(1);
      } else {
        return err(res, "Perfil inválido", 400);
      }

      const senhas = await loadSenhasPessoais();
      const entry  = senhas[identity];
      if (!entry || !entry.email) return err(res, "E-mail de recuperação não cadastrado. Entre em contato com o administrador.", 400);

      const token = crypto.randomBytes(32).toString("hex");
      const tokens = await loadResetTokens();
      tokens[token] = {
        identity,
        nome,
        expires: Date.now() + 3600000,
      };
      await saveResetTokens(tokens);

      const email_mascarado = entry.email.replace(/(.{2}).+(@.+)/, "$1***$2");
      // Email sending not configured — inform the user
      return sendJson(res, {
        ok: true,
        email_mascarado,
        msg: "Link de redefinição gerado. Configure o SMTP para envio automático.",
      });
    }

    // POST /api/verificar-token-reset
    if (method === "POST" && path === "/api/verificar-token-reset") {
      const d      = await readBody(req);
      const token  = d.token || "";
      const tokens = await loadResetTokens();
      const entry  = tokens[token];
      if (!entry || entry.expires < Date.now()) return err(res, "Token inválido ou expirado.", 400);
      return sendJson(res, { ok: true, nome: entry.nome });
    }

    // POST /api/confirmar-reset
    if (method === "POST" && path === "/api/confirmar-reset") {
      const d      = await readBody(req);
      const token  = d.token || "";
      const senha  = d.senha || "";
      const tokens = await loadResetTokens();
      const entry  = tokens[token];
      if (!entry || entry.expires < Date.now()) return err(res, "Token inválido ou expirado.", 400);
      if (senha.length < 4) return err(res, "A senha precisa ter ao menos 4 caracteres.");

      const senhas = await loadSenhasPessoais();
      const prev   = senhas[entry.identity] || {};
      senhas[entry.identity] = { ...prev, hash: hashSenha(senha), alterada_em: new Date().toLocaleString("pt-BR") };
      await saveSenhasPessoais(senhas);

      delete tokens[token];
      await saveResetTokens(tokens);
      return sendJson(res, { ok: true });
    }

    return err(res, "Not found", 404);
  } catch (e) {
    sendJson(res, { ok: false, msg: `Erro interno: ${e.message}` }, 500);
  }
};
