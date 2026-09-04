from pathlib import Path

p = Path('administracion.html')
a = p.read_text(encoding='utf-8')

replacements = [
    ("let msg='¿De qué área depende esta oficina?\n';", "let msg='¿De qué área depende esta oficina?\\n';"),
    ("msg+=(i+1)+' - '+x.nombre+'\n');", "msg+=(i+1)+' - '+x.nombre+'\\n');"),
    ("let msg='Elegí responsable / encargado:\n';", "let msg='Elegí responsable / encargado:\\n';"),
    ("+(x.cargo?' ('+x.cargo+')':'')+'\n');", "+(x.cargo?' ('+x.cargo+')':'')+'\\n');"),
]

changed = 0
for old, new in replacements:
    if old in a:
        a = a.replace(old, new, 1)
        changed += 1

if changed != 4:
    raise SystemExit(f'Se esperaban 4 correcciones y se aplicaron {changed}')

for bad in [
    "let msg='¿De qué área depende esta oficina?\n';",
    "let msg='Elegí responsable / encargado:\n';",
]:
    if bad in a:
        raise SystemExit('Quedó un salto de línea inválido dentro de JavaScript')

for marker in [
    'Organigrama municipal',
    'async function editOfficeFromOrg(id)',
    'async function assignFromOrg(type,id)',
    'Encargado:',
    'depende de',
]:
    if marker not in a:
        raise SystemExit(f'Falta marcador esperado: {marker}')

p.write_text(a, encoding='utf-8')
print('Saltos de línea de JavaScript corregidos')
