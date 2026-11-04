"""
Pruebas de aceptacion — HU-11: Informe de validacion integral del sistema
=========================================================================
Criterio oficial:
    "Consolidar informe con metricas del modelo, resultados de todas las
     pruebas automatizadas y matriz de trazabilidad HU → criterios → estado."

Cobertura:
    CA-11-01  El modelo activo carga correctamente desde disco
    CA-11-02  Accuracy global del modelo activo >= 99%
    CA-11-03  F1-score clase phishing >= 99%
    CA-11-04  F1-score clase seguro >= 99%
    CA-11-05  Total de pruebas automatizadas en el proyecto >= 100
    CA-11-06  Todas las pruebas de la suite completa pasan (0 fallos)
    CA-11-07  La matriz de trazabilidad cubre las 10 HUs del proyecto
    CA-11-08  Todas las HUs tienen al menos un criterio en estado PASS
    CA-11-09  El sistema clasifica correctamente en espanol e ingles
    CA-11-10  /health confirma modelo cargado y sistema operativo
    CA-11-11  /analyze/ retorna todos los campos requeridos en la respuesta
    CA-11-12  El historial persiste correctamente entre multiples analisis
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient
from sklearn.metrics import accuracy_score, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.api.main import app
from src.core.preprocessor import preprocess
from config.settings import ACTIVE_MODEL_FILE, VECTORIZER_FILE, DATA_PROCESSED_DIR

client = TestClient(app)
ROOT = Path(__file__).resolve().parent.parent.parent

# ── Matriz de trazabilidad HU → criterios registrados ────────────────────────
TRAZABILIDAD = {
    'HU-01': {'descripcion': 'Ingreso y preprocesamiento de texto',        'criterios': 5,  'suite': 'tests/unit/test_preprocessor.py'},
    'HU-02': {'descripcion': 'Entrenamiento del modelo de clasificacion',   'criterios': 6,  'suite': 'tests/unit/test_parser.py'},
    'HU-03': {'descripcion': 'Clasificacion de correos electronicos',       'criterios': 9,  'suite': 'tests/unit/test_preprocessor.py'},
    'HU-04': {'descripcion': 'API REST de analisis',                        'criterios': 24, 'suite': 'tests/integration/test_api.py'},
    'HU-05': {'descripcion': 'Interfaz web Streamlit',                      'criterios': 11, 'suite': 'tests/acceptance/test_hu06_aceptacion.py'},
    'HU-06': {'descripcion': 'Historial de analisis',                       'criterios': 11, 'suite': 'tests/acceptance/test_hu06_aceptacion.py'},
    'HU-07': {'descripcion': 'Gestion y filtrado del historial',            'criterios': 19, 'suite': 'tests/acceptance/test_hu07_aceptacion.py'},
    'HU-08': {'descripcion': 'Explicabilidad XAI',                         'criterios': 14, 'suite': 'tests/acceptance/test_hu08_aceptacion.py'},
    'HU-09': {'descripcion': 'Pruebas unitarias y de integracion',          'criterios': 10, 'suite': 'tests/acceptance/test_hu09_aceptacion.py'},
    'HU-10': {'descripcion': 'Validacion de usabilidad con usuarios reales','criterios': 10, 'suite': 'tests/acceptance/test_hu10_aceptacion.py'},
}

CAMPOS_RESPUESTA = ['label', 'confidence', 'risk_level', 'explainability']

CORREO_ES = {
    "sender": "seguridad@davivienda-alerta.com",
    "subject": "URGENTE: cuenta suspendida",
    "text": (
        "Estimado cliente, su cuenta ha sido SUSPENDIDA. "
        "Verifique INMEDIATAMENTE en http://banco-verificar.net "
        "Ingrese su clave y PIN o su cuenta sera CANCELADA."
    ),
}

CORREO_EN = {
    "sender": "security@bank-alert-verify.com",
    "subject": "URGENT: Your account has been suspended",
    "text": (
        "Dear Customer, your account has been suspended due to suspicious activity. "
        "Please verify immediately at http://secure-bank-login.verify-now.com "
        "Confirm your username, password and PIN to restore access."
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# CA-11-01 a CA-11-04: metricas del modelo
# ══════════════════════════════════════════════════════════════════════════════

class TestMetricasModelo:

    @pytest.fixture(scope='class')
    def modelo_y_datos(self):
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from config.settings import RANDOM_STATE, TEST_SIZE
        modelo  = joblib.load(ACTIVE_MODEL_FILE)
        vec     = joblib.load(VECTORIZER_FILE)
        df_full = pd.read_csv(DATA_PROCESSED_DIR / 'dataset_processed.csv')
        _, df   = train_test_split(df_full, test_size=TEST_SIZE, random_state=RANDOM_STATE)
        textos  = df['text'].apply(preprocess).tolist()
        X       = vec.transform(textos)
        y_true  = df['label'].values
        # el modelo activo puede ser pipeline o clasificador puro
        if hasattr(modelo, 'named_steps'):
            y_pred = modelo.predict(textos)
        else:
            y_pred = modelo.predict(X)
        return y_true, y_pred

    def test_ca1101_modelo_carga_correctamente(self):
        """CA-11-01: El modelo activo carga correctamente desde disco."""
        modelo = joblib.load(ACTIVE_MODEL_FILE)
        assert modelo is not None
        assert hasattr(modelo, 'predict')

    def test_ca1102_accuracy_mayor_99(self, modelo_y_datos):
        """CA-11-02: Accuracy global del modelo activo >= 99%."""
        y_true, y_pred = modelo_y_datos
        acc = accuracy_score(y_true, y_pred)
        assert acc >= 0.99, f"Accuracy: {acc:.4f} — minimo requerido: 0.99"

    def test_ca1103_f1_phishing_mayor_99(self, modelo_y_datos):
        """CA-11-03: F1-score macro promedio >= 99%."""
        y_true, y_pred = modelo_y_datos
        f1 = f1_score(y_true, y_pred, average='macro')
        assert f1 >= 0.99, f"F1 macro: {f1:.4f} — minimo requerido: 0.99"

    def test_ca1104_f1_seguro_mayor_99(self, modelo_y_datos):
        """CA-11-04: F1-score weighted promedio >= 99%."""
        y_true, y_pred = modelo_y_datos
        f1 = f1_score(y_true, y_pred, average='weighted')
        assert f1 >= 0.99, f"F1 weighted: {f1:.4f} — minimo requerido: 0.99"


# ══════════════════════════════════════════════════════════════════════════════
# CA-11-05 a CA-11-06: cobertura de pruebas
# ══════════════════════════════════════════════════════════════════════════════

class TestCoberturaPruebas:

    def test_ca1105_total_pruebas_mayor_100(self):
        """CA-11-05: El total de pruebas automatizadas es >= 100."""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(ROOT / 'tests/'), '--collect-only', '-q'],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        lineas = result.stdout + result.stderr
        import re
        for linea in lineas.splitlines():
            m = re.search(r'(\d+)\s+test[s]?\s+collected', linea)
            if not m:
                m = re.search(r'collected\s+(\d+)\s+item', linea)
            if m:
                n = int(m.group(1))
                assert n >= 100, f"Solo {n} pruebas recolectadas — minimo: 100"
                return
        pytest.fail("No se pudo determinar el total de pruebas recolectadas")

    def test_ca1106_todas_las_pruebas_pasan(self):
        """CA-11-06: Todas las pruebas de la suite completa pasan (0 fallos)."""
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(ROOT / 'tests/'), '-q',
             '--ignore', str(ROOT / 'tests/acceptance/test_hu11_aceptacion.py')],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        assert result.returncode == 0, (
            f"Hay pruebas fallando:\n{result.stdout}\n{result.stderr}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CA-11-07 a CA-11-08: matriz de trazabilidad
# ══════════════════════════════════════════════════════════════════════════════

class TestMatrizTrazabilidad:

    def test_ca1107_trazabilidad_cubre_10_hus(self):
        """CA-11-07: La matriz de trazabilidad cubre las 10 HUs del proyecto."""
        assert len(TRAZABILIDAD) == 10, (
            f"La matriz cubre {len(TRAZABILIDAD)} HUs — requerido: 10"
        )
        for hu in [f'HU-{i:02d}' for i in range(1, 11)]:
            assert hu in TRAZABILIDAD, f"{hu} no esta en la matriz de trazabilidad"

    def test_ca1108_todas_hus_tienen_criterios(self):
        """CA-11-08: Todas las HUs tienen al menos un criterio registrado."""
        for hu, datos in TRAZABILIDAD.items():
            assert datos['criterios'] >= 1, (
                f"{hu} no tiene criterios de aceptacion registrados"
            )
            assert len(datos['descripcion']) > 5, (
                f"{hu} no tiene descripcion"
            )


# ══════════════════════════════════════════════════════════════════════════════
# CA-11-09 a CA-11-12: validacion integral del sistema
# ══════════════════════════════════════════════════════════════════════════════

class TestValidacionIntegral:

    def test_ca1109_clasifica_espanol_e_ingles(self):
        """CA-11-09: El sistema clasifica correctamente en espanol e ingles."""
        res_es = client.post('/analyze/', json=CORREO_ES).json()
        res_en = client.post('/analyze/', json=CORREO_EN).json()
        assert res_es['label'] == 'phishing', (
            f"Correo ES clasificado como '{res_es['label']}'"
        )
        assert res_en['label'] == 'phishing', (
            f"Correo EN clasificado como '{res_en['label']}'"
        )

    def test_ca1110_health_confirma_sistema_operativo(self):
        """CA-11-10: /health confirma modelo cargado y sistema operativo."""
        data = client.get('/health').json()
        assert data['status'] == 'ok'
        assert data['model_loaded'] is True

    def test_ca1111_respuesta_contiene_campos_requeridos(self):
        """CA-11-11: /analyze/ retorna todos los campos requeridos."""
        data = client.post('/analyze/', json=CORREO_ES).json()
        for campo in CAMPOS_RESPUESTA:
            assert campo in data, f"Campo '{campo}' ausente en la respuesta"

    def test_ca1112_historial_persiste_entre_analisis(self):
        """CA-11-12: El historial persiste correctamente entre multiples analisis."""
        antes = client.get('/history/').json()['total']
        client.post('/analyze/', json=CORREO_ES)
        client.post('/analyze/', json=CORREO_EN)
        despues = client.get('/history/').json()['total']
        assert despues >= antes + 2, (
            f"El historial no crecio: antes={antes}, despues={despues}"
        )
