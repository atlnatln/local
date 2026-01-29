from django.core.management.base import BaseCommand
from apps.batches.models import Batch
from apps.batches.services import BatchProcessor
from apps.accounts.models import Organization
import logging
import os

class Command(BaseCommand):
    help = 'Tests adaptive quadtree search for İzmir city planners'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stage2',
            action='store_true',
            help='Include Stage 2 verification (Pro tier API calls)',
        )
        parser.add_argument(
            '--stage3',
            action='store_true',
            help='Include Stage 3 enrichment (Enterprise tier API calls - requires --stage2)',
        )

    def handle(self, *args, **options):
        include_stage2 = options.get('stage2', False)
        include_stage3 = options.get('stage3', False)
        
        # Validate stage dependencies
        if include_stage3 and not include_stage2:
            self.stdout.write(self.style.ERROR("❌ --stage3 requires --stage2"))
            return
        
        # Create stage info text
        if include_stage3:
            stage_info = "with Stage 2 Verification + Stage 3 Enrichment"
        elif include_stage2:
            stage_info = "with Stage 2 Verification"
        else:
            stage_info = "(Stage 1 Only)"
        
        self.stdout.write(f"🚀 Testing Adaptive Quadtree Search for İzmir Şehir Plancıları {stage_info}")
        
        # Check API key
        api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ GOOGLE_PLACES_API_KEY not found in environment"))
            return
            
        self.stdout.write(f"✅ API Key found: {api_key[:20]}...")
        
        # Ensure Org exists
        org, _ = Organization.objects.get_or_create(name="Test Org")
        
        # Cleanup previous tests
        Batch.objects.filter(city='İzmir', sector='Şehir plancısı').delete()
        
        # Create Batch
        batch = Batch.objects.create(
            organization=org,
            created_by="adaptive_test", 
            city='İzmir',
            sector='Şehir plancısı',
            record_count_estimate=100,  # Higher to trigger potential splitting
            status='CREATED'
        )
        
        self.stdout.write(f"📋 Created Batch ID: {batch.id}")
        
        processor = BatchProcessor(batch.id)
        
        # Configure logging for detailed output
        logger = logging.getLogger('apps.providers.grid_search')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        bs_logger = logging.getLogger('apps.batches.services')
        bs_logger.setLevel(logging.INFO)
        bs_logger.addHandler(handler)

        if include_stage2:
            self.stdout.write("🔍 Starting Adaptive Search + Stage 2 Verification...")
            self.stdout.write("📊 Watch for API call counts, splitting behavior, and verification logic:")
        else:
            self.stdout.write("🔍 Starting Adaptive Search (Stage 1 Only)...")
            self.stdout.write("📊 Watch for API call counts and splitting behavior:")

        try:
            candidates = processor._stage_collect_ids(include_stage2=include_stage2, include_stage3=include_stage3)
            
            self.stdout.write(f"\n🎯 === RESULTS ===")
            self.stdout.write(f"✨ Found {len(candidates)} candidates")
            
            if candidates:
                self.stdout.write(f"📍 Sample results:")
                for i, c in enumerate(candidates[:5], 1):
                    name = c.get('name', 'Unknown')
                    place_id = c.get('id', 'No ID')
                    
                    if include_stage3:
                        # Stage 3 format with contact info
                        address = c.get('address', 'No address')[:50] + "..." if len(c.get('address', '')) > 50 else c.get('address', 'No address')
                        reason = c.get('verification_reason', 'unknown')
                        types_preview = ', '.join(c.get('types', [])[:3])[:30] + "..." if c.get('types') else 'No types'
                        website = c.get('website', 'No website')
                        phone = c.get('phone', 'No phone')
                        self.stdout.write(f"   {i}. ✅ {name}")
                        self.stdout.write(f"      📍 {address}")  
                        self.stdout.write(f"      🏷️  Types: {types_preview}")
                        self.stdout.write(f"      ✔️  Verified by: {reason}")
                        self.stdout.write(f"      🌐 Website: {website}")
                        self.stdout.write(f"      📞 Phone: {phone}")
                        self.stdout.write(f"      🆔 ID: {place_id[:10]}...")
                    elif include_stage2:
                        # Stage 2 format with verification data
                        address = c.get('address', 'No address')[:50] + "..." if len(c.get('address', '')) > 50 else c.get('address', 'No address')
                        reason = c.get('verification_reason', 'unknown')
                        types_preview = ', '.join(c.get('types', [])[:3])[:30] + "..." if c.get('types') else 'No types'
                        self.stdout.write(f"   {i}. ✅ {name}")
                        self.stdout.write(f"      📍 {address}")  
                        self.stdout.write(f"      🏷️  Types: {types_preview}")
                        self.stdout.write(f"      ✔️  Verified by: {reason}")
                        self.stdout.write(f"      🆔 ID: {place_id[:10]}...")
                    else:
                        # Stage 1 format - just IDs
                        self.stdout.write(f"   {i}. {name} (ID: {place_id[:10]}...)")
                        
                if len(candidates) > 5:
                    self.stdout.write(f"   ... and {len(candidates) - 5} more")
            else:
                self.stdout.write("⚠️  No results found")
                
            if include_stage3:
                self.stdout.write(f"\n💡 Stage 3 completed! Check logs for contact enrichment details and full funnel efficiency!")
            elif include_stage2:
                self.stdout.write(f"\n💡 Stage 2 completed! Run with --stage3 to test contact enrichment.")
            else:
                self.stdout.write(f"\n💡 Stage 1 completed! Run with --stage2 to test verification logic.")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            import traceback
            traceback.print_exc()
