from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="let session=null,profile=null,office=null,current=[],pending=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={},relSearch='',relScrollY=0;"
new="let session=null,profile=null,office=null,current=[],pending=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={},relSearch='',relStateFilter='',relResultFilter='',relScrollY=0;"
assert old in s, 'No se encontró el estado global esperado'
s=s.replace(old,new,1)

oldsel="select('id,codigo,descripcion,marca,modelo,color,cantidad,oficina_id,area_responsable_id,estado_id,estados(nombre)')"
newsel="select('id,codigo,descripcion,marca,modelo,color,numero_serie_patente,cantidad,oficina_id,area_responsable_id,estado_id,estados(nombre)')"
assert s.count(oldsel)>=2, 'No se encontraron las consultas de bienes esperadas'
s=s.replace(oldsel,newsel,2)

oldhelpers="""function relSearchText(x){return [x?.descripcion,x?.codigo,x?.marca,x?.modelo,x?.color,x?.numero_serie_patente,x?.estados?.nombre,x?.datos?.observaciones].filter(Boolean).join(' ').toLowerCase()}
function applyRelFilter(value=''){relSearch=String(value||'');const term=relSearch.trim().toLowerCase();document.querySelectorAll('[data-rel-search]').forEach(el=>{el.style.display=!term||String(el.dataset.relSearch||'').includes(term)?'':'none'})}
function rememberRelView(){const q=document.getElementById('relsearch');if(q)relSearch=q.value;relScrollY=window.scrollY||document.documentElement.scrollTop||0}
function restoreRelView(){const q=document.getElementById('relsearch');if(q){q.value=relSearch;q.oninput=ev=>applyRelFilter(ev.target.value)}applyRelFilter(relSearch);requestAnimationFrame(()=>window.scrollTo({top:relScrollY,left:0,behavior:'auto'}))}
"""
newhelpers="""function relSearchText(x){return [x?.descripcion,x?.codigo,x?.marca,x?.modelo,x?.color,x?.numero_serie_patente,x?.estados?.nombre,x?.datos?.observaciones].filter(Boolean).join(' ').toLowerCase()}
function stateFilterOptions(){return '<option value="">Todos los estados</option><option value="none" '+(relStateFilter==='none'?'selected':'')+'>Sin estado</option>'+states.map(x=>'<option value="'+e(x.id)+'" '+(relStateFilter===x.id?'selected':'')+'>'+e(x.nombre)+'</option>').join('')}
function resultFilterOptions(){const opts=[['','Todos los resultados'],['sin_revisar','Sin revisar en este relevamiento'],['encontrado','Encontrado'],['faltante','Faltante'],['observado','Observado'],['pendiente_ubicar','Pendiente de ubicar'],['bien_nuevo','Bien nuevo detectado'],['incorporado','Incorporado desde detección']];return opts.map(x=>'<option value="'+x[0]+'" '+(relResultFilter===x[0]?'selected':'')+'>'+x[1]+'</option>').join('')}
function applyRelFilters(){const term=relSearch.trim().toLowerCase(),state=relStateFilter,result=relResultFilter;let visible=0,total=0;document.querySelectorAll('[data-rel-search]').forEach(el=>{total++;const okSearch=!term||String(el.dataset.relSearch||'').includes(term),okState=!state||String(el.dataset.relState||'none')===state,okResult=!result||String(el.dataset.relResult||'sin_revisar')===result,show=okSearch&&okState&&okResult;el.style.display=show?'':'none';if(show)visible++});const c=document.getElementById('relfiltercount');if(c)c.textContent=(term||state||result)?visible+' coincidencia'+(visible===1?'':'s')+' de '+total:total+' bienes / registros visibles'}
function applyRelFilter(value=''){relSearch=String(value||'');applyRelFilters()}
function rememberRelView(){const q=document.getElementById('relsearch'),sf=document.getElementById('relstate'),rf=document.getElementById('relresult');if(q)relSearch=q.value;if(sf)relStateFilter=sf.value;if(rf)relResultFilter=rf.value;relScrollY=window.scrollY||document.documentElement.scrollTop||0}
function restoreRelView(){const q=document.getElementById('relsearch'),sf=document.getElementById('relstate'),rf=document.getElementById('relresult'),cl=document.getElementById('clearrelfilters');if(q){q.value=relSearch;q.oninput=ev=>{relSearch=ev.target.value;applyRelFilters()}}if(sf){sf.value=relStateFilter;sf.onchange=ev=>{relStateFilter=ev.target.value;applyRelFilters()}}if(rf){rf.value=relResultFilter;rf.onchange=ev=>{relResultFilter=ev.target.value;applyRelFilters()}}if(cl)cl.onclick=()=>{relSearch='';relStateFilter='';relResultFilter='';if(q)q.value='';if(sf)sf.value='';if(rf)rf.value='';applyRelFilters()};applyRelFilters();requestAnimationFrame(()=>window.scrollTo({top:relScrollY,left:0,behavior:'auto'}))}
"""
assert oldhelpers in s, 'No se encontró el bloque actual de búsqueda'
s=s.replace(oldhelpers,newhelpers,1)

oldsearch='<input id="relsearch" class="search" placeholder="Buscar bien por descripción, código, marca, modelo..." value="\'+e(relSearch)+\'" style="margin:10px 0"><div id="cur"></div>'
newsearch='<div class="card" style="padding:10px;margin:10px 0"><input id="relsearch" class="search" placeholder="Buscar por descripción, código, marca, modelo, serie o patente..." value="\'+e(relSearch)+\'"><div class="row" style="margin-top:8px"><select id="relstate" style="flex:1 1 220px;width:auto">\'+stateFilterOptions()+\'</select><select id="relresult" style="flex:1 1 220px;width:auto">\'+resultFilterOptions()+\'</select><button id="clearrelfilters" class="btn ghost" type="button">Limpiar filtros</button></div><div id="relfiltercount" class="muted" style="margin-top:7px"></div></div><div id="cur"></div>'
assert oldsearch in s, 'No se encontró el buscador del relevamiento'
s=s.replace(oldsearch,newsearch,1)

oldcur="return '<div class=\"item\" data-rel-search=\"'+e(relSearchText(g))+'\">"
newcur="return '<div class=\"item\" data-rel-search=\"'+e(relSearchText({...g,datos:{observaciones:x.observaciones||''}}))+'\" data-rel-state=\"'+e(g.estado_id||'none')+'\" data-rel-result=\"'+e(x.resultado||'sin_revisar')+'\">"
assert oldcur in s, 'No se encontró la tarjeta de bien actual'
s=s.replace(oldcur,newcur,1)

oldpen="pending.map(g=>'<div class=\"item\" data-rel-search=\"'+e(relSearchText(g))+'\">"
newpen="pending.map(g=>'<div class=\"item\" data-rel-search=\"'+e(relSearchText(g))+'\" data-rel-state=\"'+e(g.estado_id||'none')+'\" data-rel-result=\"pendiente_ubicar\">"
assert oldpen in s, 'No se encontró la tarjeta pendiente'
s=s.replace(oldpen,newpen,1)

oldnew="return '<div class=\"item\" data-rel-search=\"'+e(relSearchText(n))+'\">"
newnew="return '<div class=\"item\" data-rel-search=\"'+e(relSearchText(n))+'\" data-rel-state=\"none\" data-rel-result=\"'+(added?'incorporado':'bien_nuevo')+'\">"
assert oldnew in s, 'No se encontró la tarjeta de bien nuevo'
s=s.replace(oldnew,newnew,1)

# Mostrar serie/patente también en las tarjetas del relevamiento.
oldmeta="g.marca,g.modelo,g.color].filter(Boolean).join(' · '))"
newmeta="g.marca,g.modelo,g.color,g.numero_serie_patente?('Serie/Patente '+g.numero_serie_patente):''].filter(Boolean).join(' · '))"
assert s.count(oldmeta)>=2, 'No se encontraron los metadatos esperados de bienes'
s=s.replace(oldmeta,newmeta,2)

p.write_text(s,encoding='utf-8')
print('Filtros del relevamiento aplicados correctamente')
