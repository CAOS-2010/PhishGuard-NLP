"""
Agrega ejemplos sintéticos en español para las 3 categorías de phishing
que fallan: estafa financiera, suplantación de autoridad (DIAN),
e ingeniería social avanzada (oferta de trabajo falsa).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

# ---------------------------------------------------------------------------
# 1. ESTAFA FINANCIERA (herencia, premio, comisión)
# ---------------------------------------------------------------------------
ESTAFA_FINANCIERA = [
    "Estimado beneficiario, le informamos que usted ha sido seleccionado para recibir la suma de CINCO MILLONES DE DÓLARES como parte de la herencia del difunto empresario Fernando Lagos. Para procesar la transferencia necesitamos sus datos bancarios completos incluyendo número de cuenta y clave de acceso. Responda urgentemente antes de que el plazo venza.",
    "NOTIFICACIÓN OFICIAL DE TRANSFERENCIA INTERNACIONAL. Su dirección de correo electrónico ganó el premio mayor de nuestra rifa internacional. Premio: $850,000 USD. Para reclamar su premio debe pagar una comisión de liberación de fondos de $350. Contacte al agente autorizado en las próximas 48 horas o perderá el premio.",
    "Soy el abogado de confianza del señor James Okafor, ciudadano nigeriano fallecido sin herederos. Su apellido coincide con el del difunto y según la ley podemos registrarle como beneficiario de $4,200,000 USD. Todo lo que necesita es enviar sus datos bancarios y copia de su documento de identidad para iniciar el trámite legal.",
    "BANCO MUNDIAL DE COMPENSACIONES le informa que tiene fondos retenidos a su nombre por valor de $1,700,000 dólares americanos. Estos fondos corresponden a compensaciones por fraudes anteriores. Para desbloquear el dinero debe pagar un arancel de transferencia de $200 dólares. Envíe el pago vía Western Union y recibirá sus fondos en 24 horas.",
    "Felicitaciones! Su número de teléfono fue seleccionado ganador del sorteo TELECOMUNICACIONES COLOMBIA 2024. Premio en efectivo: $25,000,000 pesos. Para reclamar su premio llame ahora al 01-800-PREMIO o haga clic aquí y proporcione su número de cédula, cuenta bancaria y clave de acceso. Plazo máximo: hoy a las 11:59 PM.",
    "Estimado cliente, tiene pendiente una herencia de su tío abuelo residente en España por valor de €780,000. Los herederos anteriores renunciaron y usted es el único beneficiario válido. Necesitamos su número de cuenta bancaria para depositar los fondos. El proceso es completamente legal pero debe actuar antes del 15 de este mes.",
    "FONDO MONETARIO INTERNACIONAL - COLOMBIA. Usted ha sido identificado como beneficiario de fondos de compensación por $3,500,000 pesos. Estos fondos son el resultado de un acuerdo de reparación. Para recibir el depósito ingrese a este enlace y confirme su identidad con su clave bancaria y número de cuenta. No comparta este correo.",
    "Su correo electrónico resultó ganador en el sorteo internacional EUROMILLONES DIGITAL. Premio: €500,000. Para procesar el pago de su premio debe primero cancelar los impuestos de ganancia por valor de $1,200 dólares. Una vez confirmado el pago sus fondos serán transferidos en 48 horas. Contacte a nuestro agente en Ginebra.",
    "AVISO LEGAL URGENTE: Existen fondos bloqueados a su nombre en el Banco de Reservas por valor de $8,900,000 pesos. Estos fondos corresponden a una herencia legítima que vence en 30 días. Para reclamarlos ingrese sus datos en el formulario adjunto incluyendo número de cuenta, nombre completo y copia de cédula. Actúe ya.",
    "Estimado amigo, trabajo en el departamento de transferencias del Banco Central Africano. Tengo acceso a fondos de $21,000,000 millones de dólares de un cliente fallecido. Necesito un socio de confianza en su país para trasladar este dinero. Usted recibirá el 40% si me ayuda. Todo completamente confidencial. Responda urgente.",
    "PREMIO ESPECIAL MOVISTAR COLOMBIA: Como cliente premiado ha ganado un bono de $500,000 pesos y un smartphone. Para recibir su premio confirme sus datos: número de cédula, fecha de nacimiento, y los últimos 4 dígitos de su tarjeta de crédito. Su código de reclamación vence en 24 horas. No deje pasar esta oportunidad.",
    "Alerta de transferencia pendiente a su favor: $4,500,000 pesos de una cuenta inactiva en Davivienda serán asignados a beneficencia si usted no reclama en 72 horas. Para reclamar estos fondos como beneficiario legítimo debe verificar su identidad ingresando a la plataforma segura y proporcionando su número de cuenta y clave.",
    "Buenos días, le escribo de parte de la firma jurídica Lagos & Asociados de Madrid. Representamos a la sucesión del señor Roberto Ángel Mora, colombiano fallecido en España sin herederos directos. Tras investigar el árbol genealógico lo identificamos como heredero legítimo de €340,000. Necesitamos sus datos bancarios para iniciar el proceso legal.",
    "NOTIFICACIÓN DE HERENCIA INTERNACIONAL: Por medio del presente le informamos que ha sido identificado como beneficiario del testamento del Dr. Emmanuel Adeyemi. El valor de la herencia asciende a $6,200,000 USD. Para proceder con la transferencia requerimos número de cuenta bancaria, nombre completo, dirección y copia de documento de identidad.",
    "LOTERÍA NACIONAL DIGITAL sorteo especial: Su número de participación 4872-XK ganó el PRIMER PREMIO de $50,000,000 pesos colombianos. Para reclamar debe pagar el impuesto de ganancia ocasional del 2% equivalente a $1,000,000 pesos. Realice el pago por Nequi o Daviplata al número 3001234567 y en 2 horas recibirá su premio.",
    "Su cuenta ha sido seleccionada para recibir un beneficio especial del Gobierno Nacional por valor de $800,000 pesos como compensación del programa de ayudas. Para activar el desembolso ingrese a la plataforma del ICBF con su clave bancaria y confirme sus datos personales. El beneficio vence en 48 horas si no lo reclama.",
    "Estimado señor, soy el director financiero de una empresa multinacional y necesito trasladar urgentemente $15,000,000 dólares fuera del país. Le ofrezco el 30% de esta suma si me permite usar su cuenta bancaria para la transferencia. La operación es legal y confidencial. Por favor envíe sus datos bancarios completos a la brevedad.",
    "OFERTA ESPECIAL BANCOLOMBIA: Ha sido seleccionado para un crédito pre-aprobado de $50,000,000 pesos a tasa 0% por 12 meses. Para activarlo solo necesita pagar una comisión de estudio de $80,000 pesos. Realice el pago al número de cuenta adjunto y en 24 horas tendrá el dinero en su cuenta. Oferta válida solo hoy.",
    "MINISTERIO DE HACIENDA - REINTEGRO TRIBUTARIO: Según revisión de su declaración de renta tiene un saldo a favor de $2,340,000 pesos. Para hacer efectivo el reintegro ingrese a la plataforma con su RUT y clave tributaria. Adjunte copia de cuenta bancaria y en 5 días hábiles recibirá el dinero. Consulte en dian.gov.co.secure-refund.net",
    "URGENTE - FONDOS BLOQUEADOS: El Banco AV Villas tiene retenidos $3,200,000 en su nombre por inactividad de cuenta. Para desbloquear los fondos debe verificar su identidad ingresando su cédula, fecha de nacimiento y clave bancaria en el siguiente formulario. Si no actúa en 72 horas los fondos serán transferidos a la beneficencia.",
    "Ganó $30,000 dólares en nuestra rifa internacional de patrocinadores. Su correo fue elegido aleatoriamente entre millones de participantes. Para procesar su premio necesitamos que pague el seguro de transferencia de $150 dólares. Aceptamos PayPal, Western Union o tarjeta de crédito. Responda con sus datos personales para continuar.",
    "COMPENSACIÓN POR LLAMADAS PERDIDAS: Según nuestros registros usted fue afectado por fallas en el servicio de telecomunicaciones entre 2021-2023. Tiene derecho a una compensación de $450,000 pesos. Para recibirla haga clic en el enlace adjunto, ingrese su número de cédula y datos bancarios. Plazo: 5 días hábiles.",
    "Estimado usuario, la Corporación Financiera Internacional tiene fondos a su disposición provenientes de un proyecto de cooperación. El monto asignado es de $12,000,000 pesos. Para recibirlos debe abrir una cuenta especial en nuestro banco corresponsal y depositar $500,000 como capital inicial. Los fondos serán duplicados en 30 días.",
    "ALERTA: Su número de teléfono ganó el SORTEO CLARO 25 ANIVERSARIO. Premio: $10,000,000 pesos en efectivo + 2 años de plan gratis. Para reclamar llame al 018000123456 o ingrese en claro-premios-colombia.com con su número de cédula y datos de cuenta bancaria. Válido solo las próximas 12 horas. No deje pasar esta oportunidad única.",
    "Por este medio le informamos que usted es beneficiario de los fondos de compensación establecidos en el Acuerdo de Paz de Colombia. Le corresponde la suma de $4,800,000 pesos. Para gestionar el desembolso debe dirigirse a nuestro portal con su clave de acceso del banco y número de cuenta corriente o ahorros activa.",
]

# ---------------------------------------------------------------------------
# 2. SUPLANTACIÓN DE AUTORIDAD — DIAN / entidades colombianas
# ---------------------------------------------------------------------------
AUTORIDAD_DIAN = [
    "DIRECCIÓN DE IMPUESTOS Y ADUANAS NACIONALES - DIAN. Su empresa figura con inconsistencias en la declaración de renta del año gravable 2023. Se ha iniciado un proceso de fiscalización que puede resultar en sanción de $12,500,000 pesos. Para evitar sanciones debe actualizar su RUT y pagar el valor en disputa. Ingrese en dian.gov.co.verificacion-urgente.net",
    "NOTIFICACIÓN OFICIAL DIAN: Según nuestros sistemas su número de RUT presenta información desactualizada lo que activa un proceso de suspensión automática. Tiene 3 días hábiles para actualizar sus datos en el portal tributario. Ingrese con su NIT o cédula y contraseña en el siguiente enlace. Evite sanciones económicas y penales.",
    "SUPERSOCIEDADES COLOMBIA - CITACIÓN JUDICIAL. Su empresa ha sido incluida en un proceso de liquidación por deudas con el sistema financiero. Para evitar el embargo de sus cuentas debe presentar sus descargos en línea en las próximas 48 horas. Acceda con su NIT y clave de acceso al portal web de Supersociedades adjunto.",
    "UNIDAD DE INFORMACIÓN Y ANÁLISIS FINANCIERO - UIAF. Su cuenta bancaria ha sido marcada como sospechosa de lavado de activos. Para evitar el bloqueo definitivo de sus cuentas y una investigación penal debe responder a este cuestionario de verificación de identidad de manera urgente. Adjunte copia de cédula y extractos bancarios.",
    "POLICIA NACIONAL DE COLOMBIA - DIVISIÓN CIBERNÉTICA. Hemos detectado que su dirección IP fue usada para acceder a contenido ilegal. Tiene una orden de investigación preliminar a su nombre. Para evitar su captura debe pagar una multa de $850,000 pesos en las próximas 6 horas. Realice el pago en el portal adjunto y archive el caso.",
    "MINISTERIO DE SALUD Y PROTECCIÓN SOCIAL - REGISTRO ESPECIAL. Su EPS figura con inconsistencias en el sistema de afiliados. Debe actualizar su información de manera urgente o será desafiliado del sistema de salud. Ingrese a la plataforma del Ministerio con su cédula y clave para actualizar sus datos y mantener activos sus beneficios.",
    "CONTRALORÍA GENERAL DE LA REPÚBLICA. Su empresa fue seleccionada en un proceso de auditoría especial. Se encontraron irregularidades por $3,400,000 pesos en contratos estatales. Para evitar sanciones disciplinarias y penales debe responder el pliego de cargos adjunto en 24 horas. Ingrese al portal con su firma digital.",
    "DIAN OFICIAL - RETENCIÓN EN LA FUENTE: Detectamos que no realizó la retención en la fuente del mes de agosto. Esto genera una sanción automática de $2,100,000. Para corregir esta situación ingrese al portal de la DIAN con su usuario y contraseña y realice la declaración correctiva. De lo contrario su RUT será suspendido.",
    "PROCURADURÍA GENERAL DE LA NACIÓN - INVESTIGACIÓN DISCIPLINARIA. Ha sido vinculado a un proceso disciplinario por presunta irregularidad en el ejercicio de funciones públicas. Tiene 48 horas para presentar sus descargos de manera virtual. Ingrese al sistema de información disciplinaria con su número de cédula y código de proceso adjunto.",
    "FISCALÍA GENERAL DE LA NACIÓN. Existe una orden de comparendo en su contra por delito informático. Para evitar la captura preventiva debe pagar la caución equivalente a $1,200,000 pesos en las próximas 24 horas. Realice el pago en el portal de la Fiscalía adjunto. Guarde el comprobante como evidencia de cumplimiento.",
    "INVIMA - INSTITUTO NACIONAL DE VIGILANCIA DE MEDICAMENTOS. Su establecimiento comercial fue reportado por venta de productos sin registro sanitario. Tiene una multa pendiente de $4,500,000 pesos. Para impugnar esta multa ingrese al sistema de trámites del INVIMA con su número de matrícula mercantil en el enlace adjunto antes del viernes.",
    "MINISTERIO DE TRABAJO DE COLOMBIA - INSPECCIÓN LABORAL. Su empresa fue demandada por un ex empleado por incumplimiento en el pago de prestaciones sociales. La demanda asciende a $8,700,000 pesos. Para mediar el proceso de manera extrajudicial ingrese al portal del Ministerio y descargue el formulario de conciliación adjunto.",
    "DIAN - DEVOLUCIÓN DE IVA: Detectamos que tiene un saldo a favor en IVA por $1,890,000 pesos correspondiente al período enero-junio 2023. Para gestionar la devolución ingrese al portal de la DIAN con su clave tributaria y diligencie el formulario 597. El trámite vence el 31 de este mes. Acceda: dian.gov.co.reembolso-iva.net",
    "BANCO DE LA REPÚBLICA DE COLOMBIA - ALERTA DE SEGURIDAD. Hemos detectado movimientos inusuales en cuentas asociadas a su número de cédula. Para evitar el congelamiento de sus fondos debe verificar su identidad en el sistema de monitoreo financiero. Acceda con su clave bancaria y confirme sus últimas 5 transacciones en el portal adjunto.",
    "NOTIFICACIÓN ALCALDÍA DE MEDELLÍN: Tiene multas de tránsito pendientes por $1,340,000 pesos que generan intereses de mora diariamente. Si no paga antes del 30 de este mes su vehículo será inmovilizado y sus cuentas bancarias embargadas. Ingrese al portal de pagos de la Alcaldía con su cédula y número de placa para regularizar.",
    "UGPP - UNIDAD DE GESTIÓN PENSIONAL Y PARAFISCALES. Su empresa presenta mora en el pago de aportes a seguridad social por $6,200,000 pesos. Se ha iniciado un proceso coactivo que puede resultar en embargo de cuentas. Para evitar esto acceda al portal de la UGPP con su NIT y realice el pago o un acuerdo de pago en 48 horas.",
    "SIC - SUPERINTENDENCIA DE INDUSTRIA Y COMERCIO. Su empresa recibió una denuncia por prácticas comerciales engañosas. Tiene 5 días para presentar descargos o se impondrá una multa de $15,000,000 pesos. Acceda al sistema de trámites virtuales de la SIC con su NIT y descargue el pliego de cargos completo. Fecha límite: viernes 5PM.",
    "SECRETARÍA DE HACIENDA DISTRITAL - PREDIAL BOGOTÁ. Su predio presenta una deuda en impuesto predial de $2,340,000 pesos correspondiente a los años 2022-2023. Si no cancela antes del 30 de noviembre se iniciará proceso jurídico de cobro coactivo. Ingrese al portal de pagos con el número de chip catastral adjunto y regularice su deuda.",
    "MIGRACIÓN COLOMBIA - ALERTA MIGRATORIA. Hemos detectado inconsistencias en su pasaporte y situación migratoria. Tiene una investigación activa que puede resultar en restricción de salida del país. Para resolver esta situación ingrese al portal de Migración Colombia con su número de pasaporte y cédula en las próximas 24 horas.",
    "DIAN - PROCESO DE COBRO COACTIVO: Su número de identificación tributaria tiene deudas ejecutoriadas con la DIAN por $9,200,000 pesos. Se han iniciado medidas cautelares sobre sus cuentas bancarias. Para detener el embargo definitivo debe realizar un acuerdo de pago en el portal tributario. Acceda urgentemente: portal-dian-coactivo.gov.co.pagos.net",
    "MINISTERIO DE EDUCACIÓN NACIONAL. Según nuestros registros, el título profesional que presentó en sus documentos de trabajo presenta irregularidades. Tiene 72 horas para validar su título en el SNIES o se reportará a las autoridades. Ingrese al sistema con su número de cédula y código de título. Evite consecuencias legales.",
    "REGISTRADURÍA NACIONAL DEL ESTADO CIVIL. Su cédula de ciudadanía presenta alertas de uso fraudulento. Se recomienda actualizar biométricos urgentemente para evitar que terceros usen su identidad. Ingrese al portal seguro de la Registraduría con su número de cédula y código OTP enviado a su correo para verificar su identidad.",
    "SERVICIO NACIONAL DE APRENDIZAJE - SENA. Tiene una certificación SENA suspendida por irregularidades en el proceso de formación. Para reactivarla debe actualizar su información en el sistema Sofia Plus con su número de cédula y contraseña. Si no lo hace en 5 días hábiles la certificación será anulada definitivamente.",
    "COMISIÓN DE REGULACIÓN DE COMUNICACIONES - CRC. Su proveedor de internet fue multado y como consecuencia debe recibir una compensación de $340,000 pesos. Para recibir el reembolso confirme sus datos bancarios en el portal de compensaciones de la CRC. Ingrese con su número de cédula y cuenta bancaria activa antes del 15 de diciembre.",
    "COLPENSIONES - NOTIFICACIÓN DE SEMANAS: Detectamos un error en el registro de sus semanas cotizadas al sistema pensional que le afecta negativamente. Para corregir este error debe ingresar al portal de Colpensiones con su clave de acceso y adjuntar los soportes de cotización. Actúe antes de fin de mes para evitar afectación a su pensión.",
]

# ---------------------------------------------------------------------------
# 3. INGENIERÍA SOCIAL AVANZADA — oferta de trabajo falsa
# ---------------------------------------------------------------------------
INGENIERIA_SOCIAL = [
    "Estimado candidato, tras revisar su perfil en LinkedIn hemos decidido contactarle para ofrecerle una posición en nuestra empresa internacional. El cargo es Analista de Datos con salario de $8,500,000 pesos mensuales más beneficios. Para continuar con el proceso de selección necesitamos que complete el formulario adjunto con sus datos personales, bancarios y suba copia de su cédula.",
    "OPORTUNIDAD LABORAL URGENTE: Empresa multinacional busca representantes comerciales para trabajo desde casa. Gane entre $3,000,000 y $6,000,000 pesos mensuales. No se requiere experiencia. Solo necesita internet y disposición. Para aplicar envíe su hoja de vida más copia de cédula y cuenta bancaria donde recibirá su primer pago de comisión.",
    "CONVOCATORIA LABORAL - COLCAFÉ EXPORTACIONES. Estamos contratando 50 personas para trabajo de empaque en planta. Salario: $2,800,000 + prestaciones + horas extras. Para participar en la convocatoria deposite $200,000 pesos como garantía de uniforme en la cuenta adjunta y preséntese el lunes con su cédula y cuenta bancaria.",
    "TRABAJO DESDE CASA - GANE $150,000 PESOS DIARIOS: Empresa de marketing digital busca personas para calificar contenido en redes sociales. No necesita experiencia ni título. Solo 2 horas diarias de trabajo. Para iniciar descargue nuestra aplicación e ingrese su número de cédula y datos bancarios para recibir su primer pago de bienvenida de $50,000.",
    "Hola! Vi tu perfil y creo que eres la persona indicada para una oportunidad increíble. Nuestra empresa de criptomonedas está contratando asistentes de cuenta con salario base de $4,000,000 + comisiones ilimitadas. Trabajo 100% remoto. Solo necesitas abrir una cuenta en nuestra plataforma con $500,000 de depósito inicial y empezamos esta semana.",
    "CONVOCATORIA LABORAL BANCO DAVIVIENDA 2024: Necesitamos asesores comerciales en toda Colombia. Salario: $3,200,000 + comisiones hasta $2,000,000. Para aplicar ingrese su hoja de vida en el portal de empleo Davivienda. Importante: debe pagar exámenes médicos por valor de $180,000 pesos antes de la entrevista. Consignación a la cuenta adjunta.",
    "OFERTA DE TRABAJO INTERNACIONAL - TRABAJO EN CANADÁ: Empresa agroindustrial en Ontario busca trabajadores colombianos. Salario en dólares canadienses equivalente a $12,000,000 pesos mensuales. Alojamiento y alimentación incluidos. Para tramitar la visa de trabajo debe pagar gastos consulares de $1,500,000 pesos. Contacte a nuestro agente en Bogotá.",
    "Estimado postulante, su hoja de vida fue preseleccionada para el cargo de COMMUNITY MANAGER en reconocida empresa de medios. Salario: $3,800,000 + trabajo remoto. Para confirmar su participación en la entrevista virtual debe adquirir el kit de evaluación psicotécnica en línea por $95,000 pesos. Sin este paso no podemos continuar el proceso.",
    "EMPLEO URGENTE - CONDUCTOR PARA EMPRESA LOGÍSTICA: Necesitamos 20 conductores con pase C o E. Salario: $2,500,000 + rodamiento. Para ingresar debe pagar el estudio de seguridad y examen toxicológico por $250,000 pesos en la cuenta indicada. Preséntese el martes con recibo de pago, cédula y licencia. Cupos limitados.",
    "Hola [nombre], te contactamos de parte de AMAZON COLOMBIA. Estamos abriendo centro de distribución en tu ciudad y necesitamos personal de bodega. Salario $2,100,000 + prestaciones. Para agendar tu entrevista debes registrarte en nuestra plataforma de selección e ingresar tu número de cédula y datos bancarios para el pago de la primera quincena anticipada.",
    "CONVOCATORIA LABORAL ECOPETROL 2024: Contratamos operadores de campo, ingenieros y técnicos. Salarios desde $5,000,000. Proceso 100% virtual. Para participar pague los derechos de inscripción al concurso de $300,000 pesos en PSE o Efecty y regístrese en el portal de convocatorias adjunto. Plazas limitadas. Cierre de inscripciones viernes.",
    "OPORTUNIDAD: Empresa de inversiones busca captadores de clientes. Gane el 10% de comisión sobre cada cliente que traiga. En promedio nuestros captadores ganan $5,000,000 mensuales. Para empezar debe abrir una cuenta de demostración con un depósito de $1,000,000 pesos para mostrar seriedad. Le duplicamos esa inversión en el primer mes.",
    "TRABAJO EN CASA - DIGITADORES DE DATOS: Empresa norteamericana contrata personas de Colombia para captura de datos. Pago: $500 pesos por registro completado. Promedio: $200,000 diarios. Para empezar descargue el software especial en el enlace adjunto e ingrese su cédula y datos bancarios para recibir las primeras asignaciones de trabajo hoy mismo.",
    "CONTRATACIÓN DIRECTA CLARO COLOMBIA: Necesitamos asesores call center para trabajo desde casa. Salario fijo $2,200,000 + variable. Para el proceso de contratación debe pagar $150,000 de afiliación al plan de beneficios corporativos. Realice el pago al número de cuenta adjunto y en 24 horas recibirá sus credenciales de acceso al sistema.",
    "GRAN OPORTUNIDAD LABORAL - EMPRESA ISRAELÍ: Buscamos colombianos para trabajo en seguridad privada en Tel Aviv. Salario: $18,000,000 pesos mensuales. Incluye visa, tiquetes y alojamiento. Para aplicar envíe copia de cédula, pasaporte y datos bancarios. Se requiere un depósito de garantía de $800,000 pesos reembolsable al inicio del contrato.",
    "Estimado profesional, hemos revisado su perfil de LinkedIn y consideramos que es ideal para nuestra vacante de GERENTE DE ZONA con salario de $12,000,000 + vehículo. Para continuar con la selección necesitamos que realice una prueba técnica en línea. La plataforma de evaluación tiene un costo de $120,000. Ingrese con su cédula al portal adjunto.",
    "CONVOCATORIA ABIERTA - TRABAJO EN BUQUES: Empresa naviera internacional contrata marineros, cocineros y personal de limpieza. Salario mínimo $8,000,000 más propinas. No requiere experiencia previa. Para tramitar documentos marítimos y visa debe pagar $2,000,000 de gestión. Le devolvemos el dinero al abordar el primer barco. Contacte ahora.",
    "ALERTA DE EMPLEO - TIEMPO LIMITADO: Reconocida empresa de cosméticos busca distribuidores independientes en Colombia. Gane desde $4,000,000 mensuales vendiendo desde casa. Para iniciar su kit de distribución tiene un costo de $450,000 pesos. Incluye productos de muestra y acceso a la plataforma de ventas. Cupos solo hasta agotar existencias.",
    "Hola, encontré tu perfil y me parece que tienes el talento que buscamos. Soy reclutadora de empresa tecnológica en Silicon Valley. El puesto es tester de aplicaciones móviles con pago de $200 dólares diarios. Para comenzar necesito tu nombre completo, cédula, cuenta bancaria y acceso a tu correo para registrarte en nuestra plataforma de trabajo remoto.",
    "EMPLEO INMEDIATO - SIN EXPERIENCIA: Empresa de mensajería contrata repartidores con o sin moto. Pago por entrega entre $3,000 y $8,000 pesos. Gane más de $150,000 diarios. Para registrarse como repartidor debe pagar el kit de herramientas de seguridad por $280,000 pesos. Consigne al número de cuenta adjunto y reciba su primer pedido hoy.",
    "TRABAJO REMOTO EMPRESA USA: Buscamos asistentes virtuales hispanohablantes. Pago $15 USD por hora. Contrato inicial 3 meses con opción de permanencia. Para firmar contrato necesitamos copia de cédula escaneada, número de cuenta bancaria y contraseña de su correo electrónico principal para integración con nuestros sistemas corporativos de gestión.",
    "OFERTA LABORAL PETROBRAS COLOMBIA: Contratamos topógrafos, operadores y conductores para proyecto en el Llano. Salario $6,500,000 + viáticos. Proceso de selección online. Para la prueba psicotécnica virtual pague $200,000 en el portal adjunto. Los candidatos aprobados iniciaran inducción el próximo lunes. Plazas limitadas a 30 personas.",
    "¡Felicitaciones! Tras analizar su perfil fue seleccionado para el programa EMPRENDEDOR DEL AÑO. Como ganador recibirá $10,000,000 de capital semilla para su empresa. Para acceder al desembolso debe completar el formulario en línea con sus datos bancarios y pagar el seguro de fidelización de $350,000 pesos. Dinero garantizado en 72 horas.",
    "CONVOCATORIA LABORAL - HOSPITAL UNIVERSITARIO: Necesitamos auxiliares de enfermería, personal de aseo y administrativos. Salarios entre $1,800,000 y $3,500,000. Para el proceso de selección descargue y diligencie el formulario adjunto con sus datos personales, bancarios y número de cuenta donde recibirá el anticipo de 15 días al ser contratado.",
    "MULTINACIONAL ALEMANA BUSCA EMPLEADOS EN COLOMBIA: Requiere técnicos electrónicos y mecánicos para planta en Bogotá. Salario $5,800,000 + beneficios. Para aplicar regístrese en nuestra plataforma de empleo ingresando cédula, datos bancarios y clave de acceso a su correo corporativo actual. Entrevistas virtuales la próxima semana. No deje pasar esta oportunidad.",
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
    for text in ESTAFA_FINANCIERA:
        new_rows.append({"text": text.strip(), "label": 1})
    for text in AUTORIDAD_DIAN:
        new_rows.append({"text": text.strip(), "label": 1})
    for text in INGENIERIA_SOCIAL:
        new_rows.append({"text": text.strip(), "label": 1})

    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset="text", inplace=True)
    df_combined.to_csv(data_path, index=False)

    added = len(df_combined) - len(df_existing)
    print(f"Agregados: {added} ejemplos")
    print(f"  - Estafa financiera: {len(ESTAFA_FINANCIERA)}")
    print(f"  - Suplantación autoridad (DIAN): {len(AUTORIDAD_DIAN)}")
    print(f"  - Ingeniería social (trabajo): {len(INGENIERIA_SOCIAL)}")
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
