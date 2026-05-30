#!/usr/bin/env python3
"""
Wiki Asistani — LSP-Style Token Optimizasyon icin yardimci program.
Kimi'nin dosya kesfi/okuma yukunu alir, ona sadece "context paketi" sunar.

Kullanim:
    python3 wiki-assistant.py --prepare [--project <isim>]
    python3 wiki-assistant.py --locate --file <dosya> --symbol <isim>
    python3 wiki-assistant.py --query "<konu>"
    python3 wiki-assistant.py --sor "<konu>"
    python3 wiki-assistant.py --apply <kiminin-karar.json>
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

LOCAL_ROOT = "/home/akn/local"
WIKI_ROOT = os.path.join(LOCAL_ROOT, "wiki")
WIKI_ASSISTANT_INDEX = os.path.join(WIKI_ROOT, ".assistant-index.json")

# ---------------------------------------------------------------------------
# Cache / Index Mekanizmasi (L2 Cache benzeri)
# ---------------------------------------------------------------------------
# Wiki sayfalarinin baslik yapisini (headings) cache'ler.
# Sonraki calistirmalarda degismemis sayfalar icin dosyayi bastan acmaz.
# ---------------------------------------------------------------------------

def load_cache():
    """Cache dosyasini oku. Yoksa bos dict dondur."""
    if os.path.exists(WIKI_ASSISTANT_INDEX):
        try:
            with open(WIKI_ASSISTANT_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(cache):
    """Cache dosyasini atomik olarak yaz."""
    tmp_path = WIKI_ASSISTANT_INDEX + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, WIKI_ASSISTANT_INDEX)
    except Exception as e:
        sys.stderr.write(f"Cache yazma hatasi: {e}\n")


def get_file_mtime(path):
    """Dosyanin degisiklik zamanini (mtime) int olarak dondur."""
    try:
        return int(os.path.getmtime(path))
    except Exception:
        return 0


def parse_headings_from_file(full_path):
    """Bir markdown dosyasindaki tum basliklari parse et."""
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
    Wiki dosyasinin baslik listesini getir.
    Cache'te var ve guncelse cache'ten, yoksa dosyadan parse edip cache'e yazar.
    """
    full_path = os.path.join(LOCAL_ROOT, wiki_path)
    if not os.path.exists(full_path):
        return []

    cache = load_cache()
    current_mtime = get_file_mtime(full_path)
    cache_key = wiki_path

    # Cache kontrolu
    if cache_key in cache:
        entry = cache[cache_key]
        if entry.get("mtime") == current_mtime and "headings" in entry:
            return entry["headings"]

    # Cache miss -> dosyadan parse et
    headings = parse_headings_from_file(full_path)

    # Cache'e kaydet
    cache[cache_key] = {
        "mtime": current_mtime,
        "headings": headings,
    }
    save_cache(cache)
    return headings


# Proje yapilandirmasi
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
    "ace": {
        "dir": "wiki/ace",
        "wiki": "wiki/ace/playbook.md",
        "checkpoint": "wiki/.checkpoints/local.sha",
        "git_root": ".",
    },
}

# Dosya -> Wiki hedefi esleme kurallari (WORKFLOW.md Adim 4'ten)
FILE_TO_WIKI_RULES = [
    # (dosya pattern, wiki sayfasi, bolum ipucu)
    (r"^AGENTS\.md$", "wiki/concepts/agents-md.md", "AGENTS.md"),
    (r"^README\.md$", "wiki/projects/local.md", "README"),
    (r"^deploy\.sh$", None, "Deployment"),
    (r"^infrastructure/", "wiki/projects/infrastructure.md", "Altyapi"),
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
    """Checkpoint'ten HEAD'e kadar commit'lenmis degisiklikler."""
    cfg = PROJECTS[project]
    sha = get_checkpoint_sha(project)
    if not sha:
        return ""
    git_root = os.path.join(LOCAL_ROOT, cfg["git_root"])
    target = cfg["dir"] if cfg["git_root"] == "." else "."
    stdout, _ = run_cmd(["git", "diff", "--name-status", f"{sha}..HEAD", "--", target], cwd=git_root)
    return stdout


def git_diff_workdir(project):
    """HEAD'ten sonraki working directory + staged degisiklikler."""
    cfg = PROJECTS[project]
    git_root = os.path.join(LOCAL_ROOT, cfg["git_root"])
    target = cfg["dir"] if cfg["git_root"] == "." else "."
    stdout, _ = run_cmd(["git", "diff", "--name-status", "HEAD", "--", target], cwd=git_root)
    return stdout


def parse_diff(name_status_output):
    """git --name-status ciktisini parse et."""
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
    """Bir dosya yolunu ilgili wiki sayfasina ve bolum ipucuna esle."""
    # ACE playbook dosyalari -> kendi wiki sayfalari
    if rel_path.startswith("wiki/ace/") and rel_path.endswith(".md"):
        return rel_path, "ACE Playbook"

    # Once genel kurallar
    for pattern, wiki_page, section_hint in FILE_TO_WIKI_RULES:
        if re.search(pattern, rel_path):
            if wiki_page is None:
                # Projenin kendi wiki sayfasina yonlendir
                wiki_page = PROJECTS[project]["wiki"]
            return wiki_page, section_hint

    # Proje alt dizinleri -> projenin wiki sayfasi
    if rel_path.startswith(PROJECTS[project]["dir"]):
        return PROJECTS[project]["wiki"], guess_section_from_path(rel_path)

    # Bilinmeyen -> local wiki
    return "wiki/projects/local.md", "Genel"


def guess_section_from_path(path):
    """Dosya yolundan wiki bolumu tahmini."""
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
    Bir dosyadan 'snippet' cikar.
    Uzun dosyalarda: Tamamini degil, baslik/fonksiyon duzeyinde ozet sun.
    Eger dosya cok kisaysa tamamini, uzunsa sadece yapisini.
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

    # Cok kisa dosya -> tamamini sun
    if total_lines <= max_lines:
        return {
            "type": "full",
            "line_count": total_lines,
            "content": "".join(lines),
        }

    # Uzun dosya -> yapisal ozet (fonksiyonlar, siniflar, basliklar)
    structure = []
    for i, line in enumerate(lines):
        # Fonksiyon tanimlari
        if re.match(r"^\s*(def|function|async\s+def)\s+\w+", line):
            structure.append({"type": "function", "line": i + 1, "signature": line.strip()})
        # Sinif tanimlari
        elif re.match(r"^\s*(class)\s+\w+", line):
            structure.append({"type": "class", "line": i + 1, "signature": line.strip()})
        # Markdown basliklari
        elif re.match(r"^#{1,4}\s+", line):
            structure.append({"type": "heading", "line": i + 1, "signature": line.strip()})
        # HTML script/style bloklari
        elif re.match(r"^\s*<(script|style|section|div)\b", line, re.I):
            structure.append({"type": "block", "line": i + 1, "signature": line.strip()[:80]})

    # Ayrica dosyanin basindan biraz baglam sun
    header = "".join(lines[:min(15, total_lines)])

    return {
        "type": "structure",
        "line_count": total_lines,
        "header": header,
        "structure": structure[:20],  # en fazla 20 yapi ogesi
    }


def extract_wiki_sections(wiki_path, section_hints):
    """
    Wiki sayfasindan ilgili bolumleri cikar.
    section_hints: aranacak bolum anahtar kelimeleri listesi

    OPTIMIZASYON: Once cache'teki headings listesini kontrol eder.
    Hic section eslesmezse dosyayi acmaz, sadece outline dondurur.
    """
    full_path = os.path.join(LOCAL_ROOT, wiki_path)
    if not os.path.exists(full_path):
        return None

    # 1. Headings'i cache'ten al (dosyayi acmadan)
    headings = get_cached_headings(wiki_path)
    if not headings:
        return None

    # 2. Ilgili basliklari bul (keyword esleme)
    matched_titles = []
    for hint in section_hints:
        hint_lower = hint.lower()
        for h in headings:
            title_lower = h["title"].lower()
            if hint_lower in title_lower or title_lower in hint_lower:
                matched_titles.append(h)

    # 3. Hic eslesme yoksa -> dosyayi acmaya gerek yok, outline dondur
    if not matched_titles:
        return {
            "type": "outline",
            "headings": [{"title": h["title"], "level": h["level"], "line": h["line"]} for h in headings],
        }

    # 4. Eslesme varsa -> dosyayi ac, section icerigini cikar
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Ilgili basliklari bul (keyword esleme)
    matched_sections = {}
    for hint in section_hints:
        hint_lower = hint.lower()
        for h in headings:
            title_lower = h["title"].lower()
            if hint_lower in title_lower or title_lower in hint_lower:
                # Baslik ve alt bolumlerini cikar
                start_idx = h["line"] - 1
                end_idx = len(lines)
                # Sonraki ayni seviye veya ust seviye basligini bul
                for next_h in headings:
                    if next_h["line"] > h["line"] and next_h["level"] <= h["level"]:
                        end_idx = next_h["line"] - 1
                        break
                section_content = "".join(lines[start_idx:end_idx])
                # Cok uzun bolumleri kisalt (~1500 karakter)
                if len(section_content) > 1500:
                    section_content = section_content[:1500] + "\n\n... [bolum devam ediyor, toplam " + str(len(section_content)) + " karakter] ..."
                matched_sections[h["title"]] = {
                    "level": h["level"],
                    "start_line": h["line"],
                    "end_line": end_idx,
                    "content": section_content,
                }

    return {"type": "sections", "matched": matched_sections}


# ---------------------------------------------------------------------------
# Yapilandirma / XML / JSON dosyalari icin basit sembol arama (LSP fallback)
# ---------------------------------------------------------------------------

GREP_LIKE_EXTS = {".xml", ".json", ".yaml", ".yml", ".sh", ".gradle", ".kts", ".properties", ".conf", ".toml"}


def locate_in_file(file_path, symbol_name):
    """
    Bir dosyada basit metin arama yap. LSP desteklemeyen dosyalar icin fallback.
    Satir numarasi, baglam ve snippet dondurur.
    """
    full_path = os.path.join(LOCAL_ROOT, file_path)
    if not os.path.exists(full_path):
        full_path = file_path
    if not os.path.exists(full_path):
        return {"error": f"Dosya bulunamadi: {file_path}"}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}

    matches = []
    for i, line in enumerate(lines):
        if symbol_name in line:
            # Sembolun tam olarak bu satirda tanimlandigini kontrol et (yaklasik)
            start = max(0, i - 2)
            end = min(len(lines), i + 4)
            snippet = "".join(lines[start:end])
            matches.append({
                "line": i,
                "column": line.find(symbol_name),
                "snippet": snippet,
            })

    if not matches:
        return {"error": f"'{symbol_name}' dosyada bulunamadi", "file": full_path}

    return {
        "file": full_path,
        "symbol": symbol_name,
        "kind": "text_match",
        "matches": matches,
        "note": "LSP fallback: bu dosya turu icin LSP destegi yok, basit metin aramasi yapildi.",
    }


def locate_symbol(file_path, symbol_name, pretty=False):
    """LSP uzerinden sembol konumunu bul; desteklenmeyen dosya turlerinde fallback kullan."""
    full_path = os.path.join(LOCAL_ROOT, file_path)
    if not os.path.exists(full_path):
        full_path = file_path
    if not os.path.exists(full_path):
        return {"error": f"Dosya bulunamadi: {file_path}"}

    ext = os.path.splitext(full_path)[1].lower()
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".kt": "kotlin",
    }
    language = lang_map.get(ext)

    # LSP desteklemeyen dosya turleri -> dogrudan fallback
    if not language:
        if ext in GREP_LIKE_EXTS or ext == "":
            return locate_in_file(file_path, symbol_name)
        return {"error": f"Desteklenmeyen dosya turu: {ext}. "
                         f"LSP: Python, JS/TS, Kotlin. Fallback: {', '.join(sorted(GREP_LIKE_EXTS))}."}

    # Proje kokunu tahmin et — sunucu baslatma hizi icin daralt
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
            parsed = json.loads(err)
        except Exception:
            parsed = {"error": f"LSP client hatasi: {err}"}
        # LSP sembol bulamadiysa ve dosya kucukse fallback dene
        if "bulunamadi" in parsed.get("error", "") or "bos" in parsed.get("error", ""):
            fb = locate_in_file(file_path, symbol_name)
            if "error" not in fb:
                fb["lsp_error"] = parsed.get("error")
                return fb
        return parsed

    try:
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": f"LSP ciktisi parse edilemedi: {e}", "raw": result.stdout}


def prepare_project(project):
    """Bir proje icin context paketi hazirla."""
    cfg = PROJECTS[project]

    # Committed diff + working directory diff
    committed = git_diff_committed(project)
    workdir = git_diff_workdir(project)

    files_committed = parse_diff(committed)
    files_workdir = parse_diff(workdir)

    # Birlestir: ayni dosya varsa working directory oncelikli
    all_files = {}
    for f in files_committed:
        all_files[f["path"]] = f
    for f in files_workdir:
        all_files[f["path"]] = f

    if not all_files:
        return None

    # Her dosya icin detay
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

    # Wiki hedeflerinden ilgili bolumleri cikar
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


# ---------------------------------------------------------------------------
# Wiki arama (query / sor)
# ---------------------------------------------------------------------------

def search_wiki(query, max_results=5):
    """
    Wiki sayfalarinda baslik ve icerik aramasi yap.
    Cache'teki headings listesini kullanir; degismemis sayfalar icin tekrar parse edilmez.
    """
    query_lower = query.lower()
    query_parts = query_lower.split()
    matches = []

    # Tum wiki .md dosyalarini bul
    wiki_files = glob.glob(os.path.join(WIKI_ROOT, "**/*.md"), recursive=True)
    for full_path in wiki_files:
        rel_path = os.path.relpath(full_path, LOCAL_ROOT)
        headings = get_cached_headings(rel_path)
        if not headings:
            continue

        score = 0
        matched_headings = []
        for h in headings:
            title_lower = h["title"].lower()
            if query_lower in title_lower:
                score += 10  # Tam eslesme yuksek puan
                matched_headings.append(h)
            elif any(part in title_lower for part in query_parts):
                score += 3   # Kismi eslesme
                matched_headings.append(h)

        if score > 0:
            matches.append({
                "page": rel_path,
                "score": score,
                "matched_headings": [
                    {"title": h["title"], "level": h["level"], "line": h["line"]}
                    for h in matched_headings[:5]
                ],
            })

    # Puana gore sirala
    matches.sort(key=lambda x: x["score"], reverse=True)

    # En iyi eslesmelerin snippet'ini cikar
    results = []
    for m in matches[:max_results]:
        sections = extract_wiki_sections(m["page"], [h["title"] for h in m["matched_headings"]])
        results.append({
            "page": m["page"],
            "score": m["score"],
            "sections": sections,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Wiki Asistani")
    parser.add_argument("--prepare", action="store_true", help="Context paketi hazirla")
    parser.add_argument("--project", help="Belirli bir proje (tumu icin bos birak)")
    parser.add_argument("--apply", help="Kimi'nin karar JSON'unu uygula (gelecek)")
    parser.add_argument("--pretty", action="store_true", help="JSON'u formatli yaz")
    parser.add_argument("--locate", action="store_true", help="Kod sembolu konumlandir (LSP)")
    parser.add_argument("--file", help="Hedef dosya yolu (--locate icin)")
    parser.add_argument("--symbol", help="Aranacak sembol adi (--locate icin)")
    parser.add_argument("--query", help="Wiki'de konu ara (ingilizce)")
    parser.add_argument("--sor", help="Wiki'de konu ara (turkce)")
    args = parser.parse_args()

    if args.query or args.sor:
        q = args.query or args.sor
        results = search_wiki(q)
        print(json.dumps({
            "query": q,
            "results": results,
            "count": len(results),
        }, indent=2 if args.pretty else None, ensure_ascii=False))
        return

    if args.locate:
        if not args.file or not args.symbol:
            print(json.dumps({"error": "--locate icin --file ve --symbol zorunlu"}, indent=2 if args.pretty else None, ensure_ascii=False))
            sys.exit(1)
        result = locate_symbol(args.file, args.symbol, pretty=args.pretty)
        print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
        if "error" in result and "lsp_error" not in result:
            sys.exit(1)
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
            # Tum projeler
            all_results = []
            for project in PROJECTS:
                result = prepare_project(project)
                if result:
                    all_results.append(result)
            if not all_results:
                print(json.dumps({"results": [], "message": "Hic degisiklik yok"}, indent=2 if args.pretty else None, ensure_ascii=False))
            else:
                print(json.dumps({"results": all_results}, indent=2 if args.pretty else None, ensure_ascii=False))
    elif args.apply:
        print(json.dumps({"error": "apply modu henuz implemente edilmedi"}), file=sys.stderr)
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
