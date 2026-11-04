"""Test rapido de las 10 categorias de phishing."""
import sys
sys.path.insert(0, r"D:\SEMESTRE 10\TRABAJO DE GRADO 2\PhishGuard-NLP")

from src.core.classifier import PhishingClassifier

clf = PhishingClassifier()

tests = [
    ("ESTAFA FINANCIERA", "Estimado beneficiario, le informamos que ha sido seleccionado para recibir CINCO MILLONES DE DOLARES como parte de la herencia del difunto empresario fallecido. Para procesar la transferencia necesitamos sus datos bancarios completos incluyendo numero de cuenta y clave de acceso. Responda urgentemente antes de que el plazo venza manana.", "phishing"),
    ("SUPLANTACION DIAN", "DIRECCION DE IMPUESTOS Y ADUANAS NACIONALES DIAN. Su empresa figura con inconsistencias en la declaracion de renta del ano gravable 2023. Se ha iniciado proceso de fiscalizacion que puede resultar en sancion de 12500000 pesos. Para evitar sanciones debe actualizar su RUT e ingresar clave tributaria en dian.gov.co.verificacion-urgente.net urgentemente.", "phishing"),
    ("INGENIERIA SOCIAL TRABAJO", "Estimado candidato, tras revisar su perfil en LinkedIn hemos decidido contactarle para ofrecerle vacante como Analista de Datos con salario de 8500000 pesos mensuales mas beneficios. Para continuar el proceso de seleccion necesitamos que complete el formulario adjunto con sus datos personales bancarios y suba copia de su cedula de ciudadania.", "phishing"),
    ("BANCARIO CLASICO", "Estimado cliente Bancolombia, su cuenta ha sido temporalmente bloqueada por seguridad. Para restablecer el acceso ingrese AHORA a bancolombia-seguro.co y confirme su clave de acceso. Si no verifica en 24 horas perdera acceso permanentemente a su cuenta.", "phishing"),
    ("SOPORTE TECNICO FALSO", "MICROSOFT TECHNICAL SUPPORT ALERT. Your Windows license has expired and your computer is at risk of serious damage. Call our toll-free number immediately 1-800-555-0199 to renew your license and remove detected viruses. Do not turn off your computer.", "phishing"),
    ("ROBO CREDENCIALES TDEA", "Estimado estudiante su cuenta de correo institucional del TDEA ha sido comprometida. Debe verificar su identidad AHORA MISMO haciendo clic en el enlace adjunto e ingresando su usuario y contrasena institucional. Si no verifica en 2 horas su cuenta sera eliminada permanentemente del sistema.", "phishing"),
    ("SUPLANTACION MICROSOFT", "URGENT NOTICE: Your Microsoft account access.verify-microsoft-login.net has been suspended due to suspicious activity. Click here immediately to verify your identity and restore access to your Office 365. Failure to act within 24 hours will result in permanent account deletion.", "phishing"),
    ("CORREO SEGURO BANCO", "Estimado cliente, le informamos que su extracto bancario del mes de octubre esta disponible en la sucursal virtual. Ingrese a nuestra pagina oficial www.bancolombia.com con sus credenciales habituales para consultarlo. Comuniquese al 018000912345 si tiene dudas.", "seguro"),
    ("CORREO SEGURO INST", "Estimado estudiante, le recordamos que el periodo de matriculas para el semestre 2025-1 inicia el 15 de enero. Consulte el calendario academico en el portal estudiantil con su usuario y contrasena institucional. Comuniquese con la oficina de registro si tiene inquietudes.", "seguro"),
    ("CORREO SEGURO MICROSOFT REAL", "Dear user, your Microsoft 365 subscription has been renewed successfully. Your next billing date is December 1 2024. To manage your subscription visit account.microsoft.com. Contact our support team if you have any questions about your account.", "seguro"),
]

print("Resultados - modelo con ejemplos espanol agregados:")
print("-" * 80)
ok_count = 0
for name, text, expected in tests:
    result = clf.predict(text)
    label = result.label
    conf = result.confidence
    is_ok = (label == expected)
    ok_count += is_ok
    status = "OK  " if is_ok else "FALLO"
    print(f"{status}  {name:<30} {label:<10} {conf:.1%}  (esperado: {expected})")

print(f"\nTotal: {ok_count}/{len(tests)} correctos ({ok_count/len(tests):.0%})")
