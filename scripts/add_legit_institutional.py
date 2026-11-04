"""Agrega correos institucionales legítimos para reducir falsos positivos."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

LEGIT_INSTITUTIONAL = [
    # TDEA - pago de matrícula (el falso positivo reportado)
    "Cordial saludo. Te informamos que tu Orden de Matricula ha sido actualizada en el Sistema Campus con fecha de pago inmediato. El plazo se ha agotado y las clases ya inician, por lo que le solicitamos realizar el pago de inmediato a traves de su plataforma Campus para evitar la anulacion de su liquidacion, la perdida de su cupo y asegurar su estado oficial de matriculado. Ingresa al Sistema Campus con tu usuario y contrasena. Ve a la ruta Servicios Financiero. Haz clic en el icono de la impresora para descargar la orden. Medios de pago autorizados. En linea PSE Tarjeta de Credito. En efectivo presencial en cualquier sucursal nacional del Banco Popular o Davivienda presentando la orden impresa.",
    # Recordatorio de pago de matrícula universitaria
    "Estimado estudiante, le recordamos que la fecha limite para el pago de su matricula del periodo 2025-1 es el proximo viernes 31 de enero. Puede realizar el pago en linea a traves del portal estudiantil en la seccion de Pagos, o presencialmente en cualquier banco autorizado con su orden de matricula impresa. Para consultar el valor exacto de su liquidacion acceda al portal con su usuario institucional. Ante cualquier duda comuniquese con la oficina de registro academico.",
    # Confirmación de pago de matrícula
    "Apreciado estudiante, confirmamos que el pago de su matricula correspondiente al periodo academico 2025-1 fue registrado exitosamente en el sistema por un valor de 3850000 pesos. Su estado academico ha sido actualizado a MATRICULADO. Puede descargar su certificado de matricula desde el portal estudiantil. Le deseamos un excelente semestre.",
    # Recordatorio de contraseña vencida (legítimo)
    "Estimado usuario, su contrasena de acceso al sistema institucional vencera en 5 dias. Le recomendamos actualizarla ingresando al portal con sus credenciales actuales y seleccionando la opcion Cambiar contrasena en el menu de configuracion de cuenta. Si tiene dificultades comuniquese con soporte tecnico a traves del portal de servicios.",
    # Notificación de crédito educativo ICETEX
    "Apreciado beneficiario, le informamos que el desembolso de su credito educativo ICETEX correspondiente al segundo semestre ha sido procesado. El valor de 4200000 pesos sera aplicado directamente a su cuenta de matricula segun el convenio con la institucion educativa. Para consultar el estado de su credito ingrese al portal ICETEX con su usuario y contrasena habitual.",
    # Pago de servicios EPM - factura
    "Estimado cliente, le informamos que su factura de servicios publicos del mes de octubre por valor de 185000 pesos esta disponible para consulta y pago. Puede realizar el pago en linea a traves de nuestra sucursal virtual, en cajeros automaticos, o en cualquier punto de pago autorizado. Para consultar su factura y realizar el pago ingrese a nuestro portal oficial con su numero de contrato.",
    # Extracto bancario legítimo
    "Apreciado cliente, su extracto de cuenta de ahorros correspondiente al mes de octubre esta disponible para consulta. El saldo disponible en su cuenta es de 2340000 pesos. Puede consultar el detalle de sus movimientos y descargar el extracto en formato PDF desde la sucursal virtual. Si detecta alguna inconsistencia en sus movimientos comuniquese con nuestra linea de atencion al cliente.",
    # Aprobación de crédito de libranza
    "Estimado cliente, nos complace informarle que su solicitud de credito de libranza fue aprobada exitosamente. El monto aprobado es de 15000000 pesos con una tasa efectiva anual de 12.5%. La cuota mensual a descontar de su nomina sera de 340000 pesos durante 48 meses. Para formalizar el credito debe presentarse en cualquier oficina con su cedula de ciudadania y ultimo comprobante de pago de nomina.",
    # Pago de seguro de vida - confirmación
    "Apreciado asegurado, confirmamos que el cobro de su seguro de vida y accidentes personales por valor de 45000 pesos fue procesado exitosamente para el mes de noviembre. Su poliza se encuentra vigente hasta el 30 de noviembre. Puede consultar los detalles de su cobertura y beneficiarios desde nuestra aplicacion movil o portal web.",
    # Transferencia completada - banco
    "Estimado cliente, su transferencia a terceros por valor de 500000 pesos dirigida a la cuenta terminada en 3421 fue procesada exitosamente el dia de hoy. El comprobante de la transaccion con numero de referencia 789456123 esta disponible en su sucursal virtual. Guarde este comprobante para sus registros.",
    # Notificación académica SENA
    "Estimado aprendiz, le informamos que su proceso de evaluacion y certificacion de competencias laborales ha sido programado para el proximo lunes 18 de noviembre. Para confirmar su asistencia ingrese al portal SOFIA PLUS con su numero de documento y codigo de ficha. Recuerde presentar su documento de identidad el dia de la evaluacion.",
    # Renovación de tarjeta debito
    "Apreciado cliente, su tarjeta debito vence el proximo mes. Para garantizar la continuidad de sus servicios, su nueva tarjeta sera enviada a la direccion registrada en los proximos 5 dias habiles. Una vez la reciba actívela a traves de nuestro portal, aplicacion movil o llamando a nuestra linea de atencion. No es necesario realizar ningun pago para la renovacion.",
    # Certificado de ingresos disponible
    "Estimado empleado, le informamos que su certificado de ingresos y retenciones correspondiente al ano gravable 2023 ya se encuentra disponible. Puede descargarlo desde el portal de empleados en la seccion de Documentos. Recuerde que este documento es requerido para su declaracion de renta. Para cualquier inquietud comuniquese con el area de nomina.",
    # Aviso de vencimiento de poliza de vehiculo
    "Estimado asegurado, su poliza de seguro todo riesgo para el vehiculo de placa ABC123 vence el 15 de diciembre. Para renovarla comuniquese con su asesor comercial o visite cualquiera de nuestras oficinas. Tambien puede renovar en linea a traves de nuestro portal web. Recuerde que circular sin SOAT vigente genera multas.",
    # Liquidación de prestaciones laborales
    "Estimado ex empleado, adjuntamos la liquidacion final de sus prestaciones sociales correspondiente a su retiro de la empresa. El valor total de su liquidacion es de 8750000 pesos y sera depositado en la cuenta bancaria que tiene registrada en los proximos 3 dias habiles. Ante cualquier inconsistencia comuniquese con el departamento de recursos humanos.",
]

def main() -> None:
    import subprocess

    data_path = ROOT / "data" / "raw" / "dataset.csv"
    df = pd.read_csv(data_path)
    print(f"Dataset actual: {len(df):,} registros")

    new_rows = [{"text": t.strip(), "label": 0} for t in LEGIT_INSTITUTIONAL]
    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df, df_new], ignore_index=True)
    df_combined.drop_duplicates(subset="text", inplace=True)
    df_combined.to_csv(data_path, index=False)

    added = len(df_combined) - len(df)
    print(f"Agregados: {added} correos legítimos institucionales")
    print(f"Dataset nuevo: {len(df_combined):,} registros")

    print("\nReentrenando modelo...")
    result = subprocess.run(
        ["python", str(ROOT / "scripts" / "train_model.py")],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(result.stdout[-2000:])
    if result.returncode != 0:
        print("STDERR:", result.stderr[-1000:])

if __name__ == "__main__":
    main()
