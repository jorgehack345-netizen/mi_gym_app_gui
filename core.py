import os
import json
import csv
from datetime import datetime, date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_FILE = os.path.join(DATA_DIR, 'clientes.json')
DATE_FMT_SHOW = '%d/%m/%Y'
DATE_FMT_STORE = '%Y-%m-%d'

DEFAULT_CONFIG = {
    'precio_semanal': 120.0,
    'precio_mensual': 450.0,
    'dias_proximos': 7,
}

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)

def hoy() -> date:
    return date.today()

def fmt_show(d: date) -> str:
    return d.strftime(DATE_FMT_SHOW)

def parse_date_input(s: str) -> date:
    s = s.strip()
    for fmt in (DATE_FMT_SHOW, DATE_FMT_STORE):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError('Formato de fecha inválido. Usa dd/mm/aaaa o yyyy-mm-dd.')

def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = (date(y, m, 1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    day = min(d.day, last_day.day)
    return date(y, m, day)

def next_due(d0: date, plan: str) -> date:
    if plan == 'semanal':
        return d0 + timedelta(weeks=1)
    elif plan == 'mensual':
        return add_months(d0, 1)
    else:
        raise ValueError('Plan desconocido')

def avanzar_hasta_ponerse_al_corriente(due: date, plan: str, ref: date):
    periodos = 0
    current = due
    while current <= ref:
        periodos += 1
        current = next_due(current, plan)
    return current, periodos

def load_db():
    ensure_dirs()
    if not os.path.exists(DB_FILE):
        data = {'configs': DEFAULT_CONFIG.copy(), 'clientes': []}
        save_db(data)
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def next_id(clientes):
    return max([c['id'] for c in clientes], default=0) + 1

def registrar_cliente(data, nombre: str, plan: str, precio: float, fecha_inicio: date):
    if plan not in ('semanal','mensual'):
        raise ValueError('Plan debe ser semanal o mensual')
    cliente = {
        'id': next_id(data['clientes']),
        'nombre': nombre.strip(),
        'plan': plan,
        'precio': float(precio),
        'fecha_alta': fecha_inicio.strftime(DATE_FMT_STORE),
        'proximo_pago': next_due(fecha_inicio, plan).strftime(DATE_FMT_STORE),
        'activo': True,
        'ultima_renovacion': None,
    }
    data['clientes'].append(cliente)
    save_db(data)
    return cliente

def listar_clientes(data):
    return list(data['clientes'])

def get_pendientes(data):
    cfg = data['configs']
    dias = int(cfg.get('dias_proximos', 7))
    d_hoy = hoy()
    limite = d_hoy + timedelta(days=dias)
    atrasados, hoy_l, proximos = [], [], []
    for c in data['clientes']:
        if not c.get('activo', True):
            continue
        due = datetime.strptime(c['proximo_pago'], DATE_FMT_STORE).date()
        if due < d_hoy:
            atrasados.append(c)
        elif due == d_hoy:
            hoy_l.append(c)
        elif d_hoy < due <= limite:
            proximos.append(c)
    return atrasados, hoy_l, proximos

def calcular_cobro(cliente, refdate=None):
    if refdate is None:
        refdate = hoy()
    if not cliente.get('activo', True):
        return {'error': 'Cliente inactivo'}
    plan = cliente['plan']
    precio = float(cliente['precio'])
    due = datetime.strptime(cliente['proximo_pago'], DATE_FMT_STORE).date()

    if due > refdate:
        periodos = 1
        nuevo_due = next_due(due, plan)
        mensaje = 'Renovación por el siguiente periodo (no atrasado).'
    else:
        nuevo_due, adeudo = avanzar_hasta_ponerse_al_corriente(due, plan, refdate)
        periodos = adeudo
        mensaje = f'Adeuda {adeudo} periodo(s).'
    monto = precio * periodos
    return {'periodos': periodos, 'monto': monto, 'nuevo_due': nuevo_due, 'mensaje': mensaje}

def aplicar_cobro(data, cliente_id, nuevo_due: date):
    d = None
    for c in data['clientes']:
        if c['id'] == cliente_id:
            d = c
            break
    if d is None:
        raise ValueError('Cliente no encontrado')
    d['proximo_pago'] = nuevo_due.strftime(DATE_FMT_STORE)
    d['ultima_renovacion'] = hoy().strftime(DATE_FMT_STORE)
    save_db(data)
    return d

def toggle_activo(data, cliente_id, activo: bool):
    for c in data['clientes']:
        if c['id'] == cliente_id:
            c['activo'] = bool(activo)
            save_db(data)
            return c
    raise ValueError('Cliente no encontrado')

def buscar(data, texto: str):
    q = texto.strip().lower()
    return [c for c in data['clientes'] if q in c['nombre'].lower()]

def actualizar_config(data, precio_semanal=None, precio_mensual=None, dias_proximos=None):
    cfg = data['configs']
    if precio_semanal is not None:
        cfg['precio_semanal'] = float(precio_semanal)
    if precio_mensual is not None:
        cfg['precio_mensual'] = float(precio_mensual)
    if dias_proximos is not None:
        cfg['dias_proximos'] = int(dias_proximos)
    save_db(data)
    return cfg

def exportar_csv(data):
    out = os.path.join(DATA_DIR, 'reporte_clientes.csv')
    campos = ['id','nombre','plan','precio','fecha_alta','proximo_pago','activo','ultima_renovacion']
    with open(out, 'w', encoding='utf-8', newline='') as f:
        import csv
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for c in data['clientes']:
            w.writerow(c)
    return out
