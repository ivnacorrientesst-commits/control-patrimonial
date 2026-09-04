from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="const BUCKET='patrimonio-fotos';"
new="const BUCKET='patrimonio-fotos';\nconst ACTA_BUCKET='patrimonio-actas';"
if old not in s:
    raise SystemExit('No se encontro constante BUCKET')
s=s.replace(old,new,1)

marker="function relSearchText(x){"
if marker not in s:
    raise SystemExit('No se encontro marcador relSearchText')
helpers=r'''function pickActa(source='file'){return new Promise(r=>{const i=document.createElement('input');i.type='file';if(source==='camera'){i.accept='image/*';i.setAttribute('capture','environment')}else{i.accept='image/*,application/pdf'}i.style.display='none';document.body.appendChild(i);i.onchange=()=>{const f=i.files?.[0]||null;i.remove();r(f)};i.click()})}
async function uploadActaFile(movimientoId,source='file'){const f=await pickActa(source);if(!f)return null;busy('Preparando y subiendo acta...');let path=null;try{let blob=f,mime=f.type||'',name=f.name||'acta';if(mime.startsWith('image/')){blob=await compressPhoto(f);mime=blob.type||'image/webp'}else if(mime==='application/pdf'||name.toLowerCase().endsWith('.pdf')){mime='application/pdf';if(f.size>10*1024*1024)throw Error('El PDF supera el limite de 10 MB')}else{throw Error('Formato no admitido. Usa una imagen o PDF.')}const ext=mime==='application/pdf'?'pdf':(mime==='image/webp'?'webp':(mime==='image/png'?'png':'jpg'));path='movimientos/'+movimientoId+'/'+Date.now()+'-'+Math.random().toString(36).slice(2,10)+'.'+ext;const up=await db.storage.from(ACTA_BUCKET).upload(path,blob,{contentType:mime,upsert:false});if(up.error)throw up.error;const ins=await db.from('movimiento_documentos').insert({movimiento_id:movimientoId,ruta_storage:path,nombre_archivo:name,mime_type:mime,tamano_bytes:blob.size,descripcion:'Acta / documento del movimiento',subida_por:session.user.id}).select('id,movimiento_id,ruta_storage,nombre_archivo,mime_type,tamano_bytes,descripcion,created_at').single();if(ins.error){await db.storage.from(ACTA_BUCKET).remove([path]);throw ins.error}return ins.data}catch(err){if(path){try{await db.storage.from(ACTA_BUCKET).remove([path])}catch{}}throw err}finally{unbusy()}}
async function signedActa(path){const r=await db.storage.from(ACTA_BUCKET).createSignedUrl(path,3600);if(r.error)throw r.error;return r.data?.signedUrl||''}
async function openActa(doc){const isImage=String(doc.mime_type||'').startsWith('image/');const tab=isImage?null:window.open('about:blank','_blank');busy('Abriendo acta...');try{const url=await signedActa(doc.ruta_storage);if(!url)throw Error('No se pudo generar el acceso al archivo');if(isImage){openLightbox(url,doc.nombre_archivo||'Acta firmada')}else if(tab){tab.location=url}else{location.href=url}}catch(err){if(tab)tab.close();alert('No se pudo abrir el acta: '+(err.message||err))}finally{unbusy()}}
async function addActa(movimientoId,source,goodId,highlightId,title){try{const d=await uploadActaFile(movimientoId,source);if(!d)return;alert('Acta guardada correctamente.');await showActas(goodId,highlightId||movimientoId,title)}catch(err){alert('No se pudo subir el acta: '+(err.message||err))}}
async function showActas(goodId,highlightId=null,titleOverride=''){rememberRelView();busy('Cargando movimientos y actas...');try{const rm=await db.from('movimientos').select('id,bien_id,oficina_origen_id,oficina_destino_id,motivo,fecha_movimiento').eq('bien_id',goodId).order('fecha_movimiento',{ascending:false});if(rm.error)throw rm.error;const moves=rm.data||[],ids=[...new Set(moves.flatMap(x=>[x.oficina_origen_id,x.oficina_destino_id]).filter(Boolean))];let officeMap={};if(ids.length){const ro=await db.from('oficinas').select('id,nombre').in('id',ids);if(!ro.error)(ro.data||[]).forEach(o=>officeMap[o.id]=o.nombre)}let docs=[];if(moves.length){const rd=await db.from('movimiento_documentos').select('id,movimiento_id,ruta_storage,nombre_archivo,mime_type,tamano_bytes,descripcion,created_at').in('movimiento_id',moves.map(x=>x.id)).order('created_at',{ascending:false});if(rd.error)throw rd.error;docs=rd.data||[]}const g=current.find(x=>x.id===goodId)||pending.find(x=>x.id===goodId),title=titleOverride||g?.descripcion||'Bien';app.innerHTML='<div class="hero"><small>ACTAS Y MOVIMIENTOS</small><h2>'+e(title)+'</h2><small>Documentación privada vinculada al historial del bien</small></div><div class="hint">Cada acta queda asociada al movimiento correspondiente. Podés sacar una foto del acta firmada o subir una imagen/PDF ya guardado.</div><div id="movdocs">'+(moves.length?moves.map(m=>{const md=docs.filter(d=>d.movimiento_id===m.id),origen=officeMap[m.oficina_origen_id]||'Sin oficina de origen',destino=officeMap[m.oficina_destino_id]||'Sin oficina de destino',fecha=m.fecha_movimiento?new Date(m.fecha_movimiento).toLocaleString('es-AR'):'';return '<div class="item" '+(highlightId===m.id?'style="border:2px solid #087f5b"':'')+'><div class="between"><div><div class="ititle">'+e(origen)+' → '+e(destino)+'</div><div class="isub">'+e(fecha)+(m.motivo?' · '+e(m.motivo):'')+'</div></div><span class="pill">'+md.length+' acta'+(md.length===1?'':'s')+'</span></div>'+(md.length?'<div class="actions">'+md.map(d=>'<button class="btn ghost" data-openacta="'+d.id+'">📄 '+e(d.nombre_archivo||'Ver acta')+'</button>').join('')+'</div>':'<div class="isub" style="margin-top:8px">Todavía no hay un acta adjunta a este movimiento.</div>')+(canEdit()?'<div class="actions"><button class="btn purple" data-actacamera="'+m.id+'">📷 Sacar foto del acta</button><button class="btn blue" data-actafile="'+m.id+'">📎 Subir imagen / PDF</button></div>':'')+'</div>'}).join(''):'<div class="card muted">Este bien todavía no tiene movimientos registrados.</div>')+'</div><button id="backactas" class="btn ghost" style="width:100%;margin-top:12px">Volver al relevamiento</button>';document.getElementById('backactas').onclick=renderRel;document.querySelectorAll('[data-openacta]').forEach(b=>{const d=docs.find(x=>x.id===b.dataset.openacta);if(d)b.onclick=()=>openActa(d)});document.querySelectorAll('[data-actacamera]').forEach(b=>b.onclick=()=>addActa(b.dataset.actacamera,'camera',goodId,highlightId,title));document.querySelectorAll('[data-actafile]').forEach(b=>b.onclick=()=>addActa(b.dataset.actafile,'file',goodId,highlightId,title))}catch(err){alert('No se pudieron cargar las actas: '+(err.message||err));renderRel()}finally{unbusy()}}
'''
s=s.replace(marker,helpers+marker,1)

old_btn="'<button class=\"btn ghost\" data-move=\"'+g.id+'\">Mover a otra oficina</button></div></div>'"
new_btn="'<button class=\"btn blue\" data-actas=\"'+g.id+'\">Actas / movimientos</button><button class=\"btn ghost\" data-move=\"'+g.id+'\">Mover a otra oficina</button></div></div>'"
if old_btn not in s:
    raise SystemExit('No se encontro boton mover')
s=s.replace(old_btn,new_btn,1)

old_listener="document.querySelectorAll('[data-move]').forEach(b=>b.onclick=()=>moveGood(b.dataset.move));"
new_listener="document.querySelectorAll('[data-actas]').forEach(b=>b.onclick=()=>showActas(b.dataset.actas));"+old_listener
if old_listener not in s:
    raise SystemExit('No se encontro listener mover')
s=s.replace(old_listener,new_listener,1)

old_success="await loadOffice();await loadItems();renderRel();alert('Bien trasladado a '+dest.nombre+'. El movimiento quedó guardado en el historial.')}}"
new_success="const movimientoId=m.data?.movimiento_id||null;await loadOffice();await loadItems();alert('Bien trasladado a '+dest.nombre+'. El movimiento quedó guardado en el historial. Ahora podés adjuntar el acta firmada.');if(movimientoId){await showActas(id,movimientoId,good.descripcion||'Bien')}else{renderRel()}}}"
if old_success not in s:
    raise SystemExit('No se encontro cierre de moveGood')
s=s.replace(old_success,new_success,1)

p.write_text(s,encoding='utf-8')
print('Parche de actas aplicado')
