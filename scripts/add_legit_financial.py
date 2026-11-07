"""
Agrega documentos financieros legítimos en español al dataset para eliminar
falsos positivos en extractos bancarios, estados de cuenta y notificaciones
de transacciones reales.

Ejecutar desde la raíz del proyecto:
    python scripts/add_legit_financial.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

# ---------------------------------------------------------------------------
# 50 ejemplos de documentos financieros legítimos en español
# Cubren: extractos, confirmaciones, estados de cuenta, notificaciones
# de débito/crédito, renovaciones, certificados, avisos y otros.
# Vocabulario intencionalmente superpuesto con phishing para entrenar
# al modelo a distinguir contexto.
# ---------------------------------------------------------------------------
LEGIT_FINANCIAL: list[str] = [
    # ── EXTRACTOS BANCARIOS ───────────────────────────────────────────────
    "Apreciado cliente, adjuntamos el extracto de su cuenta de ahorros "
    "correspondiente al mes de octubre. La contraseña para abrir el archivo PDF "
    "es su número de documento de identidad. El saldo disponible al cierre del "
    "periodo es de 1.450.320 pesos. Puede consultar sus movimientos en detalle "
    "en nuestra sucursal virtual www.davivienda.com sin ningún costo adicional.",

    "Estimado cliente, su extracto de cuenta corriente del periodo septiembre "
    "está disponible para descarga. Para abrir el documento adjunto ingrese su "
    "número de cédula como contraseña. Movimientos del mes: 12 débitos por "
    "2.340.000 pesos y 5 créditos por 4.100.000 pesos. Saldo final: 1.760.000 "
    "pesos. Consulte cualquier inquietud en la línea 018000 123456.",

    "Su extracto mensual de cuenta de ahorros Davivienda está listo. Periodo: "
    "01 al 31 de octubre de 2026. Saldo inicial: 890.500 pesos. Total débitos: "
    "1.230.000 pesos. Total créditos: 2.100.000 pesos. Saldo final: 1.760.500 "
    "pesos. El extracto en PDF adjunto está protegido con su número de documento.",

    "Apreciado titular, le enviamos el extracto de su cuenta de ahorros número "
    "terminada en 1493. Período octubre 2026. Para visualizar el archivo adjunto "
    "utilice como contraseña su número de cédula de ciudadanía. Recuerde que "
    "también puede consultar sus extractos históricos desde la sucursal virtual "
    "o la aplicación móvil de forma gratuita.",

    "Extracto de Portafolio de Inversiones — periodo octubre 2026. Saldo en "
    "cuenta de ahorros: 2.890.000 pesos. CDT vigente valor nominal: 5.000.000 "
    "pesos, tasa 9.8% EA, vence 15 de febrero 2027. Fondos de inversión: "
    "participación actual valorada en 1.234.500 pesos. Para abrir el PDF adjunto "
    "use su número de documento de identidad como contraseña.",

    # ── CONFIRMACIONES DE TRANSFERENCIA ───────────────────────────────────
    "Confirmación de transferencia exitosa. Fecha: 06/11/2026 14:32. Valor: "
    "350.000 pesos. Cuenta origen: ahorros terminada en 7821. Cuenta destino: "
    "terminada en 3456 Bancolombia. Número de aprobación: 892341. Este "
    "comprobante es válido como soporte de la transacción realizada.",

    "Su transferencia interbancaria fue procesada correctamente. Valor debitado: "
    "1.200.000 pesos. Banco destino: Banco de Bogotá. Nombre beneficiario: Carlos "
    "Martínez. Número de radicado: 20261106-4521. Conserve este número para "
    "cualquier reclamación ante su entidad bancaria.",

    "Pago a terceros registrado. Desde su cuenta de ahorros se debitaron "
    "450.000 pesos con destino a cuenta Nequi terminada en 8834. Hora: 09:15 "
    "am. Referencia: TRF-20261106-7823. Si no reconoce esta transacción "
    "comuníquese de inmediato con la línea de atención.",

    "Transferencia PSE completada. Entidad origen: Davivienda. Entidad destino: "
    "EPM Medellín. Valor: 185.300 pesos. Concepto: pago factura servicios "
    "públicos octubre 2026. Número de transacción: PSE-9823741. Puede descargar "
    "el recibo desde el portal de su banco.",

    "Confirmación de pago de nómina procesado exitosamente. Fecha de acreditación: "
    "30/10/2026. Valor neto acreditado: 2.350.000 pesos en su cuenta de ahorros. "
    "Empleador: Empresa de Comercio S.A.S. Este abono corresponde a su salario "
    "del mes de octubre. Consulte el detalle en su extracto mensual.",

    # ── ESTADOS DE CUENTA TARJETA DE CRÉDITO ──────────────────────────────
    "Estado de cuenta tarjeta de crédito Visa Oro — corte 31 octubre 2026. "
    "Cupo total: 8.000.000 pesos. Cupo disponible: 5.230.400 pesos. Saldo a "
    "pagar: 2.769.600 pesos. Pago mínimo: 138.480 pesos. Fecha límite de pago: "
    "20 de noviembre de 2026. Puede pagar desde su sucursal virtual o en "
    "cualquier corresponsal bancario.",

    "Le informamos que el estado de cuenta de su tarjeta de crédito MasterCard "
    "Black con corte al 31/10/2026 está disponible. Saldo total: 4.120.000 pesos. "
    "Pago mínimo requerido: 206.000 pesos antes del 25 de noviembre. Para evitar "
    "intereses pague el total del saldo. Consulte el detalle de sus compras en "
    "la aplicación móvil.",

    "Estado de cuenta tarjeta de crédito — período octubre 2026. Compras nacionales: "
    "12 transacciones por 1.890.000 pesos. Compras internacionales: 2 transacciones "
    "por 230 USD. Avances en efectivo: 0. Intereses generados: 89.400 pesos. "
    "Saldo total a la fecha de corte: 2.209.400 pesos.",

    # ── NOTIFICACIONES DE DÉBITO / CRÉDITO ────────────────────────────────
    "Débito automático procesado. Concepto: pago cuota crédito hipotecario. "
    "Valor: 1.456.000 pesos. Debitado de su cuenta de ahorros el 05/11/2026. "
    "Número de crédito: HIP-20190034521. Cuotas pagadas: 84 de 180. Capital "
    "pendiente: 98.234.000 pesos.",

    "Notificación de crédito a su cuenta. Valor acreditado: 500.000 pesos. "
    "Concepto: reembolso IVA DIAN periodo julio-agosto 2026. Número radicado DIAN: "
    "REI-2026-003421. El valor fue acreditado automáticamente según lo establecido "
    "en su solicitud de devolución.",

    "Se realizó un débito a su cuenta de ahorros. Concepto: seguro de vida "
    "voluntario. Valor: 32.400 pesos. Fecha: 01/11/2026. Este cobro corresponde "
    "a la prima mensual de su póliza número 2345-VA. Para modificar o cancelar "
    "su seguro comuníquese con el área de seguros.",

    "Crédito a su cuenta corriente. Valor: 12.500.000 pesos. Concepto: desembolso "
    "crédito libre inversión aprobado. Número de operación: CLI-20261105-889. "
    "El plazo del crédito es 36 meses con cuota mensual de 416.667 pesos. "
    "Consulte el plan de pagos completo en su sucursal virtual.",

    "Aviso de débito: su tarjeta de crédito realizó un pago automático desde "
    "su cuenta de ahorros. Valor debitado: 350.000 pesos correspondiente al "
    "pago mínimo de su tarjeta con corte del 31/10/2026. Para aumentar el monto "
    "de pago automático actualice la configuración en su banca en línea.",

    # ── AVISOS DE VENCIMIENTO / RENOVACIÓN ────────────────────────────────
    "Su certificado de depósito a término CDT número 456789 vence el próximo "
    "15 de noviembre de 2026. Capital: 10.000.000 pesos. Intereses generados "
    "en el período: 480.000 pesos. Para renovar o redimir el título ingrese a "
    "su sucursal virtual o comuníquese con su asesor comercial asignado.",

    "Aviso de renovación automática de CDT. Su certificado de depósito a término "
    "fue renovado automáticamente según instrucción registrada. Nuevo capital: "
    "10.480.000 pesos (capital + intereses reinvertidos). Tasa vigente: 9.6% EA. "
    "Nueva fecha de vencimiento: 15 de mayo de 2027.",

    "Le informamos que su tarjeta débito Mastercard terminada en 4821 vence el "
    "próximo mes de diciembre. Su nueva tarjeta le será enviada a la dirección "
    "registrada en nuestros sistemas en los próximos 8 días hábiles. No incurre "
    "en ningún costo. Actívela a través de nuestra aplicación móvil al recibirla.",

    "Recordatorio: su crédito de libre inversión cuenta con 2 cuotas vencidas "
    "por valor de 832.000 pesos. Para ponerse al día puede realizar el pago en "
    "cualquier corresponsal bancario citando su número de crédito CLI-20240023. "
    "También puede refinanciar su deuda comunicándose con su asesor.",

    # ── CERTIFICADOS Y DOCUMENTOS OFICIALES ───────────────────────────────
    "Certificado de existencia de cuenta bancaria. Se certifica que el titular "
    "identificado con cédula de ciudadanía tiene activa una cuenta de ahorros "
    "en esta entidad desde el año 2019. Saldo promedio últimos 3 meses: "
    "1.800.000 pesos. Este certificado tiene validez de 30 días calendario "
    "para trámites ante entidades públicas y privadas.",

    "Certificado de retención en la fuente por rendimientos financieros año "
    "gravable 2025. Titular: identificado con documento de identidad. "
    "Total rendimientos de cuenta de ahorros: 125.400 pesos. Retención "
    "aplicada 4%: 5.016 pesos. Este certificado es válido para su declaración "
    "de renta ante la DIAN.",

    "Su certificado bancario de saldo promedio está disponible para descarga. "
    "Período certificado: enero a octubre 2026. Saldo promedio cuenta corriente: "
    "3.200.000 pesos. Saldo promedio CDT: 10.240.000 pesos. Documento generado "
    "automáticamente desde su sucursal virtual con firma electrónica.",

    # ── CRÉDITOS Y PRÉSTAMOS ───────────────────────────────────────────────
    "Aprobación de crédito hipotecario. Le comunicamos que su solicitud de crédito "
    "hipotecario fue aprobada. Monto aprobado: 180.000.000 pesos. Plazo: 180 meses. "
    "Tasa: UVR + 8.9% EA. Cuota aproximada: 1.890.000 pesos mensuales. Para "
    "continuar con el proceso de escrituración comuníquese con su asesor asignado.",

    "Estado de su crédito de consumo. Número: CON-20230045678. Valor inicial: "
    "15.000.000 pesos. Cuotas pagadas: 24 de 36. Saldo capital pendiente: "
    "5.100.000 pesos. Próxima cuota: 450.000 pesos con vencimiento 15/11/2026. "
    "Puede consultar el plan de pagos completo en la sucursal virtual.",

    "Refinanciación de crédito aprobada. Su solicitud de refinanciación del "
    "crédito libre inversión CLI-20220089 fue aprobada. Nuevo plazo: 24 meses "
    "adicionales. Nueva cuota: 380.000 pesos mensuales. Los cambios se verán "
    "reflejados a partir del próximo ciclo de facturación.",

    "Libranza aprobada. Acuerdo con su empleador para descuento de nómina. "
    "Monto desembolsado: 8.000.000 pesos en su cuenta de ahorros. Cuota "
    "mensual a descontar: 266.667 pesos durante 30 meses. Tasa efectiva anual: "
    "14.2%. El primer descuento aplicará en la nómina del mes siguiente.",

    # ── SEGUROS ────────────────────────────────────────────────────────────
    "Renovación de póliza SOAT procesada. Vehículo placa ABC-123. Vigencia: "
    "06/11/2026 al 05/11/2027. Valor pagado: 345.600 pesos debitados de su "
    "cuenta de ahorros. Número de póliza: SOAT-2026-8834521. Puede descargar "
    "el SOAT digital desde la aplicación móvil de su banco.",

    "Su seguro de desempleo fue activado. Período de cobertura: 6 meses. "
    "El seguro cubre el pago de sus cuotas de crédito durante el tiempo que "
    "permanezca sin empleo. Para tramitar la cobertura presente los documentos "
    "requeridos en cualquier oficina. Número de póliza: SD-20261106-445.",

    "Aviso de cobro seguro de vida. Prima mensual correspondiente a noviembre: "
    "45.800 pesos. Debitada de su cuenta corriente el primer día hábil del mes. "
    "Póliza: VID-20231122-889. Suma asegurada: 100.000.000 pesos. Beneficiarios "
    "registrados: 2 personas. Consulte y actualice sus beneficiarios en la app.",

    # ── INVERSIONES ────────────────────────────────────────────────────────
    "Resumen de portafolio de inversiones — corte 31 octubre 2026. Fondo de "
    "acciones colombianas: 2.340.000 pesos (+3.2% en el mes). Fondo renta fija: "
    "5.100.000 pesos (+0.8% en el mes). CDT: 10.480.000 pesos. Total portafolio "
    "valorado: 17.920.000 pesos. Rentabilidad acumulada año corrido: 7.4%.",

    "Confirmación de compra de acciones. Se ejecutó la orden de compra de 50 "
    "acciones de Ecopetrol a precio promedio de 1.890 pesos por acción. Total "
    "operación: 94.500 pesos más comisión de 1.890 pesos. Debitado de su cuenta "
    "de inversiones el 06/11/2026. Número de operación: BOL-20261106-3341.",

    "Distribución de dividendos acreditada. Concepto: dividendos Bancolombia "
    "tercer trimestre 2026. Valor acreditado en su cuenta de ahorros: 234.800 "
    "pesos correspondiente a su participación accionaria. Número de acciones "
    "en su portafolio: 230 acciones. Fecha de acreditación: 03/11/2026.",

    # ── NEQUI / BANCA DIGITAL ──────────────────────────────────────────────
    "Movimiento en tu cuenta Nequi. Recibiste 150.000 pesos de número celular "
    "terminado en 4521. Concepto: pago arriendo noviembre. Saldo actual: "
    "487.300 pesos. ¿No reconoces este movimiento? Contáctanos desde la app "
    "en Ayuda y soporte.",

    "Enviaste dinero con Nequi. Valor: 80.000 pesos a número celular terminado "
    "en 7823. Concepto: regalo cumpleaños. Saldo disponible después de la "
    "transacción: 234.100 pesos. Si tienes dudas sobre esta transferencia "
    "repórtala directamente desde tu app Nequi.",

    "Tu recarga Nequi fue exitosa. Valor recargado: 500.000 pesos desde tu "
    "cuenta de ahorros Bancolombia. Saldo Nequi disponible: 523.400 pesos. "
    "Hora de la operación: 11:42 am. Referencia de recarga: REC-20261106-7721.",

    # ── CORRESPONSALES / CAJEROS ───────────────────────────────────────────
    "Retiro exitoso en cajero automático. Fecha: 06/11/2026 10:23 am. Valor: "
    "200.000 pesos. Cajero: Red Servibanca oficina Centro. Saldo disponible "
    "después del retiro: 1.230.400 pesos. Si no reconoce este retiro bloquee "
    "su tarjeta desde la aplicación móvil o llame a la línea de fraudes.",

    "Pago en corresponsal bancario registrado. Concepto: pago factura Claro "
    "móvil. Valor: 45.300 pesos. Fecha: 05/11/2026. Corresponsal: Droguería "
    "San Marcos. Número de transacción: COR-20261105-5521. Guarde este "
    "comprobante como soporte de su pago.",

    # ── NOTIFICACIONES DE SEGURIDAD LEGÍTIMAS ─────────────────────────────
    "Cambio de contraseña registrado. Su contraseña de acceso a la sucursal "
    "virtual fue actualizada el 06/11/2026 a las 09:14 am desde dispositivo "
    "registrado. Si no realizó este cambio comuníquese de inmediato con la "
    "línea de fraudes 018000 123456. No compartamos su contraseña con nadie.",

    "Nuevo dispositivo registrado en su cuenta. Se registró acceso desde un "
    "dispositivo nuevo el 06/11/2026. Sistema operativo: Android 14. Si fue "
    "usted ignore este mensaje. Si no reconoce este acceso ingrese a su "
    "sucursal virtual y cierre sesión en todos los dispositivos.",

    "Alerta de seguridad: su cuenta fue accedida desde una dirección IP no "
    "habitual correspondiente a la ciudad de Bogotá el 05/11/2026 a las 7:30 pm. "
    "Si fue usted no requiere hacer nada. Para mayor seguridad active la "
    "autenticación de doble factor desde la configuración de su cuenta.",

    "Bloqueo preventivo de tarjeta débito. Por su seguridad bloqueamos "
    "temporalmente su tarjeta ante 3 intentos fallidos de PIN en cajero automático. "
    "Para desbloquearla ingrese a la sucursal virtual, visítenos en oficina o "
    "llame a la línea de atención con su documento de identidad.",

    # ── SERVICIOS PÚBLICOS Y PAGOS ─────────────────────────────────────────
    "Confirmación de pago de servicios públicos. Empresa: EPM. Contrato: "
    "1234567. Valor pagado: 198.400 pesos. Fecha de pago: 06/11/2026. "
    "Medio de pago: débito desde cuenta de ahorros. Número de aprobación: "
    "PAG-20261106-9934. Su factura queda saldada hasta la próxima facturación.",

    "Pago de impuesto predial registrado. Predio: matrícula inmobiliaria 123-45678. "
    "Municipio: Medellín. Vigencia 2026. Valor pagado: 1.234.000 pesos. "
    "Descuento por pronto pago aplicado: 10%. Valor sin descuento: 1.371.111 "
    "pesos. Número de liquidación: PRE-2026-456789.",

    "Su obligación de impuesto de vehículos fue pagada. Placa ABC-123. "
    "Departamento: Antioquia. Vigencia 2026. Valor cancelado: 456.800 pesos "
    "incluyendo descuento por pronto pago. Número de recibo: VEH-2026-234561. "
    "Puede descargar el paz y salvo desde el portal de la Gobernación.",

    # ── PENSIONES Y CESANTÍAS ─────────────────────────────────────────────
    "Confirmación de consignación de cesantías. Empleador: Empresa S.A.S. "
    "Período: enero a diciembre 2025. Valor consignado: 2.100.000 pesos. "
    "Fondo receptor: Porvenir. Fecha de acreditación: 14/02/2026. Puede "
    "consultar el detalle de su saldo en la aplicación de su fondo de cesantías.",

    "Extracto de cuenta individual de ahorro pensional CIAP — tercer trimestre "
    "2026. Saldo acumulado: 45.234.000 pesos. Aportes del trimestre: empleado "
    "346.500 pesos, empleador 519.750 pesos. Rentabilidad del trimestre: 1.8%. "
    "Consulte la proyección de su pensión en el portal del fondo.",

    # ── CONFIRMACIONES GENERALES ───────────────────────────────────────────
    "Vinculación completada. Su proceso de apertura de cuenta de ahorros "
    "digital fue completado exitosamente. Número de cuenta asignado: terminado "
    "en 7823. Tarjeta débito en camino a su dirección registrada. Puede usar "
    "la cuenta de inmediato desde la aplicación móvil para transferencias y pagos.",

    "Desafiliación de débito automático procesada. Se canceló el cobro "
    "automático del servicio de streaming a su tarjeta de crédito. El cambio "
    "aplica a partir del próximo ciclo de facturación. Si realizó esta "
    "solicitud por error puede reactivarla desde la sucursal virtual.",
]


def main() -> None:
    import subprocess

    data_path = ROOT / "data" / "raw" / "dataset.csv"
    df = pd.read_csv(data_path)
    n_before = len(df)
    print(f"Dataset antes: {n_before:,} registros")
    print(f"  Legítimos: {(df['label']==0).sum():,}")
    print(f"  Phishing:  {(df['label']==1).sum():,}")

    new_rows = pd.DataFrame([
        {"text": t.strip(), "label": 0}
        for t in LEGIT_FINANCIAL
    ])
    df_combined = pd.concat([df, new_rows], ignore_index=True)
    df_combined.drop_duplicates(subset="text", inplace=True)
    df_combined.to_csv(data_path, index=False)

    n_after = len(df_combined)
    added = n_after - n_before
    print(f"\nAgregados: {added} ejemplos financieros legítimos")
    print(f"Dataset nuevo: {n_after:,} registros")
    print(f"  Legítimos: {(df_combined['label']==0).sum():,}")
    print(f"  Phishing:  {(df_combined['label']==1).sum():,}")

    print("\nReentrenando modelo...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "train_model.py")],
        capture_output=False, text=True, cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("El entrenamiento falló.")
    else:
        print("\n[OK] Listo. Reinicia la API para cargar el nuevo modelo.")


if __name__ == "__main__":
    main()
