import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.accounts.models import Organization
from apps.batches.models import Batch, BatchItem
from apps.batches.services import BatchProcessor


class Command(BaseCommand):
    help = "Run planner batch demo and export max-N rows to CSV"

    def add_arguments(self, parser):
        parser.add_argument("--city", required=True, help="Şehir adı (örn: Muğla)")
        parser.add_argument("--sector", required=True, help="Sektör/meslek (örn: Şehir plancısı)")
        parser.add_argument("--limit", type=int, default=10, help="Maks kayıt sayısı")
        parser.add_argument(
            "--output",
            default="artifacts/demo/planner_demo.csv",
            help="CSV çıktı yolu (services/backend'e göre relatif veya mutlak)",
        )

    def handle(self, *args, **options):
        city = options["city"].strip()
        sector = options["sector"].strip()
        limit = max(1, min(int(options["limit"]), 10))

        output_path = Path(options["output"])
        if not output_path.is_absolute():
            output_path = (Path(__file__).resolve().parents[5] / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        org_slug = slugify("anka-demo-org")
        org, _ = Organization.objects.get_or_create(
            slug=org_slug,
            defaults={
                "name": "Anka Demo Organization",
                "email": "demo-org@ankadata.local",
                "country": "TR",
                "city": city,
                "is_active": True,
            },
        )

        batch = Batch.objects.create(
            organization=org,
            created_by="demo-script",
            city=city,
            sector=sector,
            filters={},
            record_count_estimate=limit,
            sort_rule_version=1,
        )

        self.stdout.write(self.style.NOTICE(f"Batch oluşturuldu: {batch.id}"))

        processor = BatchProcessor(batch.id)
        processor.run_pipeline()

        batch.refresh_from_db()
        items = list(BatchItem.objects.filter(batch=batch, is_verified=True).order_by("created_at")[:limit])

        fieldnames = [
            "name",
            "formatted_address",
            "website",
            "national_phone",
            "place_id",
            "batch_id",
        ]

        with output_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow(
                    {
                        "name": item.firm_name or "",
                        "formatted_address": item.data.get("formattedAddress", "") or "",
                        "website": item.data.get("websiteUri", "") or "",
                        "national_phone": item.data.get("nationalPhoneNumber", "") or "",
                        "place_id": item.firm_id,
                        "batch_id": str(batch.id),
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"CSV üretildi: {output_path}"))
        self.stdout.write(
            self.style.SUCCESS(
                f"Durum={batch.status} collected={batch.ids_collected} verified={batch.ids_verified} enriched={batch.contacts_enriched} exported={len(items)}"
            )
        )
