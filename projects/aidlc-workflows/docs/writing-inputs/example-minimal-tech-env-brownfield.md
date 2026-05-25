# Teknik Ortam: İade ve Geri Ödeme Modülü — OrderFlow Platformu

> **Brownfield projesi.** Mevcut yığın temel çizgidir. Yeni kod kurulan kalıplara
> uymalıdır. Aşağıda listelenmeyen bir seçim için, mevcut kod tabanını takip edin --
> gerekçe olmadan yeni kalıplar tanıtmayın.

---

## Mevcut Yığın (korunmalı)

| Katman              | Mevcut Teknoloji  | Sürüm   | Notlar                                                                |
| ------------------ | ------------------- | --------- | -------------------------------------------------------------------- |
| Dil           | TypeScript          | 5.x       | Katı mod. JavaScript dosyaları tanıtmayın.                      |
| Çalışma Zamanı            | Node.js             | 20.x LTS  |                                                                      |
| API çerçevesi      | Express             | 4.x       | Mevcut tüm servisler Express kullanır. Fastify veya Koa tanıtmayın.  |
| Veritabanı           | PostgreSQL          | 15        | pg ve node-postgres aracılığıyla. ORM yok -- yazılı sorgu yardımcılarıyla ham SQL. |
| Altyapı     | AWS ECS Fargate     | —         | Servisler Docker konteynerleri olarak dağıtılır. Tüm altyapı için CDK.             |
| Mesaj veri yolu        | Amazon SQS          | —         | Asenkron e-posta gönderimi için notification-service tarafından kullanılır.               |
| Kimlik Doğrulama               | AWS Cognito         | —         | JWT token'ları API Gateway'de doğrulanır. Yeni bir kimlik doğrulama katmanı inşa etmeyin.  |
| Paket yöneticisi    | npm                 | 10.x      | yarn veya pnpm tanıtmayın.                                       |
| Test çerçevesi     | Jest                | 29.x      | ts-jest ile. Tüm testler kaynak yanında `__tests__/` içinde.            |
| Linter / formatlayıcı | ESLint + Prettier   | —         | Yapılandırma dosyaları repo kökündedir. Bunları değiştirmeyin.               |

---

## Ne Eklenecek (bu modül için yeni)

- `order-service` ile aynı yapıyı takip eden yeni bir `returns-service`
- Yeni PostgreSQL tabloları: `return_requests`, `return_items`, `return_status_history`
- Müşteri iade formu ve operasyon panosu için yeni React bileşenleri
- Bu eklemeler mevcut tabloları veya servis sözleşmelerini değiştirmemelidir

---

## Değişmeden Kalması Gerekenler

- `order-service`, `payment-service`, `notification-service` -- bu servisleri değiştirmeyin
- Mevcut PostgreSQL tabloları -- yalnızca ekleme migrasyonları (yeni tablolar, yeni tablolarda yeni sütunlar)
- `notification-service` API sözleşmesi -- dokümante edildiği gibi çağrın, genişletmeyin
- Mevcut CDK yığınları -- `returns-service` için yeni bir yığın ekleyin, mevcut yığınları düzenlemeyin
- Ön uç tasarım sistemi bileşenleri -- mevcut bileşenleri kullanın, yerine kendi oluşturduklarınızı kullanmayın

---

## Ne Kaldırılacak / Tanıtılmayacak

| Yasaklanan                          | Neden                                                                                       | Bunun Yerine Kullan                                                                 |
| ----------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| ORM'ler (TypeORM, Prisma, Sequelize)   | Mevcut kod tabanı yazılı sorgu yardımcılarıyla ham SQL kullanır. ORM tanıtmak tutarsızlık yaratır. | Mevcut kalıpla eşleşen yazılı sorgu fonksiyonlarıyla node-postgres         |
| Axios                               | Proje yerel get kullanır (Node 20 yerleşik).                                                | fetch                                                                       |
| Herhangi bir yeni CSS çerçevesi               | Mevcut ön uç Tailwind CSS kullanır.                                                         | Tailwind CSS, mevcut tasarım sistemi bileşenleri                             |
| Yeni durum yönetim kütüphanesi        | Mevcut ön uç React Context + useReducer kullanır.                                           | React Context + useReducer                                                  |
| Yeni test çalıştırıcı (Vitest, Mocha)     | Proje boyunca Jest kullanılır.                                                                | Jest                                                                        |
| Ayrı kimlik doğrulama servisi veya ara yazılım | Kimlik doğrulama API Gateway'de Cognito JWT aracılığıyla yapılır.                                              | Authorization başlığında iletilen JWT'yi diğer servisler gibi doğrulayın |

---

## Güvenlik Temelleri

- Kimlik Doğrulama: Cognito JWT API Gateway'de doğrulanır. Servisler `x-user-id` ve `x-user-role` başlıklarını alır -- bunlara güvenin, serviste JWT'yi yeniden doğrulamayın
- Yetkilendirme: Operasyon panosu uç noktaları `role === 'operations'` gerektirir -- bu başlığı kontrol edin
- Girdi doğrulama: İşlemeden önce tüm istek gövdelerini Zod şemalarıyla doğrulayın
- KVKK: İade talepleri müşteri adlarını ve adreslerini içerir -- bu alanları loglamayın
- Sırlar: Mevcut servislerle aynı şekilde AWS Secrets Manager aracılığıyla veritabanı kimlik bilgileri ve servis URL'leri

---

## Örnek Kod Kalıpları

Mevcut kod tabanından bu kalıpları takip edin. Alternatifler icat etmeyin.

**Bir servis uç noktası (Express yönlendirici işleyici):**

```typescript
import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { createReturnRequest } from '../domain/returns';
import { AppError } from '../errors';

const router = Router();

const CreateReturnSchema = z.object({
  orderId: z.string().uuid(),
  items: z.array(z.object({ orderItemId: z.string().uuid(), reason: z.string().min(1) })).min(1),
});

router.post('/returns', async (req: Request, res: Response) => {
  const parsed = CreateReturnSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: 'VALIDATION_ERROR', details: parsed.error.flatten() });
  }
  try {
    const result = await createReturnRequest(parsed.data, req.headers['x-user-id'] as string);
    return res.status(201).json(result);
  } catch (err) {
    if (err instanceof AppError) {
      return res.status(err.statusCode).json({ error: err.code, message: err.message });
    }
    throw err;
  }
});

export default router;
```

**Bir veritabanı sorgu fonksiyonu:**

```typescript
import { pool } from '../db/pool';

export interface ReturnRequest {
  id: string;
  orderId: string;
  customerId: string;
  status: 'submitted' | 'approved' | 'rejected' | 'refunded';
  createdAt: Date;
}

export async function getReturnRequestById(id: string): Promise<ReturnRequest | null> {
  const { rows } = await pool.query<ReturnRequest>(
    'SELECT id, order_id AS "orderId", customer_id AS "customerId", status, created_at AS "createdAt" FROM return_requests WHERE id = $1',
    [id]
  );
  return rows[0] ?? null;
}
```

**Bir Jest testi:**

```typescript
import { getReturnRequestById } from '../db/return-requests';
import { pool } from '../db/pool';

jest.mock('../db/pool');
const mockQuery = pool.query as jest.Mock;

describe('getReturnRequestById', () => {
  it('bulunduğunda talebi döndürür', async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ id: 'abc', orderId: '123', status: 'submitted' }] });
    const result = await getReturnRequestById('abc');
    expect(result?.id).toBe('abc');
  });

  it('bulunamadığında null döndürür', async () => {
    mockQuery.mockResolvedValueOnce({ rows: [] });
    const result = await getReturnRequestById('missing');
    expect(result).toBeNull();
  });
});
```
