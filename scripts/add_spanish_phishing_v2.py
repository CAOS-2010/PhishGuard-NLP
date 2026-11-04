"""
Segunda ronda de ejemplos en español:
- Más ejemplos de estafa financiera y oferta de trabajo falsa
- Correos legítimos en español para reducir falsos positivos
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

# ---------------------------------------------------------------------------
# Más ejemplos PHISHING - Estafa financiera (variados)
# ---------------------------------------------------------------------------
ESTAFA_V2 = [
    "Su numero de telefono resulto ganador del tercer sorteo de CLARO COLOMBIA. Premio: 15000000 pesos colombianos. Para reclamar llame al 01-800 o transfiera 50000 pesos de seguro al numero de cuenta Nequi 3001234567. El premio vence esta noche a las 12.",
    "Le escribo en nombre del Dr. Michael Williams, director del Fondo de Compensacion Internacional. Su nombre fue encontrado en la lista de beneficiarios de un acuerdo que incluye 2400000 dolares a su favor. Solo necesito su cuenta bancaria y copia de cedula para tramitar el deposito esta semana.",
    "AVISO URGENTE BANCOLOMBIA: Por decision judicial tiene fondos retenidos a su nombre por valor de 6800000 pesos. Para reclamarlos antes del vencimiento ingrese sus datos en formulario adjunto: numero de cuenta, clave y cedula. El dinero sera depositado en 24 horas.",
    "Felicitaciones usted fue seleccionado como CLIENTE DISTINGUIDO del mes por el BANCO DAVIVIENDA. Como premio recibe un bono de 2000000 pesos. Para activar el bono confirme sus datos bancarios y clave de acceso en el portal premiodavivienda-seguro.net antes del viernes.",
    "Buen dia le informamos que su correo electronico resulto ganador de la LOTERIA DIGITAL EUROPA. Premio 380000 euros. Para procesar el pago de impuestos de su premio realice un pago de 800 euros via transferencia bancaria a la cuenta adjunta. Una vez confirmado recibiremos su premio en 48 horas.",
    "GOBIERNO DE COLOMBIA - PROGRAMA COLOMBIA MAYOR. Tiene un subsidio pendiente de cobro por valor de 900000 pesos por inactividad de beneficiario. Para activar el pago ingrese al portal con su cedula y datos de cuenta bancaria activa. El subsidio vence el ultimo dia del mes.",
    "Estimado senor, tengo acceso a fondos en el Banco Central de Nigeria por valor de 18 millones de dolares de un cliente fallecido. Necesito su colaboracion para mover estos fondos al exterior. Le ofrezco el 35% del total. Todo es legal y confidencial. Responda urgente con sus datos bancarios.",
    "PREMIO ESPECIAL ETB BOGOTA: Su linea telefonica fue seleccionada para recibir 500000 pesos de reembolso por fallas en el servicio. Para recibir el dinero confirme su numero de cuenta bancaria, nombre completo y numero de cedula en el formulario de compensacion adjunto antes de 72 horas.",
    "Usted tiene fondos disponibles en el sistema de compensacion de victimas del conflicto armado por 3200000 pesos. Para recibir el pago debe registrarse en la plataforma de la Unidad de Victimas ingresando su cedula, cuenta bancaria y clave bancaria de manera urgente.",
    "NOTIFICACION DE HERENCIA: El notario Luis Fernando Restrepo le informa que usted es beneficiario del testamento del senor Arturo Morales Martinez por valor de 450000000 pesos. Para iniciar el proceso legal envie copia de cedula, cuenta bancaria y pague honorarios notariales de 500000 pesos.",
    "Su perfil de MERCADO LIBRE fue seleccionado para el programa de vendedores elite. Recibe un credito de 5000000 pesos para inventario. Para activar el credito ingrese a mercadolibre-credito-elite.net con sus datos bancarios y confirme su identidad con cedula y clave de acceso.",
    "URGENTE EPM MEDELLIN: Su recibo de servicios publicos tiene un saldo a favor de 780000 pesos por cobro en exceso durante 2022. Para tramitar la devolucion ingrese al portal de EPM con su numero de contrato y datos bancarios. El reintegro vence el 30 de este mes.",
    "Estimado usuario, el BANCO DE OCCIDENTE tiene retenidos fondos a su nombre por herencia no reclamada de 4500000 pesos. Para recuperarlos debe verificar su identidad con numero de cedula, clave bancaria y numero de cuenta activa en el portal de reclamaciones adjunto antes del viernes.",
    "COMPENSACION PENSIONAL COLPENSIONES: Detectamos un error en su liquidacion pensional que le genera un reintegro de 1890000 pesos. Para recibir el dinero acceda al portal con su clave de acceso y numero de cedula e ingrese los datos de su cuenta bancaria para el deposito inmediato.",
    "Su numero de cedula fue incluido en el programa especial de compensacion por datos robados en la violacion de seguridad del 2022. Corresponde un pago de 350000 pesos. Para recibirlo ingrese sus datos bancarios en el portal seguro adjunto. Plazo maximo 5 dias habiles.",
]

# ---------------------------------------------------------------------------
# Más ejemplos PHISHING - Ingeniería social / trabajo falso (variados)
# ---------------------------------------------------------------------------
TRABAJO_V2 = [
    "OFERTA LABORAL URGENTE - Sin experiencia requerida. Empresa internacional busca personas para trabajar desde casa calificando productos en Amazon. Pago 80000 pesos por hora. Para aplicar descargue nuestra app e ingrese su numero de cedula y datos bancarios para activar su cuenta de trabajador.",
    "Hola! Vi tu hoja de vida en CompuTrabajo y creo que eres ideal para nuestro programa de representantes de ventas. Ganarias entre 3000000 y 8000000 pesos al mes sin limite. Para empezar necesito que deposites 300000 pesos como garantia de los productos que venderas. Te los devolvemos en el primer pago.",
    "CONVOCATORIA LABORAL BAVARIA: Empresa de bebidas contrata personal de planta en Bogota, Medellin y Cali. Salario 2800000 mas prestaciones. Para participar pague examen medico y estudio de seguridad por 200000 pesos a la cuenta Davivienda adjunta. Presentese el lunes con cedula y comprobante.",
    "Trabajo remoto para amas de casa y estudiantes. Empresa USA paga 30 dolares por hora para responder encuestas en linea. No requiere experiencia. Para empezar registrese con su cedula y cuenta bancaria en nuestra plataforma. Primer deposito de muestra: 50000 pesos en las proximas 2 horas.",
    "OPORTUNIDAD UNICA - AMAZON MECHANICAL TURK COLOMBIA. Busca digitadores de datos. Pago garantizado 150000 pesos diarios. Solo 3 horas de trabajo. Para activar su cuenta de trabajador pague el costo de afiliacion de 100000 pesos. Recupera la inversion en el primer dia de trabajo.",
    "Empresa de seguridad electronica contrata vigilantes y escoltas. Salario 2500000 mas dotacion. Para el proceso de contratacion debe pagar el estudio de confiabilidad y examen poligrafico por 400000 pesos. Realice el pago al numero de cuenta adjunto y presentese el martes con cedula.",
    "URGENTE: Empresa farmaceutica internacional contrata visitadores medicos para Colombia. Salario 5000000 mas carro. Para participar en la convocatoria registrese en el portal de empleo e ingrese sus datos bancarios para el pago anticipado de la primera semana como garantia del proceso.",
    "GRUPO NUTRESA busca promotores de ventas en todo el pais. No necesita experiencia. Salario 1800000 mas comisiones. Para inscribirse en la convocatoria debe depositar 150000 pesos de garantia en la cuenta adjunta. Los candidatos seleccionados recuperan el deposito en el primer pago de nomina.",
    "Hola soy Valentina reclutadora de empresa de cosmeticos. Vi tu perfil y creo que tienes lo necesario para ser parte de nuestro equipo de ventas. Ganarias de 4 a 10 millones al mes. Para comenzar solo necesitas hacer un pedido inicial de productos por 500000 pesos. Te los devolvemos en 30 dias.",
    "TELETRABAJO DISPONIBLE HOY: Empresa canadiense busca asistentes virtuales en Colombia. Pago 1200 dolares mensuales. Para el proceso de seleccion complete el formulario en linea con su nombre cedula cuenta bancaria y numero de whatsapp. Un agente se comunicara en 24 horas con el contrato virtual.",
    "CONVOCATORIA ABIERTA - HOTEL MARRIOTT CARTAGENA: Necesitamos recepcionistas, meseros y personal de aseo. Salarios desde 1900000. Para aplicar realice el pago de uniformes y examenes de admision por 350000 pesos a la cuenta Bancolombia adjunta. Plazas limitadas a 30 personas.",
    "FREELANCE BIEN PAGADO: Empresa de traduccion busca personas bilingues para traducir documentos. Pago 50000 pesos por pagina. Trabajo desde casa a su ritmo. Para comenzar complete el formulario de registro ingresando cedula y cuenta bancaria. Las asignaciones llegan al correo diariamente.",
    "Estimado profesional encontramos su hoja de vida en nuestros archivos. Tenemos una vacante de director comercial con salario de 15000000 pesos. Para confirmar su interes en la posicion necesitamos que pague la prueba psicotecnica online por 180000 pesos en el portal de evaluacion adjunto.",
    "EMPRESA DE SEGURIDAD PRIVADA contrata guardas de seguridad sin experiencia. Salario 2200000 mas auxilio de transporte. IMPORTANTE: Para el proceso debe pagar el uniforme inicial de 450000 pesos. Una vez contratado se descuenta de la primera quincena y nunca sale de su bolsillo. Contacte ya.",
    "Trabajo en casa calificando videos de YouTube. No requiere experiencia. Gana entre 80000 y 200000 pesos diarios. Solo necesitas internet y 2 horas libres. Para iniciar ingresa a nuestra plataforma con tu cedula y datos bancarios. Tu primer pago llega en 24 horas. Plazas limitadas actua ya.",
]

# ---------------------------------------------------------------------------
# Ejemplos SEGUROS en español (para reducir falsos positivos)
# ---------------------------------------------------------------------------
SEGUROS_ESPANOL = [
    "Estimado cliente, nos complace informarle que su solicitud de certificado bancario fue procesada exitosamente. Puede descargar el documento desde la sucursal virtual del banco en nuestra pagina oficial. Si tiene alguna inquietud no dude en comunicarse con nosotros por los canales oficiales.",
    "Apreciado estudiante le informamos que el proceso de matricula para el segundo semestre del ano academico ha sido habilitado. Para realizar su inscripcion acceda al portal estudiantil con sus credenciales. El plazo para matricula ordinaria es hasta el proximo viernes.",
    "Le confirmamos que su transferencia por valor de 500000 pesos fue realizada exitosamente. El dinero estara disponible en la cuenta destino en los proximos minutos. Guarde este mensaje como comprobante de la transaccion numero 987654321.",
    "Recordatorio: Su tarjeta de credito tiene un pago minimo de 250000 pesos con fecha limite el 25 de este mes. Para mayor comodidad realice su pago a traves de la sucursal virtual, cajero automatico o en cualquier corresponsal bancario. Gracias por ser nuestro cliente.",
    "Comunicado oficial: La jornada academica del proximo lunes queda suspendida por mantenimiento de la plataforma virtual. Las actividades se reanudan el martes a las 7am. Los docentes coordinaran con sus grupos el ajuste del cronograma de actividades pendientes.",
    "Su solicitud de cambio de contrasena fue procesada correctamente. Si usted no realizo esta solicitud comuniquese de inmediato con nuestra linea de atencion al cliente. Por su seguridad nunca compartimos su informacion con terceros ni le solicitamos datos por correo.",
    "Informamos a nuestros clientes que el dia sabado 15 de noviembre el servicio de banca en linea estara en mantenimiento de 2am a 6am. Disculpe los inconvenientes. Puede usar los cajeros automaticos con normalidad durante este periodo de mantenimiento programado.",
    "Apreciado afiliado su historia laboral actualizada esta disponible para consulta en el portal de Colpensiones. Para revisarla ingrese a nuestra pagina web con su numero de cedula. Si encuentra inconsistencias comunicase con nosotros a traves de los canales de atencion al ciudadano.",
    "Le informamos que la cuota de su credito de libranza por 850000 pesos fue debidamente aplicada el dia de hoy. Su saldo actual es de 12500000 pesos. Para consultar su estado de cuenta detallado puede acceder a la sucursal virtual de forma gratuita en nuestra pagina oficial.",
    "Confirmacion de cita medica: Tiene programada una consulta de medicina general el martes 19 de noviembre a las 10:30am en el centro medico. Si no puede asistir por favor cancele con 24 horas de anticipacion llamando a la linea de atencion o a traves del portal de la EPS.",
    "Estimado usuario, su factura del mes de octubre por servicios de internet por valor de 65000 pesos esta disponible para consulta y pago en nuestra pagina web. Recuerde que tiene hasta el dia 20 para realizar el pago sin recargo. Gracias por preferir nuestros servicios.",
    "Buen dia, este es un recordatorio de que mañana vence el plazo para presentar el informe final del proyecto de investigacion. Si tiene dificultades tecnicas con la plataforma puede enviar los documentos al correo de la coordinacion academica. Exitos en su entrega.",
    "CERTIFICADO DE AFILIACION: Adjunto encontrara el certificado de afiliacion al sistema de salud correspondiente al mes en curso. Este documento tiene validez oficial para tramites laborales y academicos. Para obtener certificados adicionales puede solicitarlos en nuestra pagina web.",
    "Su pago de seguro de vida por 45000 pesos fue procesado exitosamente para el mes de noviembre. Su poliza se encuentra vigente hasta el 30 de noviembre. Para consultar los detalles de su cobertura y beneficiarios acceda a la aplicacion movil o al portal web de la aseguradora.",
    "Respetado cliente, queremos informarle que a partir del 1 de diciembre se realizaran ajustes en las tarifas de algunos servicios debido al incremento del IPC. Consulte el detalle de los cambios en nuestra pagina web. Su confianza es muy importante para nosotros.",
    "NOTIFICACION DE NOMINA: Su pago de nomina correspondiente al periodo del 1 al 15 de noviembre fue consignado el dia de hoy en la cuenta registrada. Si tiene alguna novedad con su pago comuniquese con el departamento de recursos humanos dentro de los proximos 3 dias habiles.",
    "Estimado paciente, le recordamos que debe presentarse 15 minutos antes de su examen de laboratorio programado para manana a las 8am. No olvide traer la orden medica y su documento de identidad. Debe estar en ayunas de 8 horas para los examenes solicitados.",
    "Su solicitud de vacaciones por 15 dias habiles a partir del 25 de noviembre ha sido aprobada por su jefe inmediato. Su regreso programado es el 16 de diciembre. Para cualquier consulta comuniquese con el area de talento humano con anticipacion.",
    "Comunicamos a la comunidad universitaria que el proceso de inscripcion de asignaturas para el periodo academico 2025-1 estara disponible desde el lunes 18 de noviembre. Consulte el instructivo en el portal estudiantil. Atencion al estudiante resolvera sus inquietudes.",
    "Su solicitud de devolucion de IVA fue radicada exitosamente bajo el numero de radicado 2024-RIV-0045678. El plazo legal de respuesta es de 30 dias habiles. Puede hacer seguimiento a su solicitud en el portal tributario con su numero de NIT o cedula.",
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
    for text in ESTAFA_V2:
        new_rows.append({"text": text.strip(), "label": 1})
    for text in TRABAJO_V2:
        new_rows.append({"text": text.strip(), "label": 1})
    for text in SEGUROS_ESPANOL:
        new_rows.append({"text": text.strip(), "label": 0})

    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset="text", inplace=True)
    df_combined.to_csv(data_path, index=False)

    added = len(df_combined) - len(df_existing)
    print(f"Agregados: {added} ejemplos")
    print(f"  - Estafa financiera v2: {len(ESTAFA_V2)} phishing")
    print(f"  - Ingenieria social v2: {len(TRABAJO_V2)} phishing")
    print(f"  - Correos seguros espanol: {len(SEGUROS_ESPANOL)} seguros")
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
