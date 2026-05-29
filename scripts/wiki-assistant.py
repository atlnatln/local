#!/usr/bin/env python3
"""
Wiki Asistanı — LSP-Style Token Optimizasyon için yardımcı program.
Kimi'nin dosya karıştırma/okuma yükünü alır, ona sadece "context paketi" sunar.

Kullanım:
    python3 wiki-assistant.py --prepare [--project <isim>]
    python3 wiki-assistant.py --apply <kiminin-karar.json>
"""

import argparse
import json
import os
import re
import subprocess
import sys

LOCAL_ROOT = "/home/akn/local"
WIKI_ROOT = os.path.join(LOCAL_ROOT, "wiki")
WIKI_ASSISTANT_INDEX = os.path.join(WIKI_ROOT, ".assistant-index.json")

# ---------------------------------------------------------------------------
# Cache / Index Mekanizması (L2 Cache benzeri)
# ---------------------------------------------------------------------------
# Wiki sayfalarının başlık yapısını (headings) cache'ler.
# Sonraki çalıştırmalarda değişmemiş sayfalar için dosyayı baştan açmaz.
# ---------------------------------------------------------------------------

def load_cache():
    """Cache dosyasını oku. Yoksa boş dict döndür."""
    if os.path.exists(WIKI_ASSISTANT_INDEX):
        try:
            with open(WIKI_ASSISTANT_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(cache):
    """Cache dosyasını atomik olarak yaz."""
    tmp_path = WIKI_ASSISTANT_INDEX + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, WIKI_ASSISTANT_INDEX)
    except Exception as e:
        sys.stderr.write(f"Cache yazma hatası: {e}\n")


def get_file_mtime(path):
    """Dosyanın değişiklik zamanını (mtime) int olarak döndür."""
    try:
        return int(os.path.getmtime(path))
    except Exception:
        return 0


def parse_headings_from_file(full_path):
    """Bir markdown dosyasındaki tüm başlıkları parse et."""
    headings = []
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                m = re.match(r"^(#{1,4})\s+(.+)", line)
                if m:
                    headings.append({
                        "level": len(m.group(1)),
                        "title": m.group(2).strip(),
                        "line": i + 1,
                    })
    except Exception:
        pass
    return headings


def get_cached_headings(wiki_path):
    """
    Wiki dosyasının başlık listesini getir.
    Cache'te var ve güncelse cache'ten, yoksa dosyadan parse edip cache'e yazar.
    """
    full_path = os.path.join(LOCAL_ROOT, wiki_path)
    if not os.path.exists(full_path):
        return []

    cache = load_cache()
    current_mtime = get_file_mtime(full_path)
    cache_key = wiki_path

    # Cache kontrolü
    if cache_key in cache:
        entry = cache[cache_key]
        if entry.get("mtime") == current_mtime and "headings" in entry:
            return entry["headings"]

    # Cache miss → dosyadan parse et
    headings = parse_headings_from_file(full_path)

    # Cache'e kaydet
    cache[cache_key] = {
        "mtime": current_mtime,
        "headings": headings,
    }
    save_cache(cache)
    return headings


# Proje yapılandırması
PROJECTS = {
    "ops-bot": {
        "dir": "ops-bot",
        "wiki": "wiki/projects/ops-bot.md",
        "checkpoint": "wiki/.checkpoints/ops-bot.sha",
        "git_root": "ops-bot",
    },
    "webimar": {
        "dir": "projects/webimar",
        "wiki": "wiki/projects/webimar.md",
        "checkpoint": "wiki/.checkpoints/webimar.sha",
        "git_root": "projects/webimar",
    },
    "anka": {
        "dir": "projects/anka",
        "wiki": "wiki/projects/anka.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
    "mathlock-play": {
        "dir": "projects/mathlock-play",
        "wiki": "wiki/projects/mathlock-play.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
    "telegram-kimi": {
        "dir": "projects/telegram-kimi",
        "wiki": "wiki/projects/telegram-kimi.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
    "sayi-yolculugu": {
        "dir": "projects/sayi-yolculugu",
        "wiki": "wiki/projects/sayi-yolculugu.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
    "infrastructure": {
        "dir": "infrastructure",
        "wiki": "wiki/projects/infrastructure.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
}

# Dosya → Wiki hedefi eşleme kuralları (WORKFLOW.md Adım 4'ten)
FILE_TO_WIKI_RULES = [
    # (dosya pattern, wiki sayfası, bölüm ipucu)
    (r"^AGENTS\.md$", "wiki/concepts/agents-md.md", "AGENTS.md"),
    (r"^README\.md$", "wiki/projects/local.md", "README"),
    (r"^deploy\.sh$", None, "Deployment"),
    (r"^infrastructure/", "wiki/projects/infrastructure.md", "Altyapı"),
    (r"^scripts/hooks/", "wiki/projects/local.md", "Hook"),
    (r"^scripts/", "wiki/projects/local.md", "Script"),
]


def run_cmd(cmd, cwd=LOCAL_ROOT):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"CMD ERROR: {' '.join(cmd)}\n{result.stderr}\n")
    return result.stdout, result.returncode


def get_checkpoint_sha(project):
    cfg = PROJECTS[project]
    cp_path = os.path.join(LOCAL_ROOT, cfg["checkpoint"])
    if not os.path.exists(cp_path):
        return None
    with open(cp_path) as f:
        return f.read().strip()


def git_diff_committed(project):
    """Checkpoint'ten HEAD'e kadar commit'lenmiş değişiklikler."""
    cfg = PROJECTS[project]
    sha = get_checkpoint_sha(project)
    if not sha:
        return ""
    git_root = os.path.join(LOCAL_ROOT, cfg["git_root"])
    target = cfg["dir"] if cfg["git_root"] == "." else "."
    stdout, _ = run_cmd(["git", "diff", "--name-status", f"{sha}..HEAD", "--", target], cwd=git_root)
    return stdout


def git_diff_workdir(project):
    """HEAD'ten sonraki working directory + staged değişiklikler."""
    cfg = PROJECTS[project]
    git_root = os.path.join(LOCAL_ROOT, cfg["git_root"])
    target = cfg["dir"] if cfg["git_root"] == "." else "."
    stdout, _ = run_cmd(["git", "diff", "--name-status", "HEAD", "--", target], cwd=git_root)
    return stdout


def parse_diff(name_status_output):
    """git --name-status çıktısını parse et."""
    files = []
    for line in name_status_output.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R"):
            # Rename: R100\told\tnew
            old_path = parts[1]
            new_path = parts[2]
            files.append({"status": "R", "old_path": old_path, "path": new_path})
        else:
            path = parts[1]
            files.append({"status": status, "path": path})
    return files


def map_to_wiki(project, rel_path):
    """Bir dosya yolunu ilgili wiki sayfasına ve bölüm ipucuna eşle."""
    # Önce genel kurallar
    for pattern, wiki_page, section_hint in FILE_TO_WIKI_RULES:
        if re.search(pattern, rel_path):
            if wiki_page is None:
                # Projenin kendi wiki sayfasına yönlendir
                wiki_page = PROJECTS[project]["wiki"]
            return wiki_page, section_hint

    # Proje alt dizinleri → projenin wiki sayfası
    if rel_path.startswith(PROJECTS[project]["dir"]):
        return PROJECTS[project]["wiki"], guess_section_from_path(rel_path)

    # Bilinmeyen → local wiki
    return "wiki/projects/local.md", "Genel"


def guess_section_from_path(path):
    """Dosya yolundan wiki bölümü tahmini."""
    lowered = path.lower()
    if ".js" in lowered:
        return "JavaScript"
    if ".py" in lowered:
        return "Python"
    if ".html" in lowered:
        return "HTML"
    if ".css" in lowered:
        return "CSS"
    if ".sh" in lowered:
        return "Shell"
    if "docker" in lowered or "compose" in lowered:
        return "Docker"
    if "nginx" in lowered:
        return "Nginx"
    if "test" in lowered:
        return "Test"
    if "deploy" in lowered:
        return "Deployment"
    if "hook" in lowered:
        return "Hook"
    return "Kod"


def extract_snippets(rel_path, max_lines=40):
    """
    Bir dosyadan 'snippet' çıkar.
    MVP'de: Dosyanın tamamını değil, başlık/fonksiyon düzeyinde özet sun.
    Eğer dosya çok kısaysa tamamını, uzunsa sadece yapısını.
    """
    full_path = os.path.join(LOCAL_ROOT, rel_path)
    if not os.path.exists(full_path):
        return None

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}

    total_lines = len(lines)
    if total_lines == 0:
        return None

    # Çok kısa dosya → tamamını sun
    if total_lines <= max_lines:
        return {
            "type": "full",
            "line_count": total_lines,
            "content": "".join(lines),
        }

    # Uzun dosya → yapısal özet (fonksiyonlar, sınıflar, başlıklar)
    structure = []
    for i, line in enumerate(lines):
        # Fonksiyon tanımları
        if re.match(r"^\s*(def|function|async\s+def)\s+\w+", line):
            structure.append({"type": "function", "line": i + 1, "signature": line.strip()})
        # Sınıf tanımları
        elif re.match(r"^\s*(class)\s+\w+", line):
            structure.append({"type": "class", "line": i + 1, "signature": line.strip()})
        # Markdown başlıkları
        elif re.match(r"^#{1,4}\s+", line):
            structure.append({"type": "heading", "line": i + 1, "signature": line.strip()})
        # HTML script/style blokları
        elif re.match(r"^\s*<(script|style|section|div)\b", line, re.I):
            structure.append({"type": "block", "line": i + 1, "signature": line.strip()[:80]})

    # Ayrıca dosyanın başından biraz bağlam sun
    header = "".join(lines[:min(15, total_lines)])

    return {
        "type": "structure",
        "line_count": total_lines,
        "header": header,
        "structure": structure[:20],  # en fazla 20 yapı öğesi
    }


def extract_wiki_sections(wiki_path, section_hints):
    """
    Wiki sayfasından ilgili bölümleri çıkar.
    section_hints: aranacak bölüm anahtar kelimeleri listesi

    OPTIMIZASYON: Önce cache'teki headings listesini kontrol eder.
    Hiç section eşleşmezse dosyayı açmaz, sadece outline döndürür.
    """
    full_path = os.path.join(LOCAL_ROOT, wiki_path)
    if not os.path.exists(full_path):
        return None

    # 1. Headings'i cache'ten al (dosyayı açmadan)
    headings = get_cached_headings(wiki_path)
    if not headings:
        return None

    # 2. İlgili başlıkları bul (keyword eşleme)
    matched_titles = []
    for hint in section_hints:
        hint_lower = hint.lower()
        for h in headings:
            title_lower = h["title"].lower()
            if hint_lower in title_lower or title_lower in hint_lower:
                matched_titles.append(h)

    # 3. Hiç eşleşme yoksa → dosyayı açmaya gerek yok, outline döndür
    if not matched_titles:
        return {
            "type": "outline",
            "headings": [{"title": h["title"], "level": h["level"], "line": h["line"]} for h in headings],
        }

    # 4. Eşleşme varsa → dosyayı aç, section içeriğini çıkar
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # İlgili başlıkları bul (keyword eşleme)
    matched_sections = {}
    for hint in section_hints:
        hint_lower = hint.lower()
        for h in headings:
            title_lower = h["title"].lower()
            if hint_lower in title_lower or title_lower in hint_lower:
                # Başlık ve alt bölümlerini çıkar
                start_idx = h["line"] - 1
                end_idx = len(lines)
                # Sonraki aynı seviye veya üst seviye başlığı bul
                for next_h in headings:
                    if next_h["line"] > h["line"] and next_h["level"] <= h["level"]:
                        end_idx = next_h["line"] - 1
                        break
                section_content = "".join(lines[start_idx:end_idx])
                # Çok uzun bölümleri kısalt (~1500 karakter)
                if len(section_content) > 1500:
                    section_content = section_content[:1500] + "\n\n... [bölüm devam ediyor, toplam " + str(len(section_content)) + " karakter] ..."
                matched_sections[h["title"]] = {
                    "level": h["level"],
                    "start_line": h["line"],
                    "end_line": end_idx,
                    "content": section_content,
                }

    return {"type": "sections", "matched": matched_sections}


def locate_symbol(file_path, symbol_name, pretty=False):
    """LSP üzerinden sembol konumunu bul."""
    full_path = os.path.join(LOCAL_ROOT, file_path)
    if not os.path.exists(full_path):
        full_path = file_path
    if not os.path.exists(full_path):
        return {"error": f"Dosya bulunamadı: {file_path}"}

    ext = os.path.splitext(full_path)[1].lower()
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
    }
    language = lang_map.get(ext, "python")

    # Proje kökünü tahmin et — sunucu başlatma hızı için daralt
    project_root = LOCAL_ROOT
    rel = os.path.relpath(full_path, LOCAL_ROOT)
    parts = rel.split(os.sep)
    if parts[0] == "ops-bot":
        project_root = os.path.join(LOCAL_ROOT, "ops-bot")
    elif parts[0] == "projects" and len(parts) >= 2:
        project_root = os.path.join(LOCAL_ROOT, "projects", parts[1])

    lsp_client_path = os.path.join(LOCAL_ROOT, "scripts", "lsp-client.py")
    cmd = [
        sys.executable, lsp_client_path,
        "--language", language,
        "--file", full_path,
        "--symbol", symbol_name,
        "--project-root", project_root,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        try:
            return json.loads(err)
        except Exception:
            return {"error": f"LSP client hatası: {err}"}

    try:
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": f"LSP çıktısı parse edilemedi: {e}", "raw": result.stdout}


def prepare_project(project):
    """Bir proje için context paketi hazırla."""
    cfg = PROJECTS[project]

    # Committed diff + working directory diff
    committed = git_diff_committed(project)
    workdir = git_diff_workdir(project)

    files_committed = parse_diff(committed)
    files_workdir = parse_diff(workdir)

    # Birleştir: aynı dosya varsa working directory öncelikli
    all_files = {}
    for f in files_committed:
        all_files[f["path"]] = f
    for f in files_workdir:
        all_files[f["path"]] = f

    if not all_files:
        return None

    # Her dosya için detay
    changed_files = []
    wiki_targets_map = {}  # wiki_path -> {section_hints, files}

    for path, info in all_files.items():
        rel_path = path
        wiki_page, section_hint = map_to_wiki(project, rel_path)

        file_entry = {
            "path": rel_path,
            "status": info["status"],
            "snippets": extract_snippets(rel_path),
        }
        if info["status"] == "R":
            file_entry["old_path"] = info.get("old_path", "")

        changed_files.append(file_entry)

        # Wiki hedeflerini topla
        if wiki_page not in wiki_targets_map:
            wiki_targets_map[wiki_page] = {"section_hints": set(), "files": []}
        wiki_targets_map[wiki_page]["section_hints"].add(section_hint)
        wiki_targets_map[wiki_page]["files"].append(rel_path)

    # Wiki hedeflerinden ilgili bölümleri çıkar
    wiki_targets = []
    for wiki_page, data in wiki_targets_map.items():
        sections = extract_wiki_sections(wiki_page, list(data["section_hints"]))
        wiki_targets.append({
            "page": wiki_page,
            "relevant_sections": list(data["section_hints"]),
            "source_files": data["files"],
            "sections": sections,
        })

    return {
        "project": project,
        "diff_summary": {
            "added": sum(1 for f in all_files.values() if f["status"] == "A"),
            "modified": sum(1 for f in all_files.values() if f["status"] == "M"),
            "deleted": sum(1 for f in all_files.values() if f["status"] == "D"),
            "renamed": sum(1 for f in all_files.values() if f["status"] == "R"),
        },
        "changed_files": changed_files,
        "wiki_targets": wiki_targets,
        "index_needs_update": True,
        "log_needs_update": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Wiki Asistanı")
    parser.add_argument("--prepare", action="store_true", help="Context paketi hazırla")
    parser.add_argument("--project", help="Belirli bir proje (tümü için boş bırak)")
    parser.add_argument("--apply", help="Kimi'nin karar JSON'unu uygula (gelecek)")
    parser.add_argument("--pretty", action="store_true", help="JSON'u formatlı yaz")
    parser.add_argument("--locate", action="store_true", help="Kod sembolü konumlandır (LSP)")
    parser.add_argument("--file", help="Hedef dosya yolu (--locate için)")
    parser.add_argument("--symbol", help="Aranacak sembol adı (--locate için)")
    args = parser.parse_args()

    if args.locate:
        if not args.file or not args.symbol:
            print(json.dumps({"error": "--locate için --file ve --symbol zorunlu"}), file=sys.stderr)
            sys.exit(1)
        result = locate_symbol(args.file, args.symbol, pretty=args.pretty)
        if "error" in result:
            print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
    elif args.prepare:
        if args.project:
            if args.project not in PROJECTS:
                print(json.dumps({"error": f"Bilinmeyen proje: {args.project}"}), file=sys.stderr)
                sys.exit(1)
            result = prepare_project(args.project)
            if result is None:
                result = {"project": args.project, "diff_summary": {}, "changed_files": [], "wiki_targets": [], "index_needs_update": False, "log_needs_update": False}
            print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
        else:
            # Tüm projeler
            all_results = []
            for project in PROJECTS:
                result = prepare_project(project)
                if result:
                    all_results.append(result)
            if not all_results:
                print(json.dumps({"results": [], "message": "Hiç değişiklik yok"}, indent=2 if args.pretty else None, ensure_ascii=False))
            else:
                print(json.dumps({"results": all_results}, indent=2 if args.pretty else None, ensure_ascii=False))
    elif args.apply:
        print(json.dumps({"error": "apply modu henüz implemente edilmedi"}), file=sys.stderr)
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
