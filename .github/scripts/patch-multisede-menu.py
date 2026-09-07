from pathlib import Path
import re

# ---------- index.html ----------
p=Path('index.html')
s=p.read_text(encoding='utf-8')

new_home=r'''async function home(){
  if(!session||!profile||!profile.activo){
    app.innerHTML='<div class="hero"><small>SISTEMA PATRIMONIAL</small><h2>Control Patrimonial Municipal</h2><div>Inventario, sedes y relevamientos</div></div><div class="card"><div class="title">Acceso al sistema</div><div class="muted" style="margin:6px 0 12px">El inventario público se abre desde el QR de cada oficina. El personal autorizado puede ingresar al panel general y elegir la sede que necesita administrar.</div><button id="in" class="btn blue" style="width:100%">Acceso personal</button></div>';
    document.getElementById('in').onclick=login;return;
  }
  const params=new URLSearchParams(location.search),sedeId=params.get('sede')||'';
  if(!sedeId){
    const rs=await db.from('sedes').select('id,nombre,direccion,observaciones,activa').eq('activa',true).order('nombre');
    if(rs.error){app.innerHTML='<div class="error">No se pudieron cargar las sedes: '+e(rs.error.message)+'</div>';return}
    const sedesList=rs.data||[];
    let officesAll=[],goods=[];
    if(sedesList.length){
      const ro=await db.from('oficinas').select('id,sede_id').eq('activa',true).in('sede_id',sedesList.map(x=>x.id));
      if(!ro.error)officesAll=ro.data||[];
      if(officesAll.length){const rb=await db.from('bienes').select('oficina_id,cantidad').eq('activo',true).in('oficina_id',officesAll.map(x=>x.id));if(!rb.error)goods=rb.data||[]}
    }
    const stats={};sedesList.forEach(x=>stats[x.id]={o:0,r:0,u:0});
    const officeSede={};officesAll.forEach(o=>{officeSede[o.id]=o.sede_id;if(stats[o.sede_id])stats[o.sede_id].o++});
    goods.forEach(b=>{const sid=officeSede[b.oficina_id];if(stats[sid]){stats[sid].r++;stats[sid].u+=Number(b.cantidad||1)}});
    const totalO=Object.values(stats).reduce((a,x)=>a+x.o,0),totalR=Object.values(stats).reduce((a,x)=>a+x.r,0),totalU=Object.values(stats).reduce((a,x)=>a+x.u,0);
    app.innerHTML='<div class="hero"><small>PANEL GENERAL</small><h2>Control Patrimonial Municipal</h2><div>'+sedesList.length+' sedes · '+totalO+' oficinas / sectores · '+totalR+' registros · '+totalU+' unidades</div></div><div class="between"><input id="sq" class="search" style="flex:1" placeholder="Buscar sede o dependencia...">'+(profile.rol==='admin'?'<a class="btn green" style="text-decoration:none" href="administracion.html#organigrama">Organigrama</a><a class="btn blue" style="text-decoration:none" href="administracion.html#usuarios">Usuarios y roles</a>':'')+'<button id="out" class="btn ghost">Salir</button></div><div id="sites"></div><div class="muted" style="text-align:center;margin:15px">Sesión: '+e(profile.nombre||profile.email||session.user.email)+' · '+e(profile.rol||'usuario')+'</div>';
    function drawSites(t=''){t=String(t||'').toLowerCase();const list=sedesList.filter(x=>[x.nombre,x.direccion].filter(Boolean).join(' ').toLowerCase().includes(t));document.getElementById('sites').innerHTML=list.map(x=>{const c=stats[x.id]||{o:0,r:0,u:0};return '<div class="item"><div class="between"><div><div class="ititle">'+e(x.nombre)+'</div>'+(x.direccion?'<div class="isub">'+e(x.direccion)+'</div>':'')+'</div><div><span class="pill">'+c.o+' oficinas</span> <span class="pill">'+c.r+' registros</span> <span class="pill">'+c.u+' unidades</span></div></div><div class="actions"><button class="btn green" data-site="'+x.id+'">Abrir sede</button></div></div>'}).join('')||'<div class="card muted">No se encontraron sedes.</div>';document.querySelectorAll('[data-site]').forEach(b=>b.onclick=()=>{localStorage.setItem('patrimonio_last_sede',b.dataset.site);location.href=location.origin+location.pathname+'?sede='+encodeURIComponent(b.dataset.site)})}
    drawSites();document.getElementById('sq').oninput=ev=>drawSites(ev.target.value);document.getElementById('out').onclick=async()=>{await db.auth.signOut();session=null;profile=null;home()};return;
  }
  const rs=await db.from('sedes').select('id,nombre,direccion,observaciones,activa').eq('id',sedeId).eq('activa',true).maybeSingle();
  if(rs.error||!rs.data){location.replace(location.origin+location.pathname);return}
  const sede=rs.data;localStorage.setItem('patrimonio_last_sede',sede.id);
  const ro=await db.from('oficinas').select('id,nombre,slug_qr,referencia,area_id,sede_id,areas(nombre)').eq('activa',true).eq('sede_id',sede.id).order('nombre');
  if(ro.error){app.innerHTML='<div class="error">No se pudieron cargar las oficinas: '+e(ro.error.message)+'</div>';return}
  const offices=ro.data||[];let counts={};
  if(offices.length){const ids=offices.map(o=>o.id),rb=await db.from('bienes').select('oficina_id,cantidad').eq('activo',true).in('oficina_id',ids);if(!rb.error)(rb.data||[]).forEach(b=>{if(!counts[b.oficina_id])counts[b.oficina_id]={r:0,u:0};counts[b.oficina_id].r++;counts[b.oficina_id].u+=Number(b.cantidad||1)})}
  const totalReg=Object.values(counts).reduce((a,x)=>a+x.r,0),totalUni=Object.values(counts).reduce((a,x)=>a+x.u,0);
  app.innerHTML='<div class="hero"><small>SEDE / DEPENDENCIA</small><h2>'+e(sede.nombre)+'</h2><div>'+offices.length+' oficinas / sectores · '+totalReg+' registros · '+totalUni+' unidades</div></div><div class="between"><input id="hq" class="search" style="flex:1" placeholder="Buscar oficina o área..."><button id="allsites" class="btn ghost">Cambiar sede</button>'+(profile.rol==='admin'?'<a class="btn green" style="text-decoration:none" href="administracion.html#organigrama">Organigrama</a><a class="btn blue" style="text-decoration:none" href="administracion.html#usuarios">Usuarios y roles</a>':'')+'<button id="out" class="btn ghost">Salir</button></div><div id="offices"></div><div class="muted" style="text-align:center;margin:15px">Sesión: '+e(profile.nombre||profile.email||session.user.email)+' · '+e(profile.rol||'usuario')+'</div>';
  function drawHome(t=''){t=String(t||'').toLowerCase();document.getElementById('offices').innerHTML=offices.filter(o=>JSON.stringify(o).toLowerCase().includes(t)).map(o=>{const c=counts[o.id]||{r:0,u:0},area=o.areas?.nombre||'';return '<div class="item"><div class="between"><div><div class="ititle">'+e(o.nombre)+'</div><div class="isub">'+e(area)+'</div></div><span class="pill">'+c.r+' registros</span><span class="pill">'+c.u+' unidades</span></div>'+(o.referencia?'<div class="isub">'+e(o.referencia)+'</div>':'')+'<div class="actions"><button class="btn green" data-open="'+e(o.slug_qr)+'">Abrir inventario / relevamiento</button><button class="btn blue" data-qr="'+e(o.slug_qr)+'">Ver QR / Imprimir</button></div></div>'}).join('')||'<div class="card muted">No se encontraron oficinas.</div>';document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>{localStorage.setItem('patrimonio_last_sede',sede.id);location.href=location.origin+location.pathname+'?qr='+encodeURIComponent(b.dataset.open)});document.querySelectorAll('[data-qr]').forEach(b=>b.onclick=()=>{const o=offices.find(x=>x.slug_qr===b.dataset.qr);if(o)showOfficeQR({nombre:o.nombre,area:o.areas?.nombre||'',sede:sede.nombre,slug_qr:o.slug_qr},()=>home())})}
  drawHome();document.getElementById('hq').oninput=ev=>drawHome(ev.target.value);document.getElementById('allsites').onclick=()=>location.href=location.origin+location.pathname;document.getElementById('out').onclick=async()=>{await db.auth.signOut();session=null;profile=null;home()};
}'''

pat=r"async function home\(\)\{.*?\nasync function pub"
m=re.search(pat,s,flags=re.S)
if not m: raise SystemExit('No se encontró función home')
s=s[:m.start()]+new_home+'\nasync function pub'+s[m.end():]

old='<button id="panel" class="btn ghost">Panel del edificio</button><button id="qrview" class="btn blue">Ver QR / Imprimir</button>'
new='<button id="panel" class="btn ghost">Panel de sede</button><button id="allsites" class="btn ghost">Cambiar sede</button><button id="qrview" class="btn blue">Ver QR / Imprimir</button>'
if old not in s: raise SystemExit('No se encontró botones de panel en pub')
s=s.replace(old,new,1)
oldh="if(document.getElementById('panel'))document.getElementById('panel').onclick=()=>location.href=location.origin+location.pathname;"
newh="if(document.getElementById('panel'))document.getElementById('panel').onclick=()=>{const sid=localStorage.getItem('patrimonio_last_sede')||'';location.href=location.origin+location.pathname+(sid?'?sede='+encodeURIComponent(sid):'')};if(document.getElementById('allsites'))document.getElementById('allsites').onclick=()=>location.href=location.origin+location.pathname;"
if oldh not in s: raise SystemExit('No se encontró handler panel')
s=s.replace(oldh,newh,1)
p.write_text(s,encoding='utf-8')

# ---------- administracion.html ----------
p=Path('administracion.html')
s=p.read_text(encoding='utf-8')
new_edit=r'''async function editOfficeFromOrg(id){const o=offices.find(x=>x.id===id);if(!o)return;const name=prompt('Nombre de la oficina / sector:',o.nombre);if(!name||!name.trim())return;const list=areas.filter(a=>a.activo);let msg='¿De qué área depende esta oficina?\n';list.forEach((x,i)=>msg+=(i+1)+' - '+x.nombre+'\n');const cur=Math.max(1,list.findIndex(x=>x.id===o.area_id)+1),n=prompt(msg,String(cur));if(n===null)return;const ix=Number(n)-1;if(!list[ix])return alert('Área no válida.');const sl=sedes.filter(x=>x.activa);let smsg='¿En qué sede / edificio está físicamente esta oficina?\n';sl.forEach((x,i)=>smsg+=(i+1)+' - '+x.nombre+'\n');const scur=Math.max(1,sl.findIndex(x=>x.id===o.sede_id)+1),sn=prompt(smsg,String(scur));if(sn===null)return;const six=Number(sn)-1;if(!sl[six])return alert('Sede no válida.');const ref=prompt('Referencia física / ubicación:',o.referencia||'');if(ref===null)return;const r=await db.from('oficinas').update({nombre:name.trim(),area_id:list[ix].id,sede_id:sl[six].id,referencia:ref.trim()||null}).eq('id',id);if(r.error)return alert(r.error.message);await refresh('Oficina actualizada desde el organigrama. El QR no cambió.')}'''
pat=r"async function editOfficeFromOrg\(id\)\{.*?\nasync function assignFromOrg"
m=re.search(pat,s,flags=re.S)
if not m: raise SystemExit('No se encontró editOfficeFromOrg')
s=s[:m.start()]+new_edit+'\nasync function assignFromOrg'+s[m.end():]
p.write_text(s,encoding='utf-8')
print('Parche multi-sede aplicado')
