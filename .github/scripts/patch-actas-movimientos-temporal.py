from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="async function showActas(goodId,highlightId=null,titleOverride=''){rememberRelView();busy('Cargando movimientos y actas...');"
new="async function showActas(goodId,highlightId=null,titleOverride=''){if(document.getElementById('relsearch'))rememberRelView();busy('Cargando movimientos y actas...');"
if old not in s:
    raise SystemExit('No se encontro showActas para ajustar')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Ajuste de posicion aplicado')
