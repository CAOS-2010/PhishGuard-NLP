"""
Genera un dataset sintético de phishing bancario en español colombiano.
Produce data/raw/dataset_spanish.csv con 400 registros balanceados.

Uso:
    python scripts/generate_spanish_dataset.py
"""
from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATA_RAW_DIR

random.seed(42)

# ─── Plantillas PHISHING (label=1) ────────────────────────────────────────────

PHISHING_TEMPLATES = [
    "Estimado cliente de {banco}, su cuenta ha sido BLOQUEADA por actividad sospechosa. "
    "Para evitar la suspensión definitiva debe verificar su información AHORA mismo en el "
    "siguiente enlace: {url_falsa}. Tiene {horas} horas para completar el proceso.",

    "ALERTA DE SEGURIDAD {banco}: Detectamos un acceso no autorizado desde {ciudad}. "
    "Su cuenta quedará suspendida en {horas} horas si no confirma su identidad. "
    "Haga clic aquí para validar: {url_falsa}",

    "Notificación urgente de {banco}: Su tarjeta {tarjeta} ha sido utilizada para una "
    "compra de ${monto} en {ciudad_ext}. Si no reconoce esta transacción confirme su "
    "identidad inmediatamente en {url_falsa} o llame al {telefono_falso}.",

    "Estimado usuario, el sistema de seguridad de {banco} ha detectado que su contraseña "
    "está en riesgo de ser comprometida. Actualice su clave de acceso URGENTE ingresando "
    "a {url_falsa} con su número de cédula y PIN actual.",

    "Su cuenta {banco} presenta un saldo negativo de ${monto}. Para evitar cargos "
    "adicionales y el reporte a centrales de riesgo, regularice su situación ahora: "
    "{url_falsa}. Este proceso es obligatorio según la normativa Asobancaria.",

    "Verificación obligatoria {banco}: Como parte de nuestra política de prevención de "
    "fraude, todos los clientes deben actualizar sus datos antes del {fecha_limite}. "
    "Ingrese su información en {url_falsa}. El incumplimiento generará el bloqueo inmediato "
    "de su cuenta.",

    "GANADOR! Su cuenta {banco} fue seleccionada para recibir un BONO de ${monto} pesos. "
    "Para reclamar su premio en las próximas {horas} horas confirme sus datos bancarios "
    "en {url_falsa}. No pierda esta oportunidad única.",

    "Aviso de cobro jurídico {banco}: Su obligación crediticia se encuentra en mora. "
    "Para evitar proceso legal y embargo de bienes acceda a {url_falsa} y regularice "
    "su situación. Tiene {horas} horas.",

    "Actualización obligatoria de seguridad {banco}: Su token digital ha expirado. "
    "Renueve su dispositivo de seguridad ahora en {url_falsa} usando su número de cuenta "
    "y contraseña actual para evitar la inhabilitación de sus transacciones.",

    "Importante: Detectamos múltiples intentos fallidos en su cuenta {banco}. "
    "Por su seguridad la hemos bloqueado temporalmente. Para reactivarla ingrese a "
    "{url_falsa} y siga las instrucciones. Responda este correo con su PIN de confirmación.",

    "Servicio al cliente {banco}: Tenemos una oferta exclusiva de crédito preaprobado "
    "por ${monto} a su nombre. Para activarlo en las próximas {horas} horas visite "
    "{url_falsa} y confirme su número de cédula, cuenta y fecha de nacimiento.",

    "ATENCIÓN cliente {banco}: Su cuenta será CERRADA definitivamente por inactividad. "
    "Para conservarla debe ingresar sus credenciales en {url_falsa} antes del {fecha_limite}. "
    "Este proceso es gratuito y toma menos de 2 minutos.",

    "Notificación de transferencia {banco}: Se realizó un débito de ${monto} desde su "
    "cuenta hacia una cuenta desconocida. Si no autorizó esta operación REVIERTA ahora: "
    "{url_falsa}. La reversión solo es posible en las próximas {horas} horas.",

    "Estimado cliente, el área de seguridad informática de {banco} requiere que valide "
    "su identidad para continuar usando la app. Ingrese a {url_falsa} con su usuario y "
    "contraseña. NO comparta este correo con nadie.",

    "Actualización de datos {banco}: La Superintendencia Financiera exige actualizar "
    "la información de todos los usuarios antes de {fecha_limite}. Evite el bloqueo de "
    "su cuenta ingresando a {url_falsa} con su número de cédula.",
]

PHISHING_SUBJECTS = [
    "URGENTE: Su cuenta ha sido bloqueada",
    "Alerta de seguridad - Acción requerida",
    "Verificación obligatoria de su cuenta",
    "Actividad sospechosa detectada",
    "Su tarjeta será cancelada",
    "Último aviso - Actualice sus datos",
    "Transferencia no autorizada detectada",
    "Premio especial para usted",
    "Proceso jurídico iniciado",
    "Token vencido - Renueve ahora",
]

# ─── Plantillas SEGUROS / LEGÍTIMOS (label=0) ─────────────────────────────────

SAFE_TEMPLATES = [
    "Estimado cliente, le informamos que su extracto del mes de {mes} ya está disponible "
    "en nuestra plataforma digital {banco}. Puede consultarlo ingresando con su usuario "
    "habitual. Gracias por preferirnos.",

    "Le comunicamos que a partir del {fecha} los horarios de atención en la sucursal "
    "{sucursal} serán de lunes a viernes de 8:00 am a 4:00 pm. Para más información "
    "comuníquese al {telefono_oficial}.",

    "Su pago de tarjeta de crédito {banco} por ${monto} fue procesado exitosamente el "
    "{fecha}. Su saldo disponible actual es ${monto2}. Para más detalles ingrese a nuestra "
    "app móvil con su usuario y contraseña.",

    "Estimado cliente, como parte de nuestro compromiso con la seguridad le recordamos "
    "que {banco} NUNCA le solicitará su contraseña, PIN ni datos sensibles por correo "
    "electrónico. Si recibe mensajes solicitando esta información repórtelos.",

    "Le informamos que su solicitud de certificado bancario fue procesada. Puede "
    "descargarlo directamente desde la sección de documentos en nuestra plataforma web "
    "o app móvil {banco} a partir de mañana.",

    "Querido cliente {banco}, nos complace informarle que su solicitud de crédito de "
    "libre inversión fue aprobada. Nuestro asesor se comunicará con usted en los próximos "
    "{horas} días hábiles para coordinar la firma del pagaré.",

    "Le recordamos que el próximo {fecha} vence el pago de su cuota de crédito por "
    "${monto}. Puede realizar el pago desde nuestra app, en cualquier sucursal o a través "
    "de PSE sin costo adicional.",

    "Su inscripción al programa de puntos y beneficios {banco} fue exitosa. Empiece a "
    "acumular puntos con cada compra y canjéelos por descuentos en comercios aliados. "
    "Consulte los beneficios en nuestra página oficial.",

    "Le informamos que por mantenimiento programado nuestros servicios digitales estarán "
    "temporalmente fuera de servicio el {fecha} de {hora1} a {hora2}. Disculpe los "
    "inconvenientes. Sus saldos y movimientos están seguros.",

    "Resumen mensual {banco}: Durante {mes} realizó {num} transacciones por un total de "
    "${monto}. Sus ahorros generaron ${monto2} en rendimientos. Consulte el detalle "
    "completo en la app móvil o la plataforma web.",

    "Estimado cliente, su solicitud de cambio de dirección de correspondencia fue "
    "actualizada correctamente en nuestros sistemas. Si no realizó esta solicitud "
    "comuníquese de inmediato al {telefono_oficial}.",

    "Gracias por comunicarse con {banco}. Su número de radicado es {radicado}. "
    "Daremos respuesta a su solicitud dentro de los {horas} días hábiles establecidos "
    "por la normativa vigente.",

    "Le informamos que los intereses de su CDT por ${monto} fueron abonados el {fecha} "
    "directamente a su cuenta de ahorros. Su CDT se renovará automáticamente el próximo "
    "{fecha2} a la misma tasa pactada.",

    "Queremos recordarle que puede desactivar el uso internacional de su tarjeta {banco} "
    "directamente desde la app en la sección Seguridad. Esta función le permite proteger "
    "su tarjeta cuando no esté viajando.",

    "Su código de seguridad de un solo uso (OTP) para confirmar la transferencia es: "
    "{codigo}. Este código expira en 5 minutos. Si no realizó esta operación comuníquese "
    "de inmediato al {telefono_oficial}. Nunca comparta este código.",
]

SAFE_SUBJECTS = [
    "Su extracto del mes ya está disponible",
    "Confirmación de pago recibido",
    "Actualización de horarios de atención",
    "Recordatorio de pago próximo",
    "Solicitud aprobada",
    "Resumen mensual de cuenta",
    "Mantenimiento programado",
    "Bienvenido al programa de beneficios",
    "Cambio de datos actualizado",
    "Su CDT fue renovado",
]

# ─── Datos para relleno ───────────────────────────────────────────────────────

BANCOS = ["Bancolombia", "Davivienda", "BBVA Colombia", "Banco de Bogotá",
          "Banco Popular", "Colpatria", "Banco Falabella", "Nequi", "Daviplata"]

URLS_FALSAS = [
    "http://bancolombia-seguridad.net/verificar",
    "http://davivienda-alerta.co/login",
    "http://bbva-colombia-update.com/cuenta",
    "http://banco-bogota.verificacion.net",
    "http://secure-bancolombia.xyz/acceso",
    "http://actualizar-cuenta.bancol.net",
    "http://nequi-seguridad.info/validar",
]

TELEFONOS_FALSOS = ["018000-XXXX", "601-XXX-XXXX", "320-XXX-XXXX"]
TELEFONOS_OFICIALES = ["01 8000 912 345", "601 742 1111", "018000 93 9000"]
CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]
CIUDADES_EXT = ["Miami, USA", "Madrid, España", "Ciudad de México", "Lima, Perú"]
TARJETAS = ["Visa", "Mastercard", "Amex"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
SUCURSALES = ["El Centro", "El Poblado", "Chapinero", "Unicentro", "Bello"]


def _rand_monto() -> str:
    return f"{random.randint(50, 5000) * 1000:,}".replace(",", ".")


def _rand_fecha() -> str:
    return f"{random.randint(1, 28)}/{random.randint(1, 12)}/2026"


def _rand_fecha_limite() -> str:
    return f"{random.randint(1, 28)} de {random.choice(MESES)} de 2026"


def _rand_horas() -> str:
    return str(random.choice([2, 4, 6, 12, 24, 48]))


def _fill(template: str, label: int) -> str:
    banco = random.choice(BANCOS)
    subs = {
        "{banco}": banco,
        "{url_falsa}": random.choice(URLS_FALSAS),
        "{horas}": _rand_horas(),
        "{monto}": _rand_monto(),
        "{monto2}": _rand_monto(),
        "{ciudad}": random.choice(CIUDADES),
        "{ciudad_ext}": random.choice(CIUDADES_EXT),
        "{tarjeta}": random.choice(TARJETAS),
        "{telefono_falso}": random.choice(TELEFONOS_FALSOS),
        "{telefono_oficial}": random.choice(TELEFONOS_OFICIALES),
        "{fecha}": _rand_fecha(),
        "{fecha2}": _rand_fecha(),
        "{fecha_limite}": _rand_fecha_limite(),
        "{mes}": random.choice(MESES),
        "{num}": str(random.randint(5, 80)),
        "{sucursal}": random.choice(SUCURSALES),
        "{hora1}": "01:00 am",
        "{hora2}": "05:00 am",
        "{radicado}": f"RAD-{random.randint(100000, 999999)}",
        "{codigo}": str(random.randint(100000, 999999)),
    }
    for k, v in subs.items():
        template = template.replace(k, v)
    return template


def generate(n_per_class: int = 200) -> list[dict]:
    rows: list[dict] = []

    for _ in range(n_per_class):
        tmpl = random.choice(PHISHING_TEMPLATES)
        subject = random.choice(PHISHING_SUBJECTS)
        body = _fill(tmpl, label=1)
        rows.append({
            "text": f"{subject}. {body}",
            "label": 1,
            "language": "es",
            "source": "synthetic_banking_co",
        })

    for _ in range(n_per_class):
        tmpl = random.choice(SAFE_TEMPLATES)
        subject = random.choice(SAFE_SUBJECTS)
        body = _fill(tmpl, label=0)
        rows.append({
            "text": f"{subject}. {body}",
            "label": 0,
            "language": "es",
            "source": "synthetic_banking_co",
        })

    random.shuffle(rows)
    return rows


def save(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "language", "source"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    output = DATA_RAW_DIR / "dataset_spanish.csv"
    print("Generando dataset sintético en español...")
    rows = generate(n_per_class=200)
    save(rows, output)
    phishing = sum(1 for r in rows if r["label"] == 1)
    safe = len(rows) - phishing
    print(f"Total registros: {len(rows)}")
    print(f"  Phishing: {phishing}")
    print(f"  Seguros:  {safe}")
    print(f"Guardado en: {output}")
    print("\nPara usar este dataset como principal:")
    print("  cp data/raw/dataset_spanish.csv data/raw/dataset.csv")
