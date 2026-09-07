from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Estilos visuales para faltantes y bajas
old=".pill{display:inline-block;border-radius:999px;padding:5px 8px;background:#e6fcf5;color:#087f5b;font-size:12px;font-weight:800;margin:3px 2px}"
new=old+"\n.missing-title{color:#c92a2a}.inactive-item{opacity:.78;border:1px dashed #adb5bd}.inactive-title{text-decoration:line-through;color:#868e96}"
if old not in s: raise SystemExit('No se encontro estilo pill')
s=s.replace(old,new,1)

# Estado global de bajas
old="let session=null,profile=null,office=null,current=[],pending=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={},relSearch='',relStateFilter='',relResultFilter='',relScrollY=0;"
new="let session=null,profile=null,office=null,current=[],pending=[],inactive=[],rel=null,items=[],officePhotos=[],goodPhotos={},newFinds=[],states=[],lastResults={},relSearch='',relStateFilter='',relResultFilter='',relScrollY=0;"
if old not in s: raise SystemExit('No se encontro estado global')
s=s.replace(old,new,1)

# Cargar activos, pendientes e inactivos de la oficina, incluyendo campos editables
old="async function loadOffice(){const o=await db.from('oficinas').select('id,area_id,nombre,slug_qr,areas(nombre),sedes(nombre)').eq('slug_qr',qr).eq('activa',true).single();if(o.error)throw o.error;office=o.data;const r=await Promise.all([db.from('bienes').select('id,codigo,descripcion,marca,modelo,color,numero_serie_patente,cantidad,oficina_id,area_responsable_id,estado_id,estados(nombre)').eq('activo',true).eq('oficina_id',office.id).order('descripcion'),db.from('bienes').select('id,codigo,descripcion,marca,modelo,color,numero_serie_patente,cantidad,oficina_id,area_responsable_id,estado_id,estados(nombre)').eq('activo',true).eq('area_responsable_id',office.area_id).is('oficina_id',null).order('descripcion')]);current=r[0].data||[];pending=r[1].data||[];await loadPhotoMeta()}"
new="async function loadOffice(){const o=await db.from('oficinas').select('id,area_id,nombre,slug_qr,areas(nombre),sedes(nombre)').eq('slug_qr',qr).eq('activa',true).single();if(o.error)throw o.error;office=o.data;const fields='id,codigo,descripcion,marca,modelo,color,numero_serie_patente,cantidad,observaciones,fecha_baja,activo,oficina_id,area_responsable_id,estado_id,estados(nombre)',r=await Promise.all([db.from('bienes').select(fields).eq('activo',true).eq('oficina_id',office.id).order('descripcion'),db.from('bienes').select(fields).eq('activo',true).eq('area_responsable_id',office.area_id).is('oficina_id',null).order('descripcion'),db.from('bienes').select(fields).eq('activo',false).eq('oficina_id',office.id).order('descripcion')]);current=r[0].data||[];pending=r[1].data||[];inactive=r[2].data||[];await loadPhotoMeta()}"
if old not in s: raise SystemExit('No se encontro loadOffice')
s=s.replace(old,new,1)

# Filtro por resultado incluye eliminados
old="['incorporado','Incorporado desde detección']"
new="['incorporado','Incorporado desde detección'],['eliminado','Eliminado / dado de baja']"
if old not in s: raise SystemExit('No se encontro opcion incorporado')
s=s.replace(old,new,1)

# Helpers de orden según último resultado efectivo
marker="function renderRel(){"
helpers="""function effectiveResult(id){const x=items.find(y=>y.bien_id===id);if(x?.resultado)return x.resultado;return lastResults[id]?.resultado||null}\nfunction resultRank(id){const r=effectiveResult(id);if(r==='encontrado')return 0;if(r==='observado')return 1;if(r==='faltante')return 3;return 2}\nfunction sortedCurrent(){return [...current].sort((a,b)=>resultRank(a.id)-resultRank(b.id)||String(a.descripcion||'').localeCompare(String(b.descripcion||''),'es',{sensitivity:'base'}))}\n"""
if marker not in s: raise SystemExit('No se encontro renderRel')
s=s.replace(marker,helpers+marker,1)

# Sección de eliminados abajo del relevamiento
old="<div id=\"newfinds\"></div><div class=\"row\"><button id=\"back\""
new="<div id=\"newfinds\"></div><div class=\"title\" style=\"margin-top:22px\">Bienes eliminados / dados de baja ('+inactive.length+')</div><div class=\"muted\">Se conservan como historial con sus fotos, movimientos y actas. Podés reactivar un bien si fue dado de baja por error.</div><div id=\"inactive\"></div><div class=\"row\"><button id=\"back\""
if old not in s: raise SystemExit('No se encontro insercion de eliminados')
s=s.replace(old,new,1)

# Ordenar activos por encontrado / otros / faltante
old="document.getElementById('cur').innerHTML=current.map(g=>{"
new="document.getElementById('cur').innerHTML=sortedCurrent().map(g=>{"
if old not in s: raise SystemExit('No se encontro current.map')
s=s.replace(old,new,1)

# Nombre de faltante en rojo
old="<div class=\"ititle\">'+e(g.descripcion)+'</div><div class=\"isub\">'+e([Number(g.cantidad||1)+' unidad'"
new="<div class=\"ititle'+(effectiveResult(g.id)==='faltante'?' missing-title':'')+'\">'+e(g.descripcion)+'</div><div class=\"isub\">'+e([Number(g.cantidad||1)+' unidad'"
if old not in s: raise SystemExit('No se encontro titulo de bien')
s=s.replace(old,new,1)

# Botones Editar y Eliminar
old="<button class=\"btn blue\" data-actas=\"'+g.id+'\">Actas / movimientos</button><button class=\"btn ghost\" data-move=\"'+g.id+'\">Mover a otra oficina</button>"
new="<button class=\"btn ghost\" data-edit=\"'+g.id+'\">Editar bien</button><button class=\"btn red\" data-delete=\"'+g.id+'\">Eliminar</button><button class=\"btn blue\" data-actas=\"'+g.id+'\">Actas / movimientos</button><button class=\"btn ghost\" data-move=\"'+g.id+'\">Mover a otra oficina</button>"
if old not in s: raise SystemExit('No se encontraron botones actas/mover')
s=s.replace(old,new,1)

# Render de eliminados antes de registrar listeners
marker="document.querySelectorAll('[data-f]').forEach"
inactive_render="""document.getElementById('inactive').innerHTML=inactive.length?inactive.map(g=>'<div class=\"item inactive-item\" data-rel-search=\"'+e(relSearchText(g))+'\" data-rel-state=\"'+e(g.estado_id||'none')+'\" data-rel-result=\"eliminado\"><div class=\"between\"><div><div class=\"ititle inactive-title\">'+e(g.descripcion||'Bien')+'</div><div class=\"isub\">'+e([Number(g.cantidad||1)+' unidad'+(Number(g.cantidad||1)===1?'':'es'),g.codigo?('Código '+g.codigo):'',g.marca,g.modelo,g.numero_serie_patente?('Serie/Patente '+g.numero_serie_patente):''].filter(Boolean).join(' · '))+'</div></div><span class=\"pill\">Eliminado / baja</span></div><div class=\"isub\" style=\"margin-top:6px\">'+(g.fecha_baja?'Fecha de baja: '+e(new Date(g.fecha_baja+'T12:00:00').toLocaleDateString('es-AR')):'Baja registrada')+(g.estados?.nombre?' · Estado anterior: '+e(g.estados.nombre):'')+'</div><div class=\"actions\"><button class=\"btn green\" data-reactivate=\"'+g.id+'\">Reactivar bien</button></div></div>').join(''):'<div class=\"card muted\">No hay bienes eliminados en esta oficina.</div>';"""
if marker not in s: raise SystemExit('No se encontro primer listener')
s=s.replace(marker,inactive_render+marker,1)

# Listeners Editar / Eliminar / Reactivar
marker="document.querySelectorAll('[data-state]').forEach(b=>b.onclick=()=>changeStateForm(b.dataset.state));"
listeners="document.querySelectorAll('[data-edit]').forEach(b=>b.onclick=()=>editGoodForm(b.dataset.edit));document.querySelectorAll('[data-delete]').forEach(b=>b.onclick=()=>softDeleteGood(b.dataset.delete));document.querySelectorAll('[data-reactivate]').forEach(b=>b.onclick=()=>reactivateGood(b.dataset.reactivate));"
if marker not in s: raise SystemExit('No se encontro listener state')
s=s.replace(marker,listeners+marker,1)

# Formularios y acciones de edición/baja lógica
marker="function changeStateForm(id){"
funcs=r'''function editGoodForm(id){rememberRelView();const g=current.find(x=>x.id===id);if(!g)return;app.innerHTML='<div class="hero"><small>EDITAR BIEN</small><h2>'+e(g.descripcion||'Bien')+'</h2><small>'+e(office.nombre)+'</small></div><div class="card"><form id="editgoodform"><div class="field"><label>Descripción / nombre del bien</label><input id="egdesc" required value="'+e(g.descripcion||'')+'"></div><div class="field"><label>Cantidad de unidades</label><input id="egqty" type="number" min="1" max="100000" step="1" required value="'+Number(g.cantidad||1)+'"></div><div class="field"><label>Código</label><input id="egcode" value="'+e(g.codigo||'')+'"></div><div class="field"><label>Marca</label><input id="egbrand" value="'+e(g.marca||'')+'"></div><div class="field"><label>Modelo</label><input id="egmodel" value="'+e(g.modelo||'')+'"></div><div class="field"><label>Color</label><input id="egcolor" value="'+e(g.color||'')+'"></div><div class="field"><label>Número de serie / patente</label><input id="egserial" value="'+e(g.numero_serie_patente||'')+'"></div><div class="field"><label>Observaciones generales del bien</label><textarea id="egobs">'+e(g.observaciones||'')+'</textarea></div><div class="hint">Editar estos datos no cambia la oficina ni el área responsable. El cambio queda registrado en el historial.</div><div class="actions"><button class="btn green">Guardar cambios</button><button id="canceleditgood" type="button" class="btn ghost">Cancelar</button></div></form></div>';document.getElementById('canceleditgood').onclick=renderRel;document.getElementById('editgoodform').onsubmit=ev=>{ev.preventDefault();saveGoodEdit(id)}}
async function saveGoodEdit(id){const descripcion=document.getElementById('egdesc').value.trim(),cantidad=Number(document.getElementById('egqty').value);if(!descripcion)return alert('La descripción es obligatoria.');if(!Number.isInteger(cantidad)||cantidad<1)return alert('La cantidad debe ser mayor a 0.');busy('Guardando cambios...');try{const r=await db.rpc('editar_bien_control',{p_bien_id:id,p_descripcion:descripcion,p_codigo:document.getElementById('egcode').value.trim()||null,p_marca:document.getElementById('egbrand').value.trim()||null,p_modelo:document.getElementById('egmodel').value.trim()||null,p_color:document.getElementById('egcolor').value.trim()||null,p_numero_serie_patente:document.getElementById('egserial').value.trim()||null,p_cantidad:cantidad,p_observaciones:document.getElementById('egobs').value.trim()||null});if(r.error)throw r.error;await loadOffice();await loadItems();await loadLastResults();renderRel();alert('Bien actualizado. El cambio quedó registrado en el historial.')}catch(err){alert('No se pudo editar el bien: '+(err.message||err))}finally{unbusy()}}
async function softDeleteGood(id){rememberRelView();const g=current.find(x=>x.id===id);if(!g)return;if(!confirm('¿Eliminar / dar de baja “'+(g.descripcion||'Bien')+'”?\n\nNo se borrarán sus fotos, movimientos ni actas. Quedará visible abajo en “Bienes eliminados / dados de baja”.'))return;busy('Dando de baja el bien...');try{const r=await db.rpc('cambiar_activo_bien_control',{p_bien_id:id,p_activo:false});if(r.error)throw r.error;await loadOffice();await loadItems();await loadLastResults();renderRel();alert('Bien dado de baja. Sigue conservado en el historial y aparece al final del relevamiento.')}catch(err){alert('No se pudo dar de baja: '+(err.message||err))}finally{unbusy()}}
async function reactivateGood(id){const g=inactive.find(x=>x.id===id);if(!g)return;if(!confirm('¿Reactivar “'+(g.descripcion||'Bien')+'” y devolverlo a los bienes activos de esta oficina?'))return;busy('Reactivando bien...');try{const r=await db.rpc('cambiar_activo_bien_control',{p_bien_id:id,p_activo:true});if(r.error)throw r.error;await loadOffice();await loadItems();await loadLastResults();renderRel();alert('Bien reactivado correctamente.')}catch(err){alert('No se pudo reactivar: '+(err.message||err))}finally{unbusy()}}
'''
if marker not in s: raise SystemExit('No se encontro changeStateForm')
s=s.replace(marker,funcs+marker,1)

p.write_text(s,encoding='utf-8')
print('Parche de edición, baja lógica y orden aplicado')
