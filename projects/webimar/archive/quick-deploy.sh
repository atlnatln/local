#!/bin/bash
# Webimar Quick Deploy Scripti

echo "🚀 Webimar Quick Deploy Başlatılıyor..."
echo "============================================"

# Çalışma dizinini kontrol et
if [ ! -d ".git" ]; then
    echo "❌ Bu script git repository'si içinde çalıştırılmalıdır!"
    exit 1
fi

# Git durumunu kontrol et
echo "� Git durumu kontrol ediliyor..."
git status --porcelain > /tmp/git_status.txt

if [ ! -s /tmp/git_status.txt ]; then
    echo "✅ Hiç değişiklik yok, deploy gerekli değil."
    exit 0
fi

echo "📝 Değişen dosyalar:"
cat /tmp/git_status.txt
echo ""

# Sadece gerekli dosyaları kontrol et ve filtrele
echo "🔍 Deploy edilmesi gereken dosyalar filtreleniyor..."

# Deploy edilecek dosya uzantıları ve dizinler
DEPLOY_PATTERNS=(
    "*.py"
    "*.js"
    "*.jsx" 
    "*.ts"
    "*.tsx"
    "*.json"
    "*.html"
    "*.css"
    "*.scss"
    "*.md"
    "*.txt"
    "*.yml"
    "*.yaml"
    "*.sh"
    "requirements.txt"
    "package.json"
    "package-lock.json"
    "Dockerfile"
    ".env*"
    "webimar-api/"
    "webimar-react/"
    "webimar-nextjs/"
    ".github/"
)

# Değişen dosyaları kontrol et
DEPLOY_NEEDED=false
while IFS= read -r line; do
    if [ -n "$line" ]; then
        file_path=$(echo "$line" | awk '{print $2}')
        for pattern in "${DEPLOY_PATTERNS[@]}"; do
            if [[ "$file_path" == $pattern ]] || [[ "$file_path" == *"$pattern"* ]]; then
                DEPLOY_NEEDED=true
                echo "✅ Deploy gerekli: $file_path"
                break
            fi
        done
    fi
done < /tmp/git_status.txt

if [ "$DEPLOY_NEEDED" = false ]; then
    echo "ℹ️  Deploy edilmesi gereken dosya değişikliği bulunamadı."
    echo "   (Sadece test dosyaları, cache, log dosyaları vb. değişmiş)"
    exit 0
fi

echo ""
echo "🔄 Deploy işlemi başlatılıyor..."

# Git add - sadece deploy edilecek dosyaları ekle
echo "📝 Değişiklikler git'e ekleniyor..."
for pattern in "${DEPLOY_PATTERNS[@]}"; do
    git add "$pattern" 2>/dev/null || true
done

# Commit mesajı oluştur
COMMIT_MSG="Deploy: $(date '+%Y-%m-%d %H:%M:%S') - "
CHANGED_COUNT=$(git diff --cached --name-only | wc -l)
COMMIT_MSG+="$CHANGED_COUNT dosya güncellendi"

# Commit et
echo "💾 Commit oluşturuluyor: $COMMIT_MSG"
if git commit -m "$COMMIT_MSG"; then
    echo "✅ Commit başarılı"
else
    echo "ℹ️  Commit edilecek değişiklik bulunamadı"
    exit 0
fi

# Push et
echo "⬆️  GitHub'a push ediliyor..."
if git push origin main; then
    echo "✅ Push başarılı!"
else
    echo "❌ Push başarısız!"
    exit 1
fi

# Temizlik
rm -f /tmp/git_status.txt

echo ""
echo "✅ Deploy başarıyla tamamlandı!"
echo "============================================"
echo "📊 GitHub Actions durumunu kontrol et:"
echo "🔗 https://github.com/atlnatln/webimar/actions"
echo ""
echo "🔄 OTOMATİK PIPELINE ÇALIŞACAK:"
echo "   • Django collectstatic"
echo "   • React build"
echo "   • Next.js build & export"
echo "   • Static dosyalar sunucuya kopyalama"
echo "   • Nginx reload"
echo ""
echo "🌐 Deploy tamamlandıktan sonra kontrol et:"
echo "🏠 Next.js: https://tarimimar.com.tr"
echo "⚛️  React SPA: https://tarimimar.com.tr/hesaplama/"
echo "🔧 Django Admin: https://tarimimar.com.tr/admin/"
echo "============================================"
