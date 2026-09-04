from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="let session=null,profile=null,office=null,current=[],pending=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={};"
new="let session=null,profile=null,office=null,current=[],pending=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={},relSearch='',relScrollY=0;"
assert old in s, 'No se encontró la línea de estado global'
s=s.replace(old,new,1)

helper="""function relSearchText(x){return [x?.descripcion,x?.codigo,x?.marca,x?.modelo,x?.color,x?.numero_serie_patente,x?.estados?.nombre,x?.datos?.observaciones].filter(Boolean).join(' ').toLowerCase()}
function applyRelFilter(value=''){relSearch=String(value||'');const term=relSearch.trim().toLowerCase();document.querySelectorAll('[data-rel-search]').forEach(el=>{el.style.display=!term||String(el.dataset.relSearch||'').includes(term)?'':'none'})}
function rememberRelView(){const q=document.getElementById('relsearch');if(q)relSearch=q.value;relScrollY=window.scrollY||document.documentElement.scrollTop||0}
function restoreRelView(){const q=document.getElementById('relsearch');if(q){q.value=relSearch;q.oninput=ev=>applyRelFilter(ev.target.value)}applyRelFilter(relSearch);requestAnimationFrame(()=>window.scrollTo({top:relScrollY,left:0,behavior:'auto'}))}
"""
assert 'function renderRel(){' in s
s=s.replace('function renderRel(){',helper+'function renderRel(){',1)

oldseg='<div class="title">Bienes de esta oficina</div><div class="muted">Solo se guarda lo que revises en este relevamiento. Los bienes que no toques conservan su último control.</div><div id="cur"></div>'
newseg='<div class="title">Bienes de esta oficina</div><div class="muted">Solo se guarda lo que revises en este relevamiento. Los bienes que no toques conservan su último control.</div><input id="relsearch" class="search" placeholder="Buscar bien por descripción, código, marca, modelo..." value="'+e(relSearch)+'" style="margin:10px 0"><div id="cur"></div>'
assert oldseg in s, 'No se encontró cabecera de bienes'
s=s.replace(oldseg,newseg,1)

oldcur="document.getElementById('cur').innerHTML=current.map(g=>{const x=it(g.id),photos=goodPhotos[g.id]||[];return '<div class=\"item\">"
newcur="document.getElementById('cur').innerHTML=current.map(g=>{const x=it(g.id),photos=goodPhotos[g.id]||[];return '<div class=\"item\" data-rel-search=\"'+e(relSearchText(g))+'\">"
assert oldcur in s, 'No se encontró listado actual'
s=s.replace(oldcur,newcur,1)

oldpen="document.getElementById('pen').innerHTML=pending.map(g=>'<div class=\"item\">"
newpen="document.getElementById('pen').innerHTML=pending.map(g=>'<div class=\"item\" data-rel-search=\"'+e(relSearchText(g))+'\">"
assert oldpen in s, 'No se encontró listado pendiente'
s=s.replace(oldpen,newpen,1)

oldnew="document.getElementById('newfinds').innerHTML=newFinds.map(n=>{const added=n.resuelta&&n.bien_id;return '<div class=\"item\">"
newnew="document.getElementById('newfinds').innerHTML=newFinds.map(n=>{const added=n.resuelta&&n.bien_id;return '<div class=\"item\" data-rel-search=\"'+e(relSearchText(n))+'\">"
assert oldnew in s, 'No se encontró listado de novedades'
s=s.replace(oldnew,newnew,1)

needle="document.getElementById('new').onclick=newGood;"
assert needle in s, 'No se encontró enlace de nuevo bien'
s=s.replace(needle,"restoreRelView();document.getElementById('new').onclick=newGood;",1)

repls={
"async function addGoodPhoto(id,source='gallery'){":"async function addGoodPhoto(id,source='gallery'){rememberRelView();",
"function changeStateForm(id){":"function changeStateForm(id){rememberRelView();",
"async function mark(id,res,extra={}){":"async function mark(id,res,extra={}){rememberRelView();",
"function obsForm(id){":"function obsForm(id){rememberRelView();",
"async function here(id){":"async function here(id){rememberRelView();",
"async function moveGood(id){":"async function moveGood(id){rememberRelView();",
"async function newGood(){":"async function newGood(){rememberRelView();",
"async function promoteNewFind(id){":"async function promoteNewFind(id){rememberRelView();"
}
for a,b in repls.items():
    assert a in s, f'No se encontró {a}'
    s=s.replace(a,b,1)

oldgallery="document.querySelectorAll('[data-photosee]').forEach(b=>b.onclick=()=>{const g=current.find(x=>x.id===b.dataset.photosee);gallery(g?.descripcion||'Fotos del bien',goodPhotos[b.dataset.photosee]||[],'good',renderRel,b.dataset.photosee)});"
newgallery="document.querySelectorAll('[data-photosee]').forEach(b=>b.onclick=()=>{rememberRelView();const g=current.find(x=>x.id===b.dataset.photosee);gallery(g?.descripcion||'Fotos del bien',goodPhotos[b.dataset.photosee]||[],'good',renderRel,b.dataset.photosee)});"
assert oldgallery in s, 'No se encontró handler de galería'
s=s.replace(oldgallery,newgallery,1)

pattern=r"async function saveObservation\(id,source=null\)\{.*?\}\nasync function here\(id\)\{"
m=re.search(pattern,s,flags=re.S)
assert m, 'No se encontró saveObservation'
newobs="""async function saveObservation(id,source=null){rememberRelView();const text=document.getElementById('obstext').value.trim(),oldPath=it(id).foto_url||null;let photoPath=oldPath,u=null;if(source){try{u=await uploadPhoto('relevamientos/'+rel.id+'/observaciones/'+id,source)}catch(err){alert('No se pudo agregar la foto: '+(err.message||err));return}if(!u)return;photoPath=u.path}if(!text&&!photoPath){alert('Escribí una observación o agregá una foto.');return}const r=await db.from('relevamiento_items').upsert({relevamiento_id:rel.id,bien_id:id,resultado:'observado',observaciones:text||null,oficina_observada_id:office.id,verificado_en:new Date().toISOString(),foto_url:photoPath},{onConflict:'relevamiento_id,bien_id'});if(r.error){if(u)await db.storage.from(BUCKET).remove([u.path]);alert(r.error.message);return}if(u&&oldPath&&oldPath!==u.path)await db.storage.from(BUCKET).remove([oldPath]);await loadItems();renderRel();alert(u?(text?'Observación y foto de evidencia guardadas.':'Foto de evidencia guardada.'):'Observación guardada.')}
async function here(id){"""
s=s[:m.start()]+newobs+s[m.end():]

# Mejora el texto del formulario para dejar claro que la foto puede guardarse sola.
s=s.replace('Podés guardar solamente el texto o adjuntar una foto como evidencia.','Podés guardar texto, una foto sola o texto + foto como evidencia.',1)
s=s.replace('📷 Guardar + cámara','📷 Sacar foto y guardar',1)
s=s.replace('🖼️ Guardar + subir foto','🖼️ Subir foto y guardar',1)

p.write_text(s,encoding='utf-8')
print('Parche aplicado correctamente')
