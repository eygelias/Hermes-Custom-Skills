# Venezuelan Exchange Rate APIs

Free APIs, no auth needed. Useful for building Venezuelan finance apps.

## ve.dolarapi.com — BCV + Parallel rates

```
GET https://ve.dolarapi.com/v1/dolares
```

Response (JSON array):
```json
[
  {"moneda":"USD","fuente":"oficial","nombre":"Dólar","promedio":652.9726,"fechaActualizacion":"2026-07-03T00:00:00-04:00"},
  {"moneda":"USD","fuente":"paralelo","nombre":"Paralelo","promedio":737.9125,"fechaActualizacion":"2026-07-03T21:01:08.073Z"}
]
```

- `fuente="oficial"` → BCV official rate
- `fuente="paralelo"` → parallel market rate
- `promedio` field is the rate in Bs per USD

## BCV website — Euro rate (scraping)

```
GET https://www.bcv.org.ve
```

Parse Euro from HTML:
```kotlin
val euroSection = html.substringAfter("id=\"euro\"", "")
val match = Regex("""strong-tb">\\s*([\\d,]+)""").find(euroSection)
val euroRate = match?.groupValues?.get(1)?.replace(",", ".")?.toDoubleOrNull()
```

BCV also has USD, CNY, TRY, RUB rates in the same format.

## Binance P2P — USDT/VES rate

```
POST https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search
Content-Type: application/json

{"fiat":"VES","tradeType":"BUY","asset":"USDT","payTypes":[],"page":1,"rows":5}
```

Response: `data[].adv.price` (string, in Bs per USDT). Average the top results for a stable rate.

**Note:** `tradeType` values are `BUY` (you buy USDT) and `SELL` (you sell USDT). Prices differ slightly.

## Promedio (Average)

Average = (BCV + Parallel) / 2. Some apps include Binance in the average too.

## cotizave.com — Paid consolidated API

Requires API key (`X-API-Key` header). Free tier: 1,500 calls/month.
Endpoint: `GET https://api.cotizave.com/v1/fx/rates`
