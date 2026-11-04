"""Test categorias via API (con scoring hibrido)."""
import sys
import json
import urllib.request
import urllib.error

API = "http://127.0.0.1:8036"

tests = [
    ("ESTAFA FINANCIERA", {
        "sender": "herencias@banco-internacional.net",
        "subject": "Transferencia de herencia pendiente a su favor",
        "text": "Estimado beneficiario, le informamos que ha sido seleccionado para recibir CINCO MILLONES DE DOLARES como parte de la herencia del difunto empresario fallecido. Para procesar la transferencia necesitamos sus datos bancarios completos incluyendo numero de cuenta y clave de acceso. Responda urgentemente antes de que el plazo venza manana.",
    }, "phishing"),
    ("SUPLANTACION DIAN", {
        "sender": "notificaciones@dian.gov.co.fiscalizacion.net",
        "subject": "URGENTE: Inconsistencias en declaracion de renta - Proceso de fiscalizacion",
        "text": "DIRECCION DE IMPUESTOS Y ADUANAS NACIONALES DIAN. Su empresa figura con inconsistencias en la declaracion de renta del ano gravable 2023. Se ha iniciado proceso de fiscalizacion que puede resultar en sancion de 12500000 pesos. Para evitar sanciones debe actualizar su RUT e ingresar clave tributaria en dian.gov.co.verificacion-urgente.net urgentemente.",
    }, "phishing"),
    ("INGENIERIA SOCIAL TRABAJO", {
        "sender": "reclutamiento@empresa-internacional.careers",
        "subject": "Oferta laboral - Analista de Datos - Salario 8.5M",
        "text": "Estimado candidato, tras revisar su perfil en LinkedIn hemos decidido contactarle para ofrecerle vacante como Analista de Datos con salario de 8500000 pesos mensuales mas beneficios. Para continuar el proceso de seleccion necesitamos que complete el formulario adjunto con sus datos bancarios y suba copia de su cedula de ciudadania.",
    }, "phishing"),
    ("BANCARIO CLASICO", {
        "sender": "seguridad@bancolombia-alerta.co",
        "subject": "URGENTE: Cuenta bloqueada - Verificacion requerida",
        "text": "Estimado cliente Bancolombia, su cuenta ha sido temporalmente bloqueada por seguridad. Para restablecer el acceso ingrese AHORA a bancolombia-seguro.co y confirme su clave de acceso. Si no verifica en 24 horas perdera acceso permanentemente a su cuenta.",
    }, "phishing"),
    ("CORREO SEGURO BANCO", {
        "sender": "notificaciones@bancolombia.com",
        "subject": "Su extracto bancario esta disponible",
        "text": "Estimado cliente, le informamos que su extracto bancario del mes de octubre esta disponible en la sucursal virtual. Para consultarlo acceda a nuestra pagina oficial con sus credenciales habituales. Comuniquese al 018000912345 si tiene dudas.",
    }, "seguro"),
    ("CORREO SEGURO INST", {
        "sender": "academica@tdea.edu.co",
        "subject": "Inicio periodo de matriculas 2025-1",
        "text": "Estimado estudiante, le recordamos que el periodo de matriculas para el semestre 2025-1 inicia el 15 de enero. Consulte el calendario academico en el portal estudiantil con su usuario y contrasena institucional. Comuniquese con la oficina de registro si tiene inquietudes.",
    }, "seguro"),
]

def analyze(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/analyze/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

print("Resultados via API (scoring hibrido):")
print("-" * 90)
ok_count = 0
for name, payload, expected in tests:
    try:
        result = analyze(payload)
        label = result["label"]
        conf = result["confidence"]
        risk = result.get("risk_level", "?")
        xai = result.get("explainability", {})
        social = xai.get("social_engineering_score", 0)
        urgency = xai.get("urgency_keywords_found", [])
        urls_total = result.get("url_analysis", {}).get("total_urls", 0)
        is_ok = (label == expected)
        ok_count += is_ok
        status = "OK  " if is_ok else "FALLO"
        print(f"{status}  {name:<30} {label:<10} {conf:.1%}  social:{social:.2f} urgencia:{len(urgency)} urls:{urls_total}")
        if not is_ok:
            print(f"       urgency_words: {urgency}")
            print(f"       top_phishing: {[(f['word'],round(f['weight'],3)) for f in xai.get('top_phishing_features',[])[:5]]}")
    except Exception as e:
        print(f"ERROR {name}: {e}")

print(f"\nTotal: {ok_count}/{len(tests)} correctos ({ok_count/len(tests):.0%})")
