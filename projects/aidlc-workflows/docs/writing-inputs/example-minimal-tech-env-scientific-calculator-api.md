# Teknik Ortam: CalcEngine

## Dil ve Paket Yöneticisi

- **Python 3.12+**
- **uv** tüm paket yönetimi için (pip, poetry veya conda yok)
- `pyproject.toml` tüm proje ve araç yapılandırması için
- `uv.lock` Git'e işlenmiş

## Web Çerçevesi

- **FastAPI**, istek/yanıt doğrulaması için Pydantic v2 ile
- **Mangum**, FastAPI'yi AWS Lambda üzerinde çalıştırmak için

## Bulut ve Dağıtım

- **AWS**, tek hesap, `us-east-1`
- **Sunucusuz**: API Gateway (HTTP API tipi) arkasında Lambda
- **DynamoDB** API anahtarı depolama ve kullanım ölçümü için
- **S3 + CloudFront** dokümantasyon sitesi için
- **AWS CDK (Python)** tüm altyapı için -- elle konsol değişikliği yok

## Test

- **pytest**, pytest-cov ile (minimum %90 satır kapsamı)
- **hypothesis**, özellik tabanlı matematik doğruluk testi için
- **mypy** katı mod, tip kontrolü için
- **ruff** lint ve formatlama için
- **moto** testlerde AWS servislerini taklit etmek için

## Kullanılmayacaklar

| Yasaklanan                      | Neden                                            | Bunun Yerine Kullan                 |
| ------------------------------- | ------------------------------------------------- | ----------------------------------- |
| `eval()`, `exec()`, `compile()` | Güvenlik -- keyfi kod yürütme                    | AST tabanlı ifade ayrıştırıcı       |
| Flask, Django                   | Proje FastAPI kullanıyor                         | FastAPI                             |
| requests                        | Asenkron olay döngüsünü engeller                 | httpx                               |
| sympy                           | MVP için çok ağır                                | Özel ifade ayrıştırıcı              |
| pandas                          | Gerekmiyor -- tek hesaplamalar, dataframe değil | Standart Python                     |
| pip, poetry, pipenv             | Proje özel olarak uv kullanıyor                  | uv                                  |
| black, flake8, isort            | ruff tarafından değiştirildi                     | ruff                                |
| AWS EC2, ECS, RDS               | MVP için sunucusuz model tercih ediliyor         | Lambda, DynamoDB                    |

## Güvenlik Temelleri

- `Authorization: Bearer {key}` başlığıyla API anahtarı kimlik doğrulaması
- Anahtarlar DynamoDB'de bcrypt hash'leri olarak saklanır, düz metin olarak asla loglanmaz
- İfade ayrıştırıcı karakter izin listesi ve AST değerlendirmesi kullanır -- dinamik kod yürütme yok
- İfade uzunluğu 4.096 karakterle sınırlandırılmış, iç içe geçme derinliği 100 seviye ile sınırlandırılmış
- TLS 1.2+ zorunlu, HTTP uç noktaları yok
- Sırlar AWS Secrets Manager'da, ortam değişkenlerinde veya kodda değil

## Örnek Kod Kalıbı

Bir uç nokta şu yapıyı takip etmelidir:

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from calcengine.api.middleware.auth import get_api_key_id
from calcengine.api.models.errors import error_response
from calcengine.api.models.responses import CalculationResponse
from calcengine.engine.errors import CalcEngineError
from calcengine.engine.trigonometry import sin

router = APIRouter()


class SinRequest(BaseModel):
    value: float
    angle_mode: str = Field(default="radians", pattern="^(radians|degrees)$")


@router.post("/v1/trigonometry/sin", response_model=CalculationResponse)
async def calculate_sin(
    request: SinRequest,
    api_key_id: str = Depends(get_api_key_id),
) -> CalculationResponse | dict:
    try:
        result = sin(request.value, angle_mode=request.angle_mode)
        return CalculationResponse(result=result, expression=f"sin({request.value})")
    except CalcEngineError as e:
        return error_response(e)
```

Bir matematik fonksiyonu şu yapıyı takip etmelidir:

```python
import math

from calcengine.engine.errors import DomainError


def log_base(value: float, base: float = 10.0) -> float:
    """Verilen tabanda değerin logaritmasını hesaplar. Geçersiz girdi için DomainError yükseltir."""
    if value <= 0:
        raise DomainError(
            code="DOMAIN_ERROR",
            message=f"{value} logaritması hesaplanamaz",
            detail="Logaritma yalnızca pozitif sayılar için tanımlıdır",
        )
    if base <= 0 or base == 1.0:
        raise DomainError(
            code="DOMAIN_ERROR",
            message=f"Geçersiz logaritma tabanı: {base}",
            detail="Taban pozitif ve 1'e eşit olmamalıdır",
        )
    return math.log(value) / math.log(base)
```

Bir test şu yapıyı takip etmelidir:

```python
import math
import pytest
from hypothesis import given, strategies as st
from calcengine.engine.errors import DomainError
from calcengine.engine.logarithmic import log_base


def test_log10_of_100() -> None:
    assert log_base(100, 10) == pytest.approx(2.0)


def test_log_of_negative_raises_domain_error() -> None:
    with pytest.raises(DomainError):
        log_base(-5)


@given(st.floats(min_value=1e-300, max_value=1e300, allow_nan=False, allow_infinity=False))
def test_log10_matches_stdlib(x: float) -> None:
    assert log_base(x, 10) == pytest.approx(math.log10(x), rel=1e-14)
```
