from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Cuerpo del correo sospechoso")
    subject: str = Field(default="", description="Asunto del correo")
    sender: str = Field(default="", description="Dirección del remitente")


class FeatureWeight(BaseModel):
    word: str
    weight: float


class ExplainabilityData(BaseModel):
    top_phishing_features: list[FeatureWeight]
    urgency_keywords_found: list[str]
    social_engineering_score: float
    summary: str


class URLRiskData(BaseModel):
    url: str
    uses_http: bool
    is_ip_based: bool
    is_shortener: bool
    suspicious_keywords: list[str]
    brand_spoofing: list[str]
    suspicious_tld: bool
    excessive_subdomains: bool
    risk_score: float
    risk_level: str


class URLAnalysisData(BaseModel):
    urls: list[URLRiskData]
    total_urls: int
    high_risk_urls: int
    url_risk_score: float


class DecisionFactors(BaseModel):
    ml_confidence: float
    hybrid_triggered: bool
    data_harvesting_triggered: bool
    xai_social_score: float
    urgency_count: int
    url_count: int
    url_risk_score: float


class AnalyzeResponse(BaseModel):
    label: str
    risk_level: str
    confidence: float
    probabilities: dict[str, float]
    explainability: ExplainabilityData
    url_analysis: URLAnalysisData
    decision_factors: DecisionFactors
    urls_found: list[str]
    domain_mismatch: bool
    response_time_ms: float


class HistoryRecord(BaseModel):
    id: int
    analyzed_at: str
    sender: str | None
    subject: str | None
    label: str
    risk_level: str
    confidence: float
    snippet: str | None
    urls_found: str | None
    domain_mismatch: int | None
    response_time_ms: float | None


class HistoryListResponse(BaseModel):
    total: int
    records: list[HistoryRecord]


class ClearHistoryResponse(BaseModel):
    deleted: bool


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
