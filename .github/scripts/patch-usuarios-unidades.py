from pathlib import Path
import re


def sub_once(text, pattern, repl, label, flags=re.S):
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"No se pudo aplicar: {label} ({n})")
    return new


def replace_all_checked(text, old, new, label, min_count=1):
    n = text.count(old)
    if n < min_count:
        raise SystemExit(f"No se encontró: {label} ({n})")
    return text.replace(old, new)

# ---------------- administracion.html ----------------
p = Path('administracion.html')
a = p.read_text(encoding='utf-8')

new_users = r'''function renderUsers(){
const v=document.getElementById('view');const reg=base+'registro.html';
v.innerHTML='<div class="card"><div class="title">Crear / autorizar usuario</div><div class="muted">Podés crear la cuenta completa desde acá. Para un usuario nuevo ingresá una contraseña inicial de al menos 8 caracteres; después puede cambiarla con “Olvidé mi contraseña”.</div><div class="muted" style="margin-top:6px"><b>Administrador:</b> configuración completa · <b>Operador:</b> gestión de inventario · <b>Relevador:</b> relevamientos · <b>Consulta:</b> solo lectura.</div><form id="uform"><div class="grid"><div class="field"><label>Nombre</label><input id="uname" required></div><div class="field"><label>Correo</label><input id="uemail" type="email" required></div><div class="field"><label>Rol</label><select id="urole"><option value="admin">Administrador</option><option value="operador">Operador</option><option value="relevador">Relevador</option><option value="consulta">Consulta</option></select></div><div class="field"><label>Contraseña inicial</label><input id="upassword" type="password" minlength="8" autocomplete="new-password" placeholder="Solo obligatoria si la cuenta es nueva"><div class="isub">No se guarda en la base de datos del panel; se usa para crear el acceso en Supabase Auth.</div></div></div><button class="btn green">Crear / actualizar usuario</button></form><div class="item"><div class="ititle">Alternativa: que el usuario cree su contraseña</div><div class="isub">Si preferís no conocer su contraseña, autorizalo y pasale este enlace: '+e(reg)+'</div><button id="copyreg" class="btn blue" style="margin-top:8px">Copiar enlace de registro</button></div></div><div class="card"><div class="title">Usuarios autorizados</div><div id="ulist"></div></div>';
document.getElementById('uform').onsubmit=saveUser;document.getElementById('copyreg').onclick=async()=>{try{await navigator.clipboard.writeText(reg);alert('Enlace copiado.')}catch{prompt('Copiá este enlace:',reg)}};
document.getElementById('ulist').innerHTML=authorized.map(u=>{const p=profiles.find(x=>(x.email||'').toLowerCase()===u.email.toLowerCase());return '<div class="item"><div class="between"><div><div class="ititle">'+e(u.nombre||u.email)+'</div><div class="isub">'+e(u.email)+' · '+e(u.rol)+(p?' · cuenta creada':' · falta crear contraseña/cuenta')+'</div></div><span class="pill '+(u.activo?'':'off')+'">'+(u.activo?'Activo':'Inactivo')+'</span></div><div class="actions">'+(!p?'<button class="btn green" data-ucreate="'+u.id+'">Crear contraseña</button>':'')+'<button class="btn blue" data-uedit="'+u.id+'">Editar rol</button><button class="btn '+(u.activo?'orange':'green')+'" data-utoggle="'+u.id+'">'+(u.activo?'Desactivar':'Activar')+'</button></div></div>'}).join('')||'<div class="muted">No hay usuarios autorizados.</div>';
document.querySelectorAll('[data-ucreate]').forEach(b=>b.onclick=()=>prepareUserCreate(b.dataset.ucreate));document.querySelectorAll('[data-uedit]').forEach(b=>b.onclick=()=>editUser(b.dataset.uedit));document.querySelectorAll('[data-utoggle]').forEach(b=>b.onclick=()=>toggleUser(b.dataset.utoggle));
}
function prepareUserCreate(id){const u=authorized.find(x=>x.id===id);if(!u)return;document.getElementById('uname').value=u.nombre||'';document.getElementById('uemail').value=u.email||'';document.getElementById('urole').value=u.rol||'relevador';document.getElementById('upassword').value='';document.getElementById('upassword').focus();scrollTo({top:0,behavior:'smooth'})}
async function saveUser(ev){ev.preventDefault();const email=document.getElementById('uemail').value.trim().toLowerCase(),nombre=document.getElementById('uname').value.trim(),rol=document.getElementById('urole').value,password=document.getElementById('upassword').value;const existing=profiles.find(x=>(x.email||'').toLowerCase()===email);if(!existing&&password.length<8)return alert('Para crear una cuenta nueva, ingresá una contraseña de al menos 8 caracteres.');busyUser(true);try{const r=await db.functions.invoke('crear-usuario-patrimonial',{body:{email,nombre,rol,password}});if(r.error)throw r.error;if(r.data?.error)throw new Error(r.data.error);await refresh(r.data?.created?'Usuario creado. Ya puede ingresar con el correo y la contraseña que cargaste.':'Usuario actualizado. La cuenta ya existía.')}catch(err){alert('No se pudo guardar el usuario: '+(err.message||err))}finally{busyUser(false)}}
function busyUser(on){const b=document.querySelector('#uform button[type="submit"],#uform button');if(b){b.disabled=on;b.textContent=on?'Creando usuario...':'Crear / actualizar usuario'}}
async function editUser'''

a = sub_once(a, r"function renderUsers\(\)\{.*?\nasync function editUser", new_users, 'usuarios con contraseña')
p.write_text(a, encoding='utf-8')

# ---------------- index.html ----------------
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Mostrar unidades en panel general.
s = replace_all_checked(
    s,
    "<span class=\"pill\">'+c.r+' bienes</span>",
    "<span class=\"pill\">'+c.r+' registros</span><span class=\"pill\">'+c.u+' unidades</span>",
    'conteo de unidades en panel',
    1
)

# Mostrar cantidad en inventario público.
s = replace_all_checked(
    s,
    "[x.codigo?('Código '+x.codigo):'',x.marca,x.modelo,x.color]",
    "[Number(x.cantidad||1)+' unidad'+(Number(x.cantidad||1)===1?'':'es'),x.codigo?('Código '+x.codigo):'',x.marca,x.modelo,x.color]",
    'cantidad inventario público',
    1
)

# Mostrar cantidad tanto en bienes actuales como pendientes del relevamiento.
s = replace_all_checked(
    s,
    "[g.codigo?('Código '+g.codigo):'',g.marca,g.modelo,g.color]",
    "[Number(g.cantidad||1)+' unidad'+(Number(g.cantidad||1)===1?'':'es'),g.codigo?('Código '+g.codigo):'',g.marca,g.modelo,g.color]",
    'cantidad relevamiento',
    2
)

s = s.replace("descripcion:'Foto del bien'", "descripcion:'Foto del bien / conjunto'")
s = s.replace('Fotos del bien: ', 'Fotos del bien / conjunto: ')

new_good = r'''async function newGood(){app.innerHTML='<div class="hero"><small>BIEN NUEVO DETECTADO</small><h2>'+e(office.nombre)+'</h2><small>Podés registrar varias unidades iguales en una sola carga.</small></div><div class="card"><form id="newgoodform"><div class="field"><label>Descripción</label><input id="ngdesc" required placeholder="Ej.: Handy Motorola modelo X"></div><div class="field"><label>Cantidad de unidades</label><input id="ngqty" type="number" min="1" max="100000" step="1" value="1" required></div><div class="field"><label>Observaciones / detalle del conjunto</label><textarea id="ngobs" placeholder="Ej.: 10 handies iguales, mismo modelo. Se tomó una foto individual y una foto general del lote."></textarea></div><div class="hint">Ejemplo: si hay 10 handies iguales, cargá cantidad 10. Se crea un solo registro patrimonial y después podés adjuntar una foto de un equipo y otra foto general de las 10 unidades.</div><div class="actions"><button class="btn green">Guardar detección</button><button id="cancelnewgood" type="button" class="btn ghost">Cancelar</button></div></form></div>';document.getElementById('cancelnewgood').onclick=renderRel;document.getElementById('newgoodform').onsubmit=async ev=>{ev.preventDefault();const d=document.getElementById('ngdesc').value.trim(),cantidad=Number(document.getElementById('ngqty').value),observaciones=document.getElementById('ngobs').value.trim();if(!d)return;if(!Number.isInteger(cantidad)||cantidad<1)return alert('La cantidad debe ser un número mayor a 0.');const r=await db.from('relevamiento_novedades').insert({relevamiento_id:rel.id,tipo:'bien_nuevo',descripcion:d,datos:{oficina_id:office.id,oficina:office.nombre,cantidad,observaciones:observaciones||null}});if(r.error){alert(r.error.message);return}await loadNewFinds();renderRel();alert('Bien nuevo detectado: '+cantidad+' unidad'+(cantidad===1?'':'es')+'. Quedó pendiente de revisión.')}}
async function promoteNewFind'''
s = sub_once(s, r"async function newGood\(\)\{.*?\nasync function promoteNewFind", new_good, 'formulario de bien nuevo')

new_promote = r'''async function promoteNewFind(id){const n=newFinds.find(x=>x.id===id);if(!n)return;if(n.resuelta&&n.bien_id){alert('Este bien ya fue incorporado al inventario.');return}if(!states.length)await loadStates();const q0=Number(n.datos?.cantidad||1);app.innerHTML='<div class="hero"><small>INCORPORAR BIEN NUEVO</small><h2>'+e(n.descripcion||'Bien nuevo')+'</h2><small>'+e(office.nombre)+'</small></div><div class="card"><div class="field"><label>Cantidad de unidades</label><input id="initialqty" type="number" min="1" max="100000" step="1" value="'+e(q0)+'" required></div><div class="field"><label>Estado inicial del conjunto</label><select id="initialstate" required>'+stateOptions('')+'</select></div>'+(n.datos?.observaciones?'<div class="hint"><b>Observaciones:</b> '+e(n.datos.observaciones)+'</div>':'')+'<div class="hint">Se incorporará como un solo registro con la cantidad indicada. Después podés sacar una foto de una unidad y otra foto general del conjunto; ambas quedan vinculadas al mismo registro.</div><div class="actions"><button id="confirmnew" class="btn green">Agregar al inventario</button><button id="cancelnew" class="btn ghost">Cancelar</button></div></div>';document.getElementById('cancelnew').onclick=renderRel;document.getElementById('confirmnew').onclick=()=>confirmPromoteNewFind(id)}
async function confirmPromoteNewFind'''
s = sub_once(s, r"async function promoteNewFind\(id\)\{.*?\nasync function confirmPromoteNewFind", new_promote, 'confirmación de cantidad')

new_confirm = r'''async function confirmPromoteNewFind(id){const n=newFinds.find(x=>x.id===id),estadoId=document.getElementById('initialstate').value,cantidad=Number(document.getElementById('initialqty').value);if(!n)return;if(!estadoId){alert('Elegí el estado inicial del bien.');return}if(!Number.isInteger(cantidad)||cantidad<1){alert('La cantidad debe ser un número mayor a 0.');return}const estado=states.find(x=>x.id===estadoId);if(!confirm('¿Agregar “'+(n.descripcion||'Bien nuevo')+'” como '+cantidad+' unidad'+(cantidad===1?'':'es')+' con estado “'+(estado?.nombre||'seleccionado')+'”?'))return;busy('Agregando bien al inventario...');try{const r=await db.rpc('incorporar_bien_nuevo_relevamiento',{p_novedad_id:id,p_estado_id:estadoId,p_cantidad:cantidad});if(r.error)throw r.error;await loadOffice();await loadItems();await loadNewFinds();renderRel();alert('Bien agregado: '+cantidad+' unidad'+(cantidad===1?'':'es')+' en un solo registro, con estado '+(estado?.nombre||'seleccionado')+'. Ahora podés adjuntar las fotos del equipo/conjunto.')}catch(err){alert('No se pudo agregar el bien: '+(err.message||err))}finally{unbusy()}}
async function removeNewFind'''
s = sub_once(s, r"async function confirmPromoteNewFind\(id\)\{.*?\nasync function removeNewFind", new_confirm, 'rpc con cantidad')

# Mostrar cantidad y observación en la lista de novedades nuevas.
old_newfind = "<div class=\"isub\">'+(added?'Incorporado al inventario':'Pendiente de revisión')+' · '+e(new Date(n.created_at).toLocaleString('es-AR'))+'</div>"
new_newfind = "<div class=\"isub\">'+Number(n.datos?.cantidad||1)+' unidad'+(Number(n.datos?.cantidad||1)===1?'':'es')+' · '+(added?'Incorporado al inventario':'Pendiente de revisión')+' · '+e(new Date(n.created_at).toLocaleString('es-AR'))+'</div>"
s = replace_all_checked(s, old_newfind, new_newfind, 'cantidad en novedades', 1)
old_added = "</span></div>'+(added?'<div class=\"isub\" style=\"margin-top:8px\">Este bien ya figura arriba en los bienes de la oficina.</div>':'<div class=\"actions\">"
new_added = "</span></div>'+(n.datos?.observaciones?'<div class=\"isub\" style=\"margin-top:8px\"><b>Obs.:</b> '+e(n.datos.observaciones)+'</div>':'')+(added?'<div class=\"isub\" style=\"margin-top:8px\">Este bien ya figura arriba en los bienes de la oficina.</div>':'<div class=\"actions\">"
s = replace_all_checked(s, old_added, new_added, 'observación en novedades', 1)

# Validaciones finales.
for marker in [
    "p_cantidad:cantidad",
    "Cantidad de unidades",
    "Foto del bien / conjunto",
    "c.u+' unidades",
    "crear-usuario-patrimonial",
    "Contraseña inicial",
]:
    target = a if marker in ['crear-usuario-patrimonial','Contraseña inicial'] else s
    if marker not in target:
        raise SystemExit(f'Falta marcador final: {marker}')

p.write_text(s, encoding='utf-8')
