import json, os, time
import hashlib as _hashlib
import secrets as _secrets
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

SENHAS = {
    "lider":    "lider2026",
    "admin":    "admin2026",
    "head":     "head2026",
}

ASSESSORES = {
    "A74621": "Lucas Landroni Cozzi",
    "A68983": "Tatiane Cristina da Silva Cecchetti",
    "A27157": "Felipe Fraga",
    "A34003": "Bruno Seiji Ito",
    "A74329": "Matheus Escoza Milani",
    "A25261": "Alex Alves dos Santos",
    "A53115": "Flavia Guedes de Souza",
    "A55932": "Carolina Custodio Siqueira",
    "A74638": "Andre Guilherme Leite Figueiredo",
    "A22930": "Carlos Fernando Victor Bolivar Moreira Neto",
    "A67952": "Giuseppe Hilario Neto",
    "A72679": "Paulo Roberto Negreiros Sobrinho",
    "A26364": "Felipe Santos Nishio",
    "A56767": "Michael Ademilson Santos da Silva",
    "A38890": "Marcelo Ramos Dias",
    "A22075": "Denis Kinoshita",
}

_SENHAS_PESSOAIS_FILE = "/tmp/brauna_senhas_pessoais.json"
_RESET_TOKENS_FILE    = "/tmp/brauna_reset_tokens.json"

def _kv_client():
    url   = os.environ.get("KV_REST_API_URL")
    token = os.environ.get("KV_REST_API_TOKEN")
    if not url or not token:
        return None
    try:
        from upstash_redis import Redis
        return Redis(url=url, token=token)
    except Exception:
        return None

def _key(path: str) -> str:
    name = os.path.basename(path).replace("brauna_", "").replace(".json", "")
    return f"brauna:{name}"

def _load(path, default):
    kv = _kv_client()
    if kv:
        try:
            val = kv.get(_key(path))
            if val is not None:
                return json.loads(val) if isinstance(val, str) else val
        except Exception:
            pass
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save(path, data):
    kv = _kv_client()
    if kv:
        try:
            kv.set(_key(path), json.dumps(data, ensure_ascii=False))
            return
        except Exception:
            pass
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _hash_senha(senha: str) -> str:
    salt = _secrets.token_hex(16)
    h = _hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
    return f"{salt}${h}"

def _verifica_senha(senha: str, guardado: str) -> bool:
    try:
        salt, h = guardado.split("$", 1)
        calc = _hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
        return _secrets.compare_digest(calc, h)
    except Exception:
        return False

def _entry_hash(entry):
    if isinstance(entry, dict):
        return entry.get("hash", "")
    return entry or ""

def load_senhas_pessoais():  return _load(_SENHAS_PESSOAIS_FILE, {})
def save_senhas_pessoais(d): _save(_SENHAS_PESSOAIS_FILE, d)
def load_reset_tokens():     return _load(_RESET_TOKENS_FILE, {})
def save_reset_tokens(d):    _save(_RESET_TOKENS_FILE, d)

def _enviar_email_reset(destinatario: str, nome: str, token: str):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    host  = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port  = int(os.environ.get("SMTP_PORT", "587"))
    user  = os.environ.get("SMTP_USER", "")
    pwd   = os.environ.get("SMTP_PASS", "")
    frm   = os.environ.get("SMTP_FROM", user)
    base  = os.environ.get("APP_URL", "https://analise-carteiras-brauna.vercel.app")

    if not user or not pwd:
        return False

    link = f"{base}/reset-senha?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Braúna Investimentos — Redefinição de senha"
    msg["From"]    = frm
    msg["To"]      = destinatario

    txt = (f"Olá, {nome}!\n\nClique no link abaixo para criar uma nova senha:\n{link}\n\n"
           "Este link expira em 1 hora.\n\nBraúna Investimentos")
    html = f"""<!DOCTYPE html><html><body style="font-family:Segoe UI,sans-serif;background:#081F18;color:#F0F0F0;padding:40px 20px;margin:0">
<div style="max-width:480px;margin:0 auto;background:#111;border-radius:16px;padding:32px;border:1px solid #1A4030">
  <div style="text-align:center;margin-bottom:28px">
    <div style="font-size:22px;font-weight:800;color:#C9A96E;letter-spacing:2px">BRAÚNA INVESTIMENTOS</div>
    <div style="font-size:12px;color:#3A6A48;margin-top:4px">Sistema de Análise de Carteiras</div>
  </div>
  <p style="color:#CCC;font-size:14px;margin-bottom:8px">Olá, <strong style="color:#F0F0F0">{nome}</strong>!</p>
  <p style="color:#888;font-size:13px;line-height:1.6;margin-bottom:24px">
    Recebemos uma solicitação para redefinir sua senha no sistema Braúna.<br>
    Clique no botão abaixo para criar uma nova senha.
  </p>
  <div style="text-align:center;margin-bottom:24px">
    <a href="{link}" style="display:inline-block;background:#C9A96E;color:#081F18;font-weight:700;font-size:14px;padding:14px 32px;border-radius:10px;text-decoration:none;letter-spacing:.5px">
      Redefinir minha senha
    </a>
  </div>
  <p style="color:#3A6A48;font-size:11px;text-align:center">Este link expira em <strong>1 hora</strong>.<br>
  Se não foi você, ignore este e-mail — sua senha continua a mesma.</p>
  <hr style="border:none;border-top:1px solid #1A2A1A;margin:24px 0">
  <p style="color:#1A4030;font-size:10px;text-align:center">Braúna Investimentos · Uso interno · Acesso restrito</p>
</div>
</body></html>"""

    msg.attach(MIMEText(txt, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(host, port) as s:
            s.ehlo(); s.starttls(); s.login(user, pwd)
            s.sendmail(frm, destinatario, msg.as_string())
        return True
    except Exception:
        return False


HTML_RESET_SENHA = r"""<!DOCTYPE html>
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
.btn:hover{opacity:.85}
.btn:disabled{opacity:.4;cursor:not-allowed}
.msg{font-size:12px;margin-top:12px;text-align:center;min-height:18px}
.msg.ok{color:#5DCAA5}
.msg.err{color:#FF6B6B}
.back{display:block;text-align:center;margin-top:18px;font-size:12px;color:#3A6A48;text-decoration:none}
.back:hover{color:#C9A96E}
.loading{display:inline-block;width:16px;height:16px;border:2px solid #081F18;border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="card" id="card">
  <div class="logo">
    <div class="logo-title">BRAÚNA INVESTIMENTOS</div>
    <div class="logo-sub">Redefinição de senha</div>
  </div>

  <div id="state-loading" style="text-align:center;padding:20px 0">
    <div class="loading" style="width:24px;height:24px;border-color:#C9A96E;border-top-color:transparent;display:inline-block"></div>
    <p style="color:#3A6A48;font-size:13px;margin-top:12px">Verificando link...</p>
  </div>

  <div id="state-invalido" style="display:none;text-align:center;padding:10px 0">
    <div style="font-size:36px;margin-bottom:12px">⚠️</div>
    <h2 style="color:#FF6B6B;margin-bottom:8px">Link inválido ou expirado</h2>
    <p style="font-size:12px;color:#888;line-height:1.5;margin-bottom:20px">Este link de redefinição já foi utilizado ou expirou.<br>Solicite um novo na tela de login.</p>
    <a href="/" class="btn" style="display:block;text-align:center;text-decoration:none;padding:13px">Voltar ao login</a>
  </div>

  <div id="state-form" style="display:none">
    <h2>Olá, <span id="nome-usuario"></span>!</h2>
    <p class="desc">Escolha uma nova senha para acessar o sistema.</p>
    <div>
      <label>Nova senha</label>
      <input type="password" id="nova-senha" placeholder="Mínimo 4 caracteres" minlength="4">
    </div>
    <div>
      <label>Confirmar senha</label>
      <input type="password" id="conf-senha" placeholder="Repita a senha">
    </div>
    <button class="btn" id="btn-salvar" onclick="salvar()">Salvar nova senha</button>
    <div class="msg" id="msg-form"></div>
  </div>

  <div id="state-sucesso" style="display:none;text-align:center;padding:10px 0">
    <div style="font-size:36px;margin-bottom:12px">✅</div>
    <h2 style="color:#5DCAA5;margin-bottom:8px">Senha redefinida!</h2>
    <p style="font-size:12px;color:#888;margin-bottom:20px">Sua nova senha foi salva com sucesso. Você já pode fazer login.</p>
    <a href="/" class="btn" style="display:block;text-align:center;text-decoration:none;padding:13px">Ir para o login</a>
  </div>
</div>

<script>
let tokenAtual = '';
function estado(id){
  ['state-loading','state-invalido','state-form','state-sucesso'].forEach(s=>{
    document.getElementById(s).style.display = s===id ? 'block' : 'none';
  });
}
async function init(){
  const params = new URLSearchParams(location.search);
  tokenAtual = params.get('token') || '';
  if(!tokenAtual){ estado('state-invalido'); return; }
  try{
    const r = await fetch('/api/verificar-token-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:tokenAtual})});
    const d = await r.json();
    if(!d.ok){ estado('state-invalido'); return; }
    document.getElementById('nome-usuario').textContent = d.nome;
    estado('state-form');
  }catch(e){ estado('state-invalido'); }
}
async function salvar(){
  const nova = document.getElementById('nova-senha').value;
  const conf = document.getElementById('conf-senha').value;
  const msg  = document.getElementById('msg-form');
  const btn  = document.getElementById('btn-salvar');
  if(nova.length < 4){ msg.className='msg err'; msg.textContent='A senha precisa ter ao menos 4 caracteres.'; return; }
  if(nova !== conf){   msg.className='msg err'; msg.textContent='As senhas não coincidem.'; return; }
  btn.disabled = true; btn.innerHTML = '<span class="loading"></span>Salvando...'; msg.textContent = '';
  try{
    const r = await fetch('/api/confirmar-reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:tokenAtual,senha:nova})});
    const d = await r.json();
    if(d.ok){ estado('state-sucesso'); return; }
    msg.className='msg err'; msg.textContent = d.msg || 'Erro ao salvar. Tente novamente.';
  }catch(e){ msg.className='msg err'; msg.textContent = 'Erro de conexão.'; }
  btn.disabled = false; btn.textContent = 'Salvar nova senha';
}
init();
</script>
</body></html>"""


HTML_LOGIN = r"""<!DOCTYPE html>
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
.role-card{
  width:200px;padding:28px 20px;border-radius:16px;
  border:1.5px solid #1A4030;background:#111;
  cursor:pointer;text-align:center;transition:all .25s;
  position:relative;overflow:hidden;
}
.role-card::before{content:'';position:absolute;inset:0;opacity:0;transition:opacity .25s;}
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
.role-check{
  position:absolute;top:10px;right:10px;
  width:18px;height:18px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:900;
  opacity:0;transition:opacity .2s;
}
.assessor .role-check{background:#C9A96E;color:#000}
.lider .role-check{background:#8B9FE8;color:#000}
.admin .role-check{background:#5DCAA5;color:#000}
.role-card.selected .role-check{opacity:1}
.senha-box{
  width:100%;max-width:380px;
  background:#111;border-radius:14px;padding:28px;
  border:1px solid #1A4030;
  animation:fadeUp .25s ease;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.senha-label{font-size:11px;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.senha-label span{font-size:16px}
.senha-input-wrap{position:relative;margin-bottom:14px}
.senha-input{
  width:100%;background:#0A0A0A;border:1.5px solid #1C4A34;
  border-radius:10px;padding:13px 44px 13px 16px;
  color:#F0F0F0;font-size:16px;letter-spacing:4px;outline:none;
  transition:border .2s;
}
.senha-input::placeholder{letter-spacing:1px;font-size:13px;color:#1E4A30}
.senha-input:focus{border-color:var(--role-color)}
.toggle-pw{
  position:absolute;right:14px;top:50%;transform:translateY(-50%);
  background:none;border:none;color:#2A5A3A;cursor:pointer;font-size:16px;padding:0;
}
.btn-entrar{
  width:100%;padding:14px;border:none;border-radius:10px;
  font-size:14px;font-weight:800;cursor:pointer;
  letter-spacing:.5px;text-transform:uppercase;
  transition:all .2s;background:var(--role-color);color:#081F18;
}
.btn-entrar:hover{opacity:.88;transform:translateY(-1px)}
.btn-entrar:disabled{opacity:.3;cursor:not-allowed;transform:none}
.erro-msg{font-size:12px;color:#FF6B6B;text-align:center;margin-top:10px;height:18px;transition:opacity .2s;}
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
    <div class="role-check">✓</div>
    <span class="role-icon">📊</span>
    <div class="role-name" style="color:#C9A96E">Assessor</div>
    <div class="role-desc">Análise de carteiras e atendimento ao cliente</div>
  </div>
  <div class="role-card lider" onclick="selRole('lider')" id="card-lider">
    <div class="role-check">✓</div>
    <span class="role-icon">👥</span>
    <div class="role-name" style="color:#8B9FE8">Líder</div>
    <div class="role-desc">Visão da equipe, OKRs e orientação aos assessores</div>
  </div>
  <div class="role-card head" onclick="selRole('head')" id="card-head">
    <div class="role-check">✓</div>
    <span class="role-icon">🏛️</span>
    <div class="role-name" style="color:#D4B483">Head de Produtos</div>
    <div class="role-desc">Portfólios modelo, cenário macro e produtos em destaque</div>
  </div>
  <div class="role-card admin" onclick="selRole('admin')" id="card-admin">
    <div class="role-check">✓</div>
    <span class="role-icon">⚙️</span>
    <div class="role-name" style="color:#5DCAA5">Administração</div>
    <div class="role-desc">Documentos estratégicos, cartas e configurações</div>
  </div>
</div>

<div class="senha-box" id="senha-box" style="display:none">
  <div class="senha-label" id="senha-label">
    <span id="senha-icon"></span>
    <span id="senha-role-name" style="color:var(--role-color)"></span>
  </div>
  <div class="senha-input-wrap">
    <input type="password" id="senha" class="senha-input" placeholder="Digite sua senha" onkeydown="if(event.key==='Enter')entrar()">
    <button class="toggle-pw" onclick="toggleSenha()" type="button">👁</button>
  </div>
  <button class="btn-entrar" id="btn-entrar" onclick="entrar()">Continuar</button>
  <div class="erro-msg" id="erro"></div>
</div>

<div class="senha-box" id="pessoal-box" style="display:none">
  <div class="senha-label">
    <span>🔐</span>
    <span id="pessoal-titulo" style="color:var(--role-color)">Senha pessoal</span>
  </div>
  <div id="pessoal-aviso" style="font-size:11px;color:#888;margin-bottom:10px;line-height:1.5"></div>
  <div class="senha-input-wrap">
    <input type="password" id="senha-pessoal" class="senha-input" placeholder="Sua senha pessoal" onkeydown="if(event.key==='Enter')entrarPessoal()">
    <button class="toggle-pw" onclick="togglePessoal('senha-pessoal')" type="button">👁</button>
  </div>
  <div class="senha-input-wrap" id="confirma-wrap" style="display:none;margin-top:10px">
    <input type="password" id="senha-pessoal-confirma" class="senha-input" placeholder="Repita a senha pessoal" onkeydown="if(event.key==='Enter')entrarPessoal()">
    <button class="toggle-pw" onclick="togglePessoal('senha-pessoal-confirma')" type="button">👁</button>
  </div>
  <div id="email-wrap" style="display:none;margin-top:10px">
    <input type="email" id="email-pessoal" class="senha-input" placeholder="nome@grupobrauna.com.br"
      style="letter-spacing:normal;font-size:13px" onkeydown="if(event.key==='Enter')entrarPessoal()">
  </div>
  <button class="btn-entrar" id="btn-pessoal" onclick="entrarPessoal()">Entrar</button>
  <button class="btn-entrar" onclick="voltarLogin()" style="background:none;border:1px solid #333;color:#888;margin-top:8px">Voltar</button>
  <div class="erro-msg" id="erro-pessoal"></div>
  <div id="esqueci-wrap" style="display:none;text-align:center;margin-top:14px">
    <button onclick="esqueceuSenha()" style="background:none;border:none;color:#3A6A48;font-size:12px;cursor:pointer;text-decoration:underline">Esqueci minha senha</button>
  </div>
</div>

<div class="senha-box" id="reset-box" style="display:none">
  <div class="senha-label"><span>📧</span><span style="color:var(--role-color)">Redefinir senha</span></div>
  <div style="font-size:11px;color:#888;margin-bottom:12px;line-height:1.5" id="reset-aviso">
    Enviaremos um link de redefinição para o e-mail cadastrado no seu perfil.
  </div>
  <button class="btn-entrar" id="btn-reset" onclick="solicitarReset()">Enviar link por e-mail</button>
  <button class="btn-entrar" onclick="voltarLogin()" style="background:none;border:1px solid #333;color:#888;margin-top:8px">Voltar</button>
  <div class="erro-msg" id="erro-reset"></div>
</div>

<div class="rodape">Braúna Investimentos · Uso interno · Acesso restrito</div>

<script>
let roleAtual = null;
const ROLES = {
  assessor: {nome:"Assessor",        icon:"📊", color:"#C9A96E", dest:"/assessor"},
  lider:    {nome:"Líder",           icon:"👥", color:"#8B9FE8", dest:"/lider"},
  head:     {nome:"Head de Produtos",icon:"🏛️", color:"#D4B483", dest:"/head-produtos"},
  admin:    {nome:"Administração",   icon:"⚙️", color:"#5DCAA5", dest:"/admin"},
};

function selRole(role){
  roleAtual = role;
  document.querySelectorAll(".role-card").forEach(c=>c.classList.remove("selected"));
  document.getElementById("card-"+role).classList.add("selected");
  const r = ROLES[role];
  document.documentElement.style.setProperty("--role-color", r.color);
  document.getElementById("senha-icon").textContent = r.icon;
  document.getElementById("senha-role-name").textContent = r.nome;
  document.getElementById("senha").value = "";
  document.getElementById("erro").textContent = "";
  const inp = document.getElementById("senha");
  inp.placeholder = role === "assessor" ? "Código do assessor (ex: A74621)" : "Digite sua senha";
  inp.style.letterSpacing = role === "assessor" ? "2px" : "4px";
  document.getElementById("senha-box").style.display = "block";
  setTimeout(()=>inp.focus(), 50);
}

function toggleSenha(){
  const inp = document.getElementById("senha");
  inp.type = inp.type === "password" ? "text" : "password";
}

let _sessaoPendente = null;

async function entrar(){
  if(!roleAtual) return;
  const senha = document.getElementById("senha").value;
  if(!senha){ document.getElementById("erro").textContent="Digite a senha."; return; }
  const btn = document.getElementById("btn-entrar");
  btn.disabled = true; btn.textContent = "Verificando...";
  document.getElementById("erro").textContent = "";
  let d = null;
  for(let t = 0; t < 12; t++){
    try{
      const r = await fetch("/api/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({role: roleAtual, senha})
      });
      const text = await r.text();
      try{ d = JSON.parse(text); } catch{ d = null; }
      if(d) break;
    } catch(e){ d = null; }
    if(t < 11){
      document.getElementById("erro").textContent = `Servidor iniciando, aguarde... (${t+1}/12)`;
      await new Promise(res => setTimeout(res, 3000));
    }
  }
  btn.disabled = false; btn.textContent = "Continuar";
  if(!d){
    document.getElementById("erro").textContent = "Serviço indisponível. Recarregue a página e tente novamente.";
    return;
  }
  if(d.ok && d.etapa === "senha_pessoal"){
    _sessaoPendente = {role: d.role, nome: d.nome, codigo: d.codigo, identity: d.identity};
    mostrarSenhaPessoal(d.precisa_criar);
  } else {
    document.getElementById("erro").textContent = d.msg || "Credencial inválida. Tente novamente.";
    document.getElementById("senha").value="";
    document.getElementById("senha").focus();
  }
}

function mostrarSenhaPessoal(precisaCriar){
  document.getElementById("senha-box").style.display = "none";
  document.querySelector(".roles").style.opacity = ".4";
  document.querySelector(".roles").style.pointerEvents = "none";
  const box = document.getElementById("pessoal-box");
  box.style.display = "block";
  box.dataset.criar = precisaCriar ? "1" : "0";
  document.getElementById("confirma-wrap").style.display = precisaCriar ? "block" : "none";
  document.getElementById("email-wrap").style.display    = precisaCriar ? "block" : "none";
  document.getElementById("esqueci-wrap").style.display  = precisaCriar ? "none"  : "block";
  document.getElementById("pessoal-titulo").textContent = precisaCriar ? "Crie sua senha pessoal" : "Senha pessoal";
  document.getElementById("pessoal-aviso").innerHTML = precisaCriar
    ? "🔒 Primeiro acesso: crie uma <b>senha pessoal só sua</b> e informe seu e-mail para recuperação. Ninguém com seu código consegue acessar sem ela."
    : "Digite sua senha pessoal para acessar.";
  document.getElementById("btn-pessoal").textContent = precisaCriar ? "Criar e entrar" : "Entrar";
  document.getElementById("senha-pessoal").value = "";
  document.getElementById("senha-pessoal-confirma").value = "";
  document.getElementById("email-pessoal") && (document.getElementById("email-pessoal").value = "");
  document.getElementById("erro-pessoal").textContent = "";
  setTimeout(()=>document.getElementById("senha-pessoal").focus(), 50);
}

async function entrarPessoal(){
  if(!_sessaoPendente) return voltarLogin();
  const criar = document.getElementById("pessoal-box").dataset.criar === "1";
  const senha = document.getElementById("senha-pessoal").value;
  const erro  = document.getElementById("erro-pessoal");
  erro.textContent = "";
  if(!senha){ erro.textContent = "Digite a senha pessoal."; return; }
  if(criar){
    if(senha.length < 4){ erro.textContent = "Mínimo de 4 caracteres."; return; }
    if(senha !== document.getElementById("senha-pessoal-confirma").value){
      erro.textContent = "As senhas não conferem."; return;
    }
  }
  const btn = document.getElementById("btn-pessoal");
  btn.disabled = true; btn.textContent = "Verificando...";
  try{
    const email = criar ? (document.getElementById("email-pessoal").value.trim().toLowerCase()) : "";
    if(criar && !email){ erro.textContent = "Informe seu e-mail corporativo."; btn.disabled=false; btn.textContent="Criar e entrar"; return; }
    if(criar && !email.endsWith("@grupobrauna.com.br")){ erro.textContent = "Use seu e-mail corporativo @grupobrauna.com.br."; btn.disabled=false; btn.textContent="Criar e entrar"; return; }
    let d2 = null;
    for(let t = 0; t < 3; t++){
      try{
        const r2 = await fetch("/api/login-pessoal",{
          method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({identity: _sessaoPendente.identity, senha_pessoal: senha, criar, email})
        });
        const txt = await r2.text();
        try{ d2 = JSON.parse(txt); } catch{ d2 = null; }
        if(d2) break;
        if(t < 2){ erro.textContent = `Inicializando... (${t+2}/3)`; await new Promise(res=>setTimeout(res,3000)); }
      } catch(e){
        if(t===2){ d2=null; break; }
        await new Promise(res=>setTimeout(res,3000));
      }
    }
    const d = d2;
    if(!d){ erro.textContent = "Serviço indisponível. Tente novamente."; btn.disabled=false; btn.textContent=criar?"Criar e entrar":"Entrar"; return; }
    if(d.ok){
      localStorage.setItem("brauna_role", _sessaoPendente.role);
      localStorage.setItem("brauna_role_ts", Date.now());
      if(_sessaoPendente.nome)   localStorage.setItem("brauna_nome",   _sessaoPendente.nome);
      if(_sessaoPendente.codigo) localStorage.setItem("brauna_codigo", _sessaoPendente.codigo);
      window.location.href = ROLES[_sessaoPendente.role].dest;
    } else {
      erro.textContent = d.msg || "Falha ao validar senha pessoal.";
      document.getElementById("senha-pessoal").focus();
    }
  } catch(e){
    erro.textContent = "Erro de conexão.";
  } finally {
    btn.disabled = false;
    btn.textContent = criar ? "Criar e entrar" : "Entrar";
  }
}

function togglePessoal(id){
  const inp = document.getElementById(id);
  inp.type = inp.type === "password" ? "text" : "password";
}

function voltarLogin(){
  _sessaoPendente = null;
  document.getElementById("pessoal-box").style.display = "none";
  document.getElementById("reset-box").style.display   = "none";
  document.getElementById("senha-box").style.display   = "block";
  document.querySelector(".roles").style.opacity = "1";
  document.querySelector(".roles").style.pointerEvents = "auto";
  document.getElementById("senha").value = "";
  document.getElementById("senha").focus();
}

function esqueceuSenha(){
  document.getElementById("pessoal-box").style.display = "none";
  document.getElementById("reset-box").style.display   = "block";
  document.getElementById("erro-reset").textContent = "";
  document.getElementById("btn-reset").disabled = false;
  document.getElementById("btn-reset").textContent = "Enviar link por e-mail";
  if(_sessaoPendente){
    document.getElementById("reset-aviso").textContent =
      `Vamos enviar um link de redefinição para o e-mail cadastrado em "${_sessaoPendente.nome}".`;
  }
}

async function solicitarReset(){
  if(!_sessaoPendente) return voltarLogin();
  const btn  = document.getElementById("btn-reset");
  const erro = document.getElementById("erro-reset");
  btn.disabled = true; btn.textContent = "Enviando..."; erro.textContent = "";
  try{
    const r = await fetch("/api/solicitar-reset",{
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({role: _sessaoPendente.role, senha: _sessaoPendente.codigo || document.getElementById("senha").value})
    });
    const d = await r.json();
    if(d.ok){
      document.getElementById("reset-aviso").innerHTML =
        `✅ Link enviado para <b>${d.email_mascarado}</b>.<br><span style="color:#3A6A48">Verifique sua caixa de entrada e clique no link para criar nova senha.</span>`;
      btn.style.display = "none";
    } else {
      erro.textContent = d.msg || "Não foi possível enviar o e-mail.";
      btn.disabled = false; btn.textContent = "Tentar novamente";
    }
  }catch(e){
    erro.textContent = "Erro de conexão.";
    btn.disabled = false; btn.textContent = "Tentar novamente";
  }
}

// Aquece múltiplas instâncias Lambda em paralelo
(async function warmup(){
  const btn = document.getElementById("btn-entrar");
  if(btn){ btn.disabled = true; btn.textContent = "Conectando..."; }
  try{
    const pings = Array.from({length:10}, () => fetch("/api/ping").catch(()=>{}));
    await Promise.any(pings);
  } catch(e){}
  if(btn){ btn.disabled = false; btn.textContent = "Continuar"; }
})();

const saved = localStorage.getItem("brauna_role");
if(saved && ROLES[saved]){
  window.location.replace(ROLES[saved].dest);
}
</script>
</body></html>"""


# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def login_page():
    resp = app.make_response(render_template_string(HTML_LOGIN))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/reset-senha")
def reset_senha_page():
    return render_template_string(HTML_RESET_SENHA)

@app.route("/api/ping", methods=["GET", "POST"])
def ping():
    return jsonify({"ok": True, "ts": datetime.now().isoformat()})

@app.route("/api/login", methods=["POST"])
def login():
    d     = request.get_json()
    role  = d.get("role", "")
    senha = d.get("senha", "").strip()

    identity, nome, codigo = None, None, None
    if role == "assessor":
        cod = senha.upper()
        nome = ASSESSORES.get(cod)
        if not nome:
            return jsonify({"ok": False, "msg": "Código de assessor inválido"}), 401
        identity, codigo = f"assessor:{cod}", cod
    elif role in ("lider", "head", "admin"):
        if SENHAS.get(role) != senha:
            return jsonify({"ok": False, "msg": "Senha do perfil incorreta"}), 401
        identity, nome = role, role.capitalize()
    else:
        return jsonify({"ok": False, "msg": "Perfil inválido"}), 401

    senhas = load_senhas_pessoais()
    precisa_criar = identity not in senhas
    return jsonify({
        "ok": True, "etapa": "senha_pessoal",
        "role": role, "nome": nome, "codigo": codigo,
        "identity": identity, "precisa_criar": precisa_criar,
    })

@app.route("/api/login-pessoal", methods=["POST"])
def login_pessoal():
    d        = request.get_json() or {}
    identity = d.get("identity", "").strip()
    senha    = d.get("senha_pessoal", "")
    criar    = bool(d.get("criar"))
    if not identity:
        return jsonify({"ok": False, "msg": "Sessão inválida. Recomece o login."}), 400

    senhas = load_senhas_pessoais()
    if criar:
        if identity in senhas:
            return jsonify({"ok": False, "msg": "Senha já existe. Faça login normalmente."}), 400
        if len(senha) < 4:
            return jsonify({"ok": False, "msg": "A senha precisa ter ao menos 4 caracteres."}), 400
        email = (d.get("email") or "").strip().lower()
        if not email.endswith("@grupobrauna.com.br"):
            return jsonify({"ok": False, "msg": "Use seu e-mail corporativo @grupobrauna.com.br."}), 400
        senhas[identity] = {
            "hash": _hash_senha(senha),
            "criada_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "email": email,
        }
        save_senhas_pessoais(senhas)
        return jsonify({"ok": True, "criada": True})
    guardado = senhas.get(identity)
    if not guardado:
        return jsonify({"ok": False, "msg": "Senha pessoal não cadastrada.", "precisa_criar": True}), 400
    if _verifica_senha(senha, _entry_hash(guardado)):
        return jsonify({"ok": True})
    return jsonify({"ok": False, "msg": "Senha pessoal incorreta."}), 401

@app.route("/api/solicitar-reset", methods=["POST"])
def solicitar_reset():
    d = request.get_json() or {}
    role  = d.get("role", "assessor")
    senha = (d.get("senha") or "").strip().upper()

    if role == "assessor":
        nome = ASSESSORES.get(senha)
        if not nome:
            return jsonify({"ok": False, "msg": "Código de assessor não encontrado"}), 404
        identity = f"assessor:{senha}"
    elif role in ("lider", "head", "admin"):
        identity = role
        nome = role.capitalize()
    else:
        return jsonify({"ok": False, "msg": "Perfil inválido"}), 400

    senhas = load_senhas_pessoais()
    entrada = senhas.get(identity)
    if not entrada:
        return jsonify({"ok": False, "msg": "Nenhuma senha cadastrada para este usuário. Faça o primeiro acesso normalmente."}), 404

    email = entrada.get("email", "") if isinstance(entrada, dict) else ""
    if not email:
        return jsonify({"ok": False, "msg": "E-mail não cadastrado. Entre em contato com o administrador."}), 400
    if not email.endswith("@grupobrauna.com.br"):
        return jsonify({"ok": False, "msg": "Reset só permitido para e-mails @grupobrauna.com.br."}), 403

    token = _secrets.token_urlsafe(32)
    tokens = load_reset_tokens()
    agora = time.time()
    tokens = {k: v for k, v in tokens.items() if v.get("expira", 0) > agora}
    tokens[token] = {
        "identity": identity, "nome": nome, "email": email,
        "expira": agora + 3600,
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    save_reset_tokens(tokens)

    enviado = _enviar_email_reset(email, nome, token)
    if not enviado:
        if not os.environ.get("SMTP_USER"):
            return jsonify({"ok": True, "dev_token": token, "email_mascarado": email,
                            "aviso": "SMTP não configurado — use o dev_token para testar"})
        return jsonify({"ok": False, "msg": "Falha ao enviar e-mail. Tente novamente ou contate o admin."}), 500

    partes = email.split("@")
    visivel = partes[0][:2] + "**"
    mascarado = visivel + "@" + partes[1] if len(partes) > 1 else email
    return jsonify({"ok": True, "email_mascarado": mascarado})

@app.route("/api/confirmar-reset", methods=["POST"])
def confirmar_reset():
    d = request.get_json() or {}
    token      = (d.get("token") or "").strip()
    nova_senha = d.get("senha", "")

    if not token:
        return jsonify({"ok": False, "msg": "Token inválido"}), 400
    if len(nova_senha) < 4:
        return jsonify({"ok": False, "msg": "A senha precisa ter ao menos 4 caracteres."}), 400

    tokens = load_reset_tokens()
    entrada = tokens.get(token)
    if not entrada:
        return jsonify({"ok": False, "msg": "Link inválido ou já utilizado."}), 400
    if entrada.get("expira", 0) < time.time():
        del tokens[token]
        save_reset_tokens(tokens)
        return jsonify({"ok": False, "msg": "Este link expirou. Solicite um novo reset."}), 400

    identity = entrada["identity"]
    senhas = load_senhas_pessoais()
    existente = senhas.get(identity) or {}
    email = existente.get("email", entrada.get("email", "")) if isinstance(existente, dict) else ""

    senhas[identity] = {
        "hash": _hash_senha(nova_senha),
        "criada_em": existente.get("criada_em", "") if isinstance(existente, dict) else "",
        "atualizada_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "email": email,
    }
    save_senhas_pessoais(senhas)
    del tokens[token]
    save_reset_tokens(tokens)
    return jsonify({"ok": True, "nome": entrada.get("nome", "")})

@app.route("/api/verificar-token-reset", methods=["POST"])
def verificar_token_reset():
    token = (request.get_json() or {}).get("token", "").strip()
    tokens = load_reset_tokens()
    entrada = tokens.get(token)
    if not entrada or entrada.get("expira", 0) < time.time():
        return jsonify({"ok": False, "msg": "Link inválido ou expirado."})
    return jsonify({"ok": True, "nome": entrada.get("nome", "")})
