#!/usr/bin/env python3
"""
LSP Client Wrapper — JSON-RPC 2.0 over stdio.
Pyright, TypeScript Server ve benzeri LSP sunucuları için evrensel istemci.

Kullanım:
    python3 scripts/lsp-client.py --language python \
        --file ops-bot/bot.py --symbol "handle_message"

Çıktı: JSON (range, kind, snippet)
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time


LOCAL_ROOT = "/home/akn/local"

# Dil → LSP sunucu komutu
LANGUAGE_SERVERS = {
    "python": {
        "cmd": ["pyright-langserver", "--stdio"],
        # Pyright didOpen olmadan da çalışır ama didOpen daha güvenli
        "needs_did_open": True,
    },
    "javascript": {
        "cmd": ["typescript-language-server", "--stdio"],
        "needs_did_open": True,
    },
    "typescript": {
        "cmd": ["typescript-language-server", "--stdio"],
        "needs_did_open": True,
    },
    "kotlin": {
        "cmd": [os.path.expanduser("~/.local/bin/kotlin-language-server")],
        "needs_did_open": True,
    },
}

# SymbolKind → insan-readable isim
SYMBOL_KINDS = {
    1: "file", 2: "module", 3: "namespace", 4: "package",
    5: "class", 6: "method", 7: "property", 8: "field",
    9: "constructor", 10: "enum", 11: "interface", 12: "function",
    13: "variable", 14: "constant", 15: "string", 16: "number",
    17: "boolean", 18: "array", 19: "object", 20: "key",
    21: "null", 22: "enumMember", 23: "struct", 24: "event",
    25: "operator", 26: "typeParameter",
}


class LSPClient:
    def __init__(self):
        self.proc = None
        self.msg_id = 0
        self._lock = threading.Lock()
        self._responses = {}
        self._reader_thread = None
        self._running = False
        self._needs_did_open = False

    # ------------------------------------------------------------------
    # Sunucu yaşam-döngüsü
    # ------------------------------------------------------------------

    def start_server(self, language: str, project_root: str):
        """LSP sunucusunu subprocess olarak başlat, initialize handshake yap."""
        cfg = LANGUAGE_SERVERS.get(language)
        if not cfg:
            raise ValueError(f"Desteklenmeyen dil: {language}. "
                             f"Desteklenenler: {list(LANGUAGE_SERVERS.keys())}")

        self._needs_did_open = cfg.get("needs_did_open", False)

        env = os.environ.copy()
        # Pyright büyük projelerde log spam yapabilir; stderr'i pipe'la
        self.proc = subprocess.Popen(
            cfg["cmd"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root,
            env=env,
        )
        self._running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

        # Initialize
        root_uri = "file://" + os.path.abspath(project_root)
        result = self.send_request("initialize", {
            "processId": os.getpid(),
            "rootUri": root_uri,
            "capabilities": {
                "textDocument": {
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "definition": {"linkSupport": False},
                }
            },
            "workspaceFolders": [
                {"uri": root_uri, "name": os.path.basename(project_root)}
            ],
        }, timeout=30)

        # Initialized notification
        self._send_notification("initialized", {})
        return result

    def shutdown(self):
        """Graceful kapatma."""
        self._running = False
        try:
            self.send_request("shutdown", {}, timeout=5)
            self._send_notification("exit", {})
        except Exception:
            pass
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            try:
                self.proc.kill()
                self.proc.wait()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # JSON-RPC 2.0 transport
    # ------------------------------------------------------------------

    def _send_notification(self, method, params):
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        self._write_payload(payload)

    def _send_request(self, method, params):
        with self._lock:
            self.msg_id += 1
            msg_id = self.msg_id
        payload = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params}
        self._write_payload(payload)
        return msg_id

    def _write_payload(self, payload):
        content = json.dumps(payload, ensure_ascii=False)
        data = (f"Content-Length: {len(content.encode('utf-8'))}\r\n"
                f"\r\n"
                f"{content}")
        self.proc.stdin.write(data.encode("utf-8"))
        self.proc.stdin.flush()

    def _read_loop(self):
        """Stdout'tan LSP mesajlarını oku, id'ye göre responses sözlüğüne yaz."""
        while self._running:
            try:
                msg = self._read_message()
                if msg is None:
                    continue
                if "id" in msg:
                    with self._lock:
                        self._responses[msg["id"]] = msg
            except Exception as e:
                if self._running:
                    sys.stderr.write(f"[lsp-client] read error: {e}\n")

    def _read_message(self):
        """Tek bir JSON-RPC mesajını oku (Content-Length başlığına göre)."""
        stdout = self.proc.stdout
        # Content-Length satırını oku
        line = b""
        while True:
            byte = stdout.read(1)
            if not byte:
                return None
            line += byte
            if line.endswith(b"\r\n"):
                break
        if not line.startswith(b"Content-Length:"):
            return None
        length = int(line.decode("utf-8").split(":")[1].strip())
        # Boş satırı oku (\r\n)
        stdout.read(2)
        # Gövdeyi oku
        body = stdout.read(length)
        return json.loads(body.decode("utf-8"))

    # ------------------------------------------------------------------
    # Yüksek seviyeli API
    # ------------------------------------------------------------------

    def send_request(self, method, params, timeout=10):
        """İstek gönder ve yanıt bekle."""
        msg_id = self._send_request(method, params)
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if msg_id in self._responses:
                    resp = self._responses.pop(msg_id)
                    if "error" in resp:
                        raise RuntimeError(f"LSP error: {resp['error']}")
                    return resp.get("result")
            time.sleep(0.05)
        raise TimeoutError(f"LSP request timeout: {method} (timeout={timeout}s)")

    def did_open(self, file_path: str, language_id: str, text: str):
        """textDocument/didOpen bildirimi gönder."""
        uri = self._file_uri(file_path)
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": 1,
                "text": text,
            }
        })
        # Sunucunun işlemesi için kısa bekle
        time.sleep(0.3)

    def document_symbol(self, file_path: str, file_text: str = None):
        """Bir dosyadaki tüm sembolleri listele (DocumentSymbol[] veya SymbolInformation[])."""
        uri = self._file_uri(file_path)
        if self._needs_did_open and file_text is not None:
            lang = self._guess_lang(file_path)
            self.did_open(file_path, lang, file_text)
        return self.send_request("textDocument/documentSymbol", {
            "textDocument": {"uri": uri}
        })

    def goto_definition(self, file_path: str, line: int, character: int):
        """Tanım noktasına git."""
        uri = self._file_uri(file_path)
        return self.send_request("textDocument/definition", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
        })

    def find_references(self, file_path: str, line: int, character: int):
        """Referansları bul."""
        uri = self._file_uri(file_path)
        return self.send_request("textDocument/references", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character},
            "context": {"includeDeclaration": True},
        })

    # ------------------------------------------------------------------
    # Yardımcılar
    # ------------------------------------------------------------------

    @staticmethod
    def _file_uri(file_path: str) -> str:
        abs_path = os.path.abspath(file_path)
        return "file://" + abs_path

    @staticmethod
    def _guess_lang(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1]
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }
        return mapping.get(ext, "plaintext")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False


# ---------------------------------------------------------------------------
# Sembol arama & çıktı formatlama
# ---------------------------------------------------------------------------

def find_symbol_in_tree(symbols, name):
    """
    DocumentSymbol[] veya SymbolInformation[] ağacında isme göre sembol bul.
    İlk eşleşmeyi döndürür.
    """
    if not isinstance(symbols, list):
        return None
    for sym in symbols:
        if sym.get("name") == name:
            return sym
        # Hierarchical DocumentSymbol: children varsa recursive ara
        children = sym.get("children")
        if children:
            found = find_symbol_in_tree(children, name)
            if found:
                return found
    return None


def format_symbol_result(file_path, symbol_name, symbol_obj):
    """Sembol bilgisini standart JSON çıktıya çevir."""
    if not symbol_obj:
        return None

    kind_num = symbol_obj.get("kind", 0)
    kind_name = SYMBOL_KINDS.get(kind_num, f"unknown({kind_num})")

    # DocumentSymbol → range, SymbolInformation → location.range
    rng = symbol_obj.get("range") or symbol_obj.get("location", {}).get("range")
    if not rng:
        return None

    start_line = rng["start"]["line"]
    end_line = rng["end"]["line"]

    # Snippet çıkar
    snippet = extract_snippet(file_path, start_line, end_line)

    return {
        "file": file_path,
        "symbol": symbol_name,
        "kind": kind_name,
        "range": rng,
        "snippet": snippet,
    }


def extract_snippet(file_path, start_line, end_line, max_lines=40):
    """Dosyadan satır aralığını oku."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return None

    if not lines:
        return None

    start = max(0, start_line)
    end = min(len(lines), end_line + 1)
    selected = lines[start:end]

    # Çok uzunsa kısalt
    if len(selected) > max_lines:
        selected = selected[:max_lines]
        selected.append(f"\n... [{end_line - start_line + 1 - max_lines} satır daha] ...\n")

    return "".join(selected)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LSP Client — sembol bulma")
    parser.add_argument("--language", default="python", help="python | javascript | typescript")
    parser.add_argument("--file", required=True, help="Hedef dosya yolu")
    parser.add_argument("--symbol", required=True, help="Aranacak sembol adı")
    parser.add_argument("--project-root", default=LOCAL_ROOT, help="Proje kök dizini")
    parser.add_argument("--pretty", action="store_true", help="Formatlı JSON çıktı")
    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"Dosya bulunamadı: {file_path}"}))
        sys.exit(1)

    try:
        with LSPClient() as client:
            client.start_server(args.language, args.project_root)

            # Pyright diskten okur ama didOpen daha güvenli
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_text = f.read()

            symbols = client.document_symbol(file_path, file_text=file_text)
            if not symbols:
                print(json.dumps({"error": "Sembol listesi boş döndü"}))
                sys.exit(1)

            sym = find_symbol_in_tree(symbols, args.symbol)
            if not sym:
                # Bulunamadıysa mevcut sembol isimlerini listele
                names = [s.get("name") for s in symbols if "name" in s]
                print(json.dumps({
                    "error": f"'{args.symbol}' sembolü bulunamadı",
                    "available_symbols": names[:50],
                }, indent=2 if args.pretty else None, ensure_ascii=False))
                sys.exit(1)

            result = format_symbol_result(file_path, args.symbol, sym)
            print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
