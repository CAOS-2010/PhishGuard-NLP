"""
Tercera ronda - ejemplos muy especificos para los 2 patrones que fallan.
Foco en: pago previo para recibir algo / datos bancarios en proceso externo.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

# ---------------------------------------------------------------------------
# ESTAFA FINANCIERA v3 - foco en pedir clave/cuenta bancaria para transferir
# ---------------------------------------------------------------------------
ESTAFA_V3 = [
    "estimado beneficiario usted ha sido seleccionado para recibir fondos de herencia internacional necesitamos sus datos bancarios numero de cuenta y clave de acceso para procesar la transferencia responda urgentemente el plazo vence manana",
    "ganador sorteo internacional debe pagar impuesto de liberacion de fondos para recibir su premio de dolares realice pago de 500 dolares a cuenta adjunta y recibira su dinero en 48 horas",
    "herencia millonaria a su nombre para reclamarla necesita enviar copia de cedula cuenta bancaria y clave bancaria su heredero fallecido le dejo 4 millones dolares actue antes que venzan los plazos legales",
    "su correo gano loteria internacional de 350000 euros para procesar el desembolso pague impuesto ganancial de 800 euros a la cuenta adjunta y en 72 horas recibira sus fondos en colombia",
    "fondos retenidos a su nombre en banco central necesita verificar identidad con clave bancaria y numero de cuenta para desbloquear 6 millones pesos responda urgentemente antes del vencimiento del plazo",
    "transferencia internacional pendiente a su favor por herencia difunto familiar radicado en espana para recibir fondos proporcione numero cuenta bancaria clave de acceso y copia cedula a la brevedad",
    "notificacion urgente tiene beneficio economico de compensacion del gobierno por 2 millones pesos para activar desembolso ingrese clave bancaria y cuenta corriente activa en el portal de compensaciones adjunto",
    "premio nacional de emprendimiento a su nombre reciba 8 millones pesos solo pague seguro de transferencia de 300000 pesos y en 24 horas recibira todo su premio en cuenta bancaria que nos indique",
    "fondo de compensacion internacional tiene dinero para usted de acuerdo firmado en ginebra reciba 15000 dolares al confirmar sus datos bancarios completos incluyendo clave pin y numero de cuenta activa",
    "acuerdo judicial a su favor tiene retenidos 3 millones pesos para recibirlos deposite 200000 pesos de honorarios notariales y proporcione su cuenta bancaria con clave de acceso para la transferencia",
    "usted resulto beneficiario de programa social del gobierno que entrega dinero a familias vulnerables para el desembolso de 1 millon pesos confirme cedula clave bancaria y numero de cuenta de ahorros",
    "corporacion financiera internacional le informa que tiene saldo disponible de 12 millones pesos abra cuenta especial depositando 500000 pesos de capital inicial y recibira fondos duplicados en 30 dias",
    "sorteo especial claro 25 aniversario su telefono gano 10 millones pesos en efectivo para reclamar transfiera impuesto del 2 por ciento equivalente a 200000 pesos y proporcione cuenta bancaria activa",
    "compensacion historica a su favor como victima de practicas bancarias irregulares tiene derecho a 4 millones pesos para recibirlos confirme sus datos bancarios nombre cuenta y clave de acceso al banco",
    "oferta de inversion garantizada deposite 1 millon pesos en nuestra plataforma y reciba 3 millones en 15 dias rendimiento garantizado por contrato legal regrese al 200 por ciento su capital en semanas",
    "abogado de herencia internacional le informa que usted fue identificado como beneficiario de testamento de ciudadano fallecido por valor de 2 millones euros envie cuenta bancaria con clave para deposito",
    "banco central le notifica fondos congelados a nombre suyo por 9 millones pesos para desbloquear verifique identidad con cedula clave bancaria y autorize transferencia en el portal adjunto urgente",
    "programa de subsidio habitacional aprobado su solicitud tiene bono de 5 millones pesos para reclamarlo ingrese clave bancaria numero de cuenta y copia de cedula en el formulario de la entidad adjunto",
    "ganador concurso internacional de innovacion 50000 dolares premio debe pagar tramites de legalizacion de 1500 dolares a cuenta adjunta y en 5 dias habiles recibira su premio en colombia",
    "reembolso especial de impuestos a su favor por 3 millones pesos segun revision de sus declaraciones para recibirlo ingrese al portal tributario con su clave de acceso y proporcione numero de cuenta bancaria",
]

# ---------------------------------------------------------------------------
# INGENIERIA SOCIAL v3 - foco en pedir datos bancarios en proceso de empleo
# ---------------------------------------------------------------------------
TRABAJO_V3 = [
    "vacante disponible analista de datos salario 8 millones pesos para continuar proceso de seleccion complete formulario con sus datos bancarios numero de cuenta y copia de cedula de ciudadania urgente",
    "convocatoria laboral empresa multinacional para aplicar a cargo gerencial con salario de 12 millones pague examen psicotecnico de 150000 pesos y envie cedula y cuenta bancaria para continuar proceso",
    "trabajo desde casa sin experiencia gane 100000 pesos diarios para empezar descargue nuestra aplicacion ingrese numero cedula y datos bancarios activamos su cuenta de trabajador hoy mismo",
    "empresa reconocida busca representantes comerciales salario de 5 millones para iniciar deposite garantia de productos de 400000 pesos proporcione cuenta bancaria y en lunes inicia trabajo remunerado",
    "oferta laboral urgente se requiere personal administrativo salario 3 millones para el proceso de contratacion pague estudio de seguridad de 200000 pesos a cuenta adjunta y envie cedula con datos bancarios",
    "reclutadora linkedin encontro su perfil para cargo de director con salario de 15 millones para verificacion previa al contrato necesitamos cedula datos bancarios completos y password del correo corporativo",
    "freelance internacional paga 30 dolares hora para digitadores de datos en colombia para activar cuenta de trabajador registrese con cedula y datos bancarios primer deposito llega en 24 horas",
    "empresa de seguridad electronica contrata guardas salario 2 millones para ingresar pague kit de dotacion de 350000 pesos a cuenta davivienda adjunta y presentese el lunes con recibo cedula y cuenta bancaria",
    "amazon mecanical turk busca calificadores de contenido en colombia gane 200000 pesos diarios para comenzar pague afiliacion de 100000 pesos y proporcione cuenta bancaria activa para recibir pagos diarios",
    "convocatoria ecopetrol 2024 operadores de campo salario 6 millones registrese pagando derechos de inscripcion de 300000 pesos en pse adjunto y envie datos bancarios para proceso de contratacion",
    "trabajo remoto empresa usa asistente virtual 1200 dolares mensuales para contrato necesita enviar cedula escaneada cuenta bancaria activa y contrasena del correo electronico para integracion con sistemas",
    "hotel de lujo cartagena contrata personal salario 2 millones para aplicar pague examen medico y uniformes por 450000 pesos consigne a cuenta bancolombia adjunta y presentese el martes con cedula y comprobante",
    "trabajo en casa calificando videos de youtube sin experiencia gana 150000 pesos diarios para iniciar ingresa cedula y datos bancarios en nuestra plataforma tu primer pago llega en 24 horas actua ya",
    "multinacional alemana planta bogota requiere tecnicos salario 5 millones para aplicar registrese en plataforma de empleo ingresando cedula datos bancarios y clave de acceso a su correo corporativo actual",
    "empresa de cosmeticos busca distribuidores independientes gane 6 millones mensuales para iniciar haga pedido inicial de productos por 500000 pesos proporcione cuenta bancaria y en 30 dias recupera inversion",
    "convocatoria laboral avianca busca tripulacion de cabina salario 4 millones para proceso de seleccion pague kit de evaluacion psicofisica de 250000 pesos a cuenta adjunta y envie cedula con datos bancarios",
    "empresa de marketing digital busca community managers trabajo remoto salario 3 millones para empezar pague suscripcion a plataforma de 120000 pesos y envie cedula y cuenta bancaria para activar perfil",
    "convocatoria ejercito de colombia personal civil administrativo salario 2 millones para inscribirse descargue formulario ingrese datos personales bancarios y deposite 180000 pesos de derechos de participacion",
    "empresa de delivery busca repartidores gane 200000 pesos diarios para registrarse como repartidor pague kit de herramientas de seguridad de 280000 pesos y envie cedula con cuenta bancaria activa hoy",
    "oferta de trabajo cuba pague tiquete aereo de 1500 dolares anticipado y al llegar empresa devuelve el dinero mas salario de 2000 dolares mensuales sin papeles de trabajo envie datos bancarios para coordinar",
]

# ---------------------------------------------------------------------------
# Build and append
# ---------------------------------------------------------------------------

def main() -> None:
    import subprocess

    data_path = ROOT / "data" / "raw" / "dataset.csv"
    df_existing = pd.read_csv(data_path)
    print(f"Dataset actual: {len(df_existing):,} registros")

    new_rows: list[dict] = []
    for text in ESTAFA_V3:
        new_rows.append({"text": text.strip(), "label": 1})
    for text in TRABAJO_V3:
        new_rows.append({"text": text.strip(), "label": 1})

    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset="text", inplace=True)
    df_combined.to_csv(data_path, index=False)

    added = len(df_combined) - len(df_existing)
    print(f"Agregados: {added} ejemplos de phishing especificos")
    print(f"Dataset nuevo: {len(df_combined):,} registros")

    print("\nReentrenando modelo...")
    result = subprocess.run(
        ["python", str(ROOT / "scripts" / "train_model.py")],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])


if __name__ == "__main__":
    main()
