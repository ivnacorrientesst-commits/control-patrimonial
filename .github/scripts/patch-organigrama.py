from pathlib import Path
import re


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"No se encontró bloque: {label}")
    return text.replace(old, new, 1)


# ---------------- index.html ----------------
p = Path("index.html")
s = p.read_text(encoding="utf-8")
old = "'+(profile.rol==='admin'?'<a class=\"btn blue\" style=\"text-decoration:none\" href=\"administracion.html#usuarios\">Usuarios y roles</a>':'')+'<button id=\"out\" class=\"btn ghost\">Salir</button>"
new = "'+(profile.rol==='admin'?'<a class=\"btn green\" style=\"text-decoration:none\" href=\"administracion.html#organigrama\">Organigrama</a><a class=\"btn blue\" style=\"text-decoration:none\" href=\"administracion.html#usuarios\">Usuarios y roles</a>':'')+'<button id=\"out\" class=\"btn ghost\">Salir</button>"
s = replace_once(s, old, new, "botones de administración en panel general")
p.write_text(s, encoding="utf-8")


# ------------- administracion.html ---------
p = Path("administracion.html")
a = p.read_text(encoding="utf-8")

a = replace_once(
    a,
    "let tab=location.hash==='#usuarios'?'usuarios':'organigrama';",
    "const validTabs=['organigrama','oficinas','usuarios','responsables'];let tab=validTabs.includes(location.hash.slice(1))?location.hash.slice(1):'organigrama';",
    "hash de pestañas",
)

a = replace_once(
    a,
    ".link{color:#1971c2;text-decoration:none;font-weight:800}@media(max-width:700px)",
    ".link{color:#1971c2;text-decoration:none;font-weight:800}.org-office{margin:8px 0 0 18px;padding:10px 12px;border-left:3px solid #74c0fc;background:#f8fbff;border-radius:10px}.org-meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.org-section{margin-top:10px;padding-top:8px;border-top:1px solid #edf2f4}@media(max-width:700px)",
    "estilos del organigrama",
)

a = replace_once(
    a,
    '<h2 style="margin:4px 0">Organigrama y configuración</h2><div>Los cambios de nombre se reflejan automáticamente en todo el sistema.</div>',
    '<h2 style="margin:4px 0">Organigrama central y configuración</h2><div>Dependencias, oficinas y encargados se administran desde un solo lugar y los cambios se reflejan en todo el sistema.</div>',
    "cabecera del organigrama",
)

new_block = r'''function currentAssign(type,id){return assignments.find(x=>!x.fecha_hasta&&(type==='area'?(x.area_id===id&&!x.oficina_id):x.oficina_id===id))||null}
function renderAreas(){
const v=document.getElementById('view');
v.innerHTML='<div class="grid"><div class="card"><div class="title">Nueva área / dependencia</div><form id="newarea"><div class="field"><label>Nombre</label><input id="aname" required placeholder="Ej.: Dirección de Personal"></div><div class="grid"><div class="field"><label>Tipo</label><input id="atype" placeholder="Secretaría, Dirección, Coordinación..."></div><div class="field"><label>Depende de</label><select id="aparent">'+areaOptions()+'</select></div></div><button class="btn green">Crear área</button></form></div><div class="card"><div class="title">Nuevo responsable / encargado</div><div class="muted">Después lo asignás directamente a un área u oficina desde el organigrama de abajo.</div><form id="rform"><div class="field"><label>Nombre</label><input id="rname" required></div><div class="grid"><div class="field"><label>Cargo</label><input id="rcargo" placeholder="Director, Secretario, encargado..."></div><div class="field"><label>Documento (opcional)</label><input id="rdoc"></div></div><button class="btn green">Guardar responsable</button></form></div></div><div class="card"><div class="title">Organigrama municipal</div><div class="muted">Este es el punto central de configuración. Si cambiás el nombre de un área, su dependencia, una oficina o su encargado, el sistema usa el dato actualizado sin cambiar los QR ni perder historial.</div><div class="muted" style="margin-top:5px">La hoja “Listas” del archivo original queda como referencia inicial de nombres; la estructura vigente se administra acá.</div><div id="alist"></div></div>';
document.getElementById('newarea').onsubmit=async ev=>{ev.preventDefault();const r=await db.from('areas').insert({nombre:document.getElementById('aname').value.trim(),tipo:document.getElementById('atype').value.trim()||null,area_padre_id:document.getElementById('aparent').value||null}).select().single();if(r.error)return alert(r.error.message);await refresh('Área creada.')};
document.getElementById('rform').onsubmit=saveResp;
const roots=areas.filter(a=>!a.area_padre_id||!areas.some(x=>x.id===a.area_padre_id));
const children=id=>areas.filter(a=>a.area_padre_id===id);
function node(a,depth=0){const kids=children(a.id),active=a.activo,aa=currentAssign('area',a.id),ofs=offices.filter(o=>o.area_id===a.id),parent=a.area_padre_id?areas.find(x=>x.id===a.area_padre_id):null;const officeHtml=ofs.map(o=>{const oa=currentAssign('oficina',o.id),c=counts['o:'+o.id]||0;return '<div class="org-office"><div class="between"><div><div class="ititle">'+e(o.nombre)+'</div><div class="isub">Oficina / sector · '+e(o.sedes?.nombre||'Sin sede')+(o.referencia?' · '+e(o.referencia):'')+'</div></div><div><span class="pill">'+c+' bienes</span> <span class="pill '+(o.activa?'':'off')+'">'+(o.activa?'Activa':'Inactiva')+'</span></div></div><div class="org-meta"><span class="pill '+(oa?'':'off')+'">Encargado: '+e(oa?.responsables?.nombre||'Sin asignar')+'</span>'+(oa?.cargo?'<span class="pill">'+e(oa.cargo)+'</span>':'')+'</div><div class="actions"><button class="btn blue" data-orgoedit="'+o.id+'">Editar oficina</button><button class="btn green" data-orgassign="oficina:'+o.id+'">'+(oa?'Cambiar encargado':'Asignar encargado')+'</button>'+(oa?'<button class="btn orange" data-orgend="'+oa.id+'">Finalizar encargado</button>':'')+'<a class="btn ghost" style="text-decoration:none;text-align:center" href="'+base+'?qr='+encodeURIComponent(o.slug_qr)+'">Abrir inventario</a></div></div>'}).join('');return '<div class="item" style="margin-left:'+Math.min(depth*18,72)+'px"><div class="between"><div><div class="ititle">'+e(a.nombre)+'</div><div class="isub">'+e(a.tipo||'Área / dependencia')+(parent?' · depende de '+e(parent.nombre):' · nivel principal')+'</div></div><span class="pill '+(active?'':'off')+'">'+(active?'Activa':'Inactiva')+'</span></div><div class="org-meta"><span class="pill">'+(counts['a:'+a.id]||0)+' bienes responsables</span><span class="pill">'+ofs.length+' oficinas / sectores</span><span class="pill '+(aa?'':'off')+'">Responsable: '+e(aa?.responsables?.nombre||'Sin asignar')+'</span>'+(aa?.cargo?'<span class="pill">'+e(aa.cargo)+'</span>':'')+'</div><div class="actions"><button class="btn blue" data-aedit="'+a.id+'">Editar área / dependencia</button><button class="btn green" data-orgassign="area:'+a.id+'">'+(aa?'Cambiar responsable':'Asignar responsable')+'</button>'+(aa?'<button class="btn orange" data-orgend="'+aa.id+'">Finalizar responsable</button>':'')+'<button class="btn '+(active?'orange':'green')+'" data-atoggle="'+a.id+'">'+(active?'Desactivar':'Activar')+'</button></div>'+(officeHtml?'<div class="org-section"><div class="isub"><b>Oficinas / sectores de esta dependencia</b></div>'+officeHtml+'</div>':'')+'</div>'+kids.map(k=>node(k,depth+1)).join('')}
document.getElementById('alist').innerHTML=roots.map(r=>node(r)).join('')||'<div class="muted">Todavía no hay áreas cargadas.</div>';
document.querySelectorAll('[data-aedit]').forEach(b=>b.onclick=()=>editArea(b.dataset.aedit));document.querySelectorAll('[data-atoggle]').forEach(b=>b.onclick=()=>toggleArea(b.dataset.atoggle));document.querySelectorAll('[data-orgoedit]').forEach(b=>b.onclick=()=>editOfficeFromOrg(b.dataset.orgoedit));document.querySelectorAll('[data-orgassign]').forEach(b=>b.onclick=()=>{const [type,id]=b.dataset.orgassign.split(':');assignFromOrg(type,id)});document.querySelectorAll('[data-orgend]').forEach(b=>b.onclick=()=>endAssign(b.dataset.orgend));
}
async function editOfficeFromOrg(id){const o=offices.find(x=>x.id===id);if(!o)return;const name=prompt('Nombre de la oficina / sector:',o.nombre);if(!name||!name.trim())return;const list=areas.filter(a=>a.activo);let msg='¿De qué área depende esta oficina?\n';list.forEach((x,i)=>msg+=(i+1)+' - '+x.nombre+'\n');const cur=Math.max(1,list.findIndex(x=>x.id===o.area_id)+1),n=prompt(msg,String(cur));if(n===null)return;const ix=Number(n)-1;if(!list[ix])return alert('Área no válida.');const ref=prompt('Referencia física / ubicación:',o.referencia||'');if(ref===null)return;const r=await db.from('oficinas').update({nombre:name.trim(),area_id:list[ix].id,referencia:ref.trim()||null}).eq('id',id);if(r.error)return alert(r.error.message);await refresh('Oficina actualizada desde el organigrama. El QR no cambió.')}
async function assignFromOrg(type,id){const list=responsables.filter(r=>r.activo);if(!list.length)return alert('Primero creá un responsable en el formulario de arriba.');const current=currentAssign(type,id);let msg='Elegí responsable / encargado:\n';list.forEach((x,i)=>msg+=(i+1)+' - '+x.nombre+(x.cargo?' ('+x.cargo+')':'')+'\n');const cur=current?Math.max(1,list.findIndex(x=>x.id===current.responsable_id)+1):1,n=prompt(msg,String(cur));if(n===null)return;const ix=Number(n)-1;if(!list[ix])return alert('Responsable no válido.');const cargo=prompt('Cargo en este destino:',current?.cargo||list[ix].cargo||'Encargado');if(cargo===null)return;const today=new Date().toISOString().slice(0,10);let q=db.from('asignaciones_responsables').update({fecha_hasta:today}).is('fecha_hasta',null);q=type==='area'?q.eq('area_id',id).is('oficina_id',null):q.eq('oficina_id',id);let r=await q;if(r.error)return alert(r.error.message);const data={responsable_id:list[ix].id,cargo:cargo.trim()||null,fecha_desde:today};if(type==='area')data.area_id=id;else data.oficina_id=id;r=await db.from('asignaciones_responsables').insert(data);if(r.error)return alert(r.error.message);await refresh('Responsable / encargado actualizado en el organigrama.')}
'''

pattern = r"function renderAreas\(\)\{.*?\n\}\nasync function editArea"
if not re.search(pattern, a, flags=re.S):
    raise SystemExit("No se encontró renderAreas actual")
a = re.sub(pattern, new_block + "async function editArea", a, count=1, flags=re.S)

for marker in [
    "Organigrama municipal",
    "function currentAssign(type,id)",
    "async function editOfficeFromOrg(id)",
    "async function assignFromOrg(type,id)",
    "La hoja “Listas” del archivo original",
]:
    if marker not in a:
        raise SystemExit(f"Falta validación en administracion.html: {marker}")
if "administracion.html#organigrama" not in s:
    raise SystemExit("Falta botón Organigrama en index.html")

p.write_text(a, encoding="utf-8")
print("Parche de organigrama aplicado correctamente")
