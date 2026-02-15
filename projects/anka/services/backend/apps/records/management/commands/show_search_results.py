from django.core.management.base import BaseCommand
from apps.records.models import SearchQuery, BusinessCandidate, EnrichmentLog
from apps.records.services import GoogleMapsResultsManager
import json

class Command(BaseCommand):
    help = 'Shows saved search results from database with industry-standard recording system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--search-id',
            type=int,
            help='Show specific search query by ID',
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='Show latest completed search',
        )
        parser.add_argument(
            '--export-csv',
            action='store_true',
            help='Export results to CSV',
        )

    def handle(self, *args, **options):
        search_id = options.get('search_id')
        show_latest = options.get('latest', False)
        export_csv = options.get('export_csv', False)
        
        if search_id:
            try:
                search_query = SearchQuery.objects.get(id=search_id)
            except SearchQuery.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Search query with ID {search_id} not found"))
                return
        elif show_latest:
            search_query = SearchQuery.objects.filter(status='completed').order_by('-completed_at').first()
            if not search_query:
                self.stdout.write(self.style.ERROR("❌ No completed search queries found"))
                return
        else:
            # Show all search queries
            self.show_all_queries()
            return
            
        self.show_search_details(search_query, export_csv)
    
    def show_all_queries(self):
        self.stdout.write("🔍 All Search Queries:")
        self.stdout.write("=" * 50)
        
        queries = SearchQuery.objects.all().order_by('-created_at')
        
        if not queries.exists():
            self.stdout.write("⚠️  No search queries found")
            return
            
        for query in queries:
            status_icon = "✅" if query.status == 'completed' else "❌" if query.status == 'failed' else "🔄"
            self.stdout.write(f"{status_icon} ID: {query.id} | {query.query_text} ({query.city})")
            self.stdout.write(f"   📅 {query.created_at.strftime('%Y-%m-%d %H:%M')} | 👤 {query.created_by}")
            self.stdout.write(f"   📊 Stage: {query.max_stage} | Candidates: {query.total_candidates_found} | Cost: ${query.cost_estimate}")
            self.stdout.write(f"   🏢 Org: {query.organization.name if query.organization else 'None'}")
            self.stdout.write("")
            
        self.stdout.write(f"💡 Use --search-id <ID> to view details or --latest for most recent")
    
    def show_search_details(self, search_query, export_csv=False):
        self.stdout.write(f"🔍 Search Query Details (ID: {search_query.id})")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Query: {search_query.query_text}")
        self.stdout.write(f"City: {search_query.city}")
        self.stdout.write(f"Sector: {search_query.sector}")
        self.stdout.write(f"Created by: {search_query.created_by}")
        self.stdout.write(f"Organization: {search_query.organization.name if search_query.organization else 'None'}")
        self.stdout.write(f"Max Stage: {search_query.max_stage}")
        self.stdout.write(f"Status: {search_query.status}")
        self.stdout.write(f"Created: {search_query.created_at}")
        if search_query.started_at:
            self.stdout.write(f"Started: {search_query.started_at}")
        if search_query.completed_at:
            self.stdout.write(f"Completed: {search_query.completed_at}")
        self.stdout.write(f"Total Candidates: {search_query.total_candidates_found}")
        self.stdout.write(f"Cost Estimate: ${search_query.cost_estimate}")
        
        # API Calls breakdown
        try:
            api_calls = json.loads(search_query.api_calls_made) if search_query.api_calls_made else {}
            if api_calls:
                self.stdout.write(f"API Calls: {api_calls}")
        except json.JSONDecodeError:
            pass
            
        # Show candidates
        candidates = BusinessCandidate.objects.filter(search_query=search_query).order_by('created_at')
        
        if candidates.exists():
            self.stdout.write(f"\n📍 Business Candidates ({candidates.count()}):")
            self.stdout.write("-" * 50)
            
            for i, candidate in enumerate(candidates, 1):
                self.stdout.write(f"   {i}. ✅ {candidate.name}")
                self.stdout.write(f"      📍 {candidate.formatted_address}")
                
                # Parse types
                try:
                    types = json.loads(candidate.place_types) if candidate.place_types else []
                    types_preview = ', '.join(types[:3])[:30] + "..." if len(types) > 3 else ', '.join(types)
                    self.stdout.write(f"      🏷️  Types: {types_preview}")
                except json.JSONDecodeError:
                    pass
                    
                self.stdout.write(f"      ✔️  Verified by: {candidate.verification_reason}")
                self.stdout.write(f"      ⭐ Rating: {candidate.rating} ({candidate.user_ratings_total} reviews)")
                
                if candidate.website:
                    self.stdout.write(f"      🌐 Website: {candidate.website}")
                if candidate.phone_number:
                    self.stdout.write(f"      📞 Phone: {candidate.phone_number}")
                if candidate.enhanced_email:
                    self.stdout.write(f"      📧 Email: {candidate.enhanced_email}")
                    
                # Social media links
                try:
                    social_links = json.loads(candidate.social_media_links) if candidate.social_media_links else []
                    if social_links:
                        self.stdout.write(f"      🔗 Social: {', '.join(social_links)}")
                except json.JSONDecodeError:
                    pass
                    
                self.stdout.write(f"      🆔 Place ID: {candidate.place_id[:15]}...")
                self.stdout.write(f"      📊 Stage: Collected at {candidate.collected_at_stage}, Enriched to {candidate.last_enriched_stage}")
                self.stdout.write("")
        else:
            self.stdout.write("⚠️  No candidates found")
        
        # Export to CSV if requested
        if export_csv and candidates.exists():
            manager = GoogleMapsResultsManager(search_query.created_by)
            csv_file = manager.export_to_csv(search_query)
            self.stdout.write(f"\n📁 Results exported to: {csv_file}")
        
        # Show enrichment logs if any
        enrichment_logs = EnrichmentLog.objects.filter(candidate__search_query=search_query)
        if enrichment_logs.exists():
            self.stdout.write(f"\n🔧 Enrichment Logs ({enrichment_logs.count()}):")
            self.stdout.write("-" * 30)
            for log in enrichment_logs:
                success_icon = "✅" if log.success else "❌"
                self.stdout.write(f"   {success_icon} {log.enrichment_type} via {log.source_api}")
                self.stdout.write(f"      📞 Calls: {log.api_calls_used} | 💰 Cost: ${log.cost_estimate}")
                if log.confidence_score:
                    self.stdout.write(f"      📊 Confidence: {log.confidence_score}")
                if log.notes:
                    self.stdout.write(f"      📝 Notes: {log.notes}")
                self.stdout.write("")
        
        self.stdout.write(f"\n💡 Sektör standardında kayıt işlemi tamamlandı!")
        if search_query.max_stage == 'stage3':
            self.stdout.write(f"🎯 Stage 3 ile tam enrichment yapıldı - web sitesi olmayanları Google Search ile bulup tamamlayabiliriz!")