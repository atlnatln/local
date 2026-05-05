"""ACP (Agent Client Protocol) JSON-RPC stdio client for kimi-cli."""

from __future__ import annotations

import json
import logging
import os
import select
import signal
import subprocess
import threading
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class AcpClient:
    """Low-level ACP client that speaks JSON-RPC 2.0 over stdio with `kimi acp`."""

    def __init__(
        self,
        cmd: str = "kimi",
        args: list[str] | None = None,
        cwd: str | None = None,
        notification_handler: Callable[[dict], None] | None = None,
        permission_handler: Callable[[dict, threading.Event], None] | None = None,
        use_pty: bool = False,
    ):
        self.cmd = cmd
        self.args = args or ["acp"]
        self.cwd = cwd
        self._notification_handler = notification_handler
        self._permission_handler = permission_handler
        self.use_pty = use_pty

        self._proc: subprocess.Popen | None = None
        self._master_fd: int | None = None
        self._pid: int | None = None
        self._lock = threading.Lock()
        self._request_id = 0
        self._pending: Dict[int, threading.Event] = {}
        self._responses: Dict[int, dict] = {}
        self._reader_thread: threading.Thread | None = None
        self._stop_reader = threading.Event()
        self._initialized = False
        self.last_start_error: str | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """Launch the `kimi acp` subprocess and run initialize handshake."""
        self.last_start_error = None
        with self._lock:
            if self._proc is not None or (self.use_pty and self._pid is not None):
                logger.warning("ACP client already started")
                return True

            logger.info("Starting ACP server: %s %s", self.cmd, " ".join(self.args))
            try:
                if self.use_pty:
                    import pty
                    master_fd, slave_fd = pty.openpty()
                    pid = os.fork()
                    if pid == 0:
                        # Child
                        os.setsid()
                        os.dup2(slave_fd, 0)
                        os.dup2(slave_fd, 1)
                        os.dup2(slave_fd, 2)
                        os.close(master_fd)
                        if slave_fd > 2:
                            os.close(slave_fd)
                        if self.cwd:
                            os.chdir(self.cwd)
                        os.execlp(self.cmd, self.cmd, *self.args)
                        os._exit(1)
                    else:
                        os.close(slave_fd)
                        self._master_fd = master_fd
                        self._pid = pid
                else:
                    self._proc = subprocess.Popen(
                        [self.cmd, *self.args],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        cwd=self.cwd,
                    )
            except Exception as exc:
                self.last_start_error = str(exc)
                logger.error("Failed to start ACP server: %s", exc)
                return False

            self._stop_reader.clear()
            self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self._reader_thread.start()

        # ACP handshake
        resp = self._request("initialize", {
            "protocolVersion": 1,
            "clientInfo": {"name": "telegram-kimi", "version": "1.0.0"},
            "capabilities": {},
        }, timeout=10)

        if resp is None or "error" in resp:
            logger.error("ACP initialize failed: %s", resp)
            self.last_start_error = f"ACP initialize failed: {resp}"
            self.close()
            return False

        logger.info("ACP initialized: %s", resp.get("result", {}).get("agentInfo", {}))
        self._initialized = True
        return True

    def close(self) -> None:
        """Terminate the subprocess and cleanup."""
        with self._lock:
            self._initialized = False
            self._stop_reader.set()
            # Wake up any pending waiters so they don't hang forever
            for event in list(self._pending.values()):
                event.set()

            if self.use_pty:
                if self._pid is not None:
                    try:
                        os.kill(self._pid, signal.SIGTERM)
                        os.waitpid(self._pid, 0)
                    except (ProcessLookupError, ChildProcessError):
                        pass
                    self._pid = None
                if self._master_fd is not None:
                    try:
                        os.close(self._master_fd)
                    except OSError:
                        pass
                    self._master_fd = None
            else:
                if self._proc is not None:
                    try:
                        self._proc.terminate()
                        self._proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self._proc.kill()
                        self._proc.wait(timeout=2)
                    except Exception as exc:
                        logger.warning("Error terminating ACP server: %s", exc)
                    finally:
                        self._proc = None

        if self._reader_thread is not None and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=3)

        logger.info("ACP client closed")

    def is_ready(self) -> bool:
        if not self._initialized:
            return False
        if self.use_pty:
            if self._pid is None:
                return False
            try:
                pid, _ = os.waitpid(self._pid, os.WNOHANG)
                return pid == 0
            except ChildProcessError:
                return False
        return self._proc is not None and self._proc.poll() is None

    # ------------------------------------------------------------------
    # Session API
    # ------------------------------------------------------------------

    def new_session(self, cwd: str) -> Optional[str]:
        """Create a new session. Returns sessionId or None."""
        resp = self._request("session/new", {"cwd": cwd, "mcpServers": []}, timeout=15)
        if resp is None or "error" in resp:
            logger.error("session/new failed: %s", resp)
            return None
        sid = resp.get("result", {}).get("sessionId")
        logger.info("New session: %s", sid)
        return sid

    def prompt(self, session_id: str, text: str, timeout: float | None = None) -> dict | None:
        """Send a user prompt. Returns the final response dict or None."""
        return self._request("session/prompt", {
            "sessionId": session_id,
            "prompt": [{"type": "text", "text": text}],
        }, timeout=timeout)

    def cancel(self, session_id: str) -> None:
        """Send a session/cancel notification (no response expected)."""
        self._notify("session/cancel", {"sessionId": session_id})
        logger.info("Sent session/cancel for %s", session_id)

    # ------------------------------------------------------------------
    # Internal I/O
    # ------------------------------------------------------------------

    def _request(self, method: str, params: dict, timeout: float | None = 30) -> dict | None:
        with self._lock:
            self._request_id += 1
            req_id = self._request_id
            event = threading.Event()
            self._pending[req_id] = event

        payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        self._send_raw(payload)

        if timeout is None:
            event.wait()
        else:
            if not event.wait(timeout=timeout):
                logger.warning("Request %s timed out (%ss)", req_id, timeout)
                with self._lock:
                    self._pending.pop(req_id, None)
                return None

        with self._lock:
            resp = self._responses.pop(req_id, None)
            self._pending.pop(req_id, None)
        return resp

    def _notify(self, method: str, params: dict) -> None:
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        self._send_raw(payload)

    def _send_raw(self, payload: dict) -> None:
        line = json.dumps(payload, ensure_ascii=False)
        logger.debug("→ %s", line[:500])
        with self._lock:
            if self.use_pty:
                if self._master_fd is None:
                    raise RuntimeError("ACP server not running")
                os.write(self._master_fd, (line + "\n").encode("utf-8"))
            else:
                if self._proc is None or self._proc.stdin is None:
                    raise RuntimeError("ACP server not running")
                self._proc.stdin.write(line + "\n")
                self._proc.stdin.flush()

    def _reader_loop(self) -> None:
        """Background thread that reads JSON-RPC lines from stdout."""
        if self.use_pty:
            self._reader_loop_pty()
            return

        while not self._stop_reader.is_set():
            try:
                if self._proc is None or self._proc.stdout is None:
                    break
                ready, _, _ = select.select([self._proc.stdout], [], [], 1.0)
                if not ready:
                    continue
                line = self._proc.stdout.readline()
                if not line:
                    # EOF
                    logger.warning("ACP stdout EOF")
                    break
                line = line.strip()
                if not line:
                    continue
                logger.debug("← %s", line[:500])
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Non-JSON line from ACP: %s", line[:200])
                    continue
                self._dispatch(msg)
            except Exception as exc:
                logger.exception("ACP reader loop error: %s", exc)
                break

        logger.info("ACP reader loop exited")

    def _reader_loop_pty(self) -> None:
        """PTY variant of the reader loop."""
        buffer = bytearray()
        while not self._stop_reader.is_set():
            try:
                master = self._master_fd
                if master is None:
                    break
                ready, _, _ = select.select([master], [], [], 1.0)
                if not ready:
                    continue
                master = self._master_fd
                if master is None:
                    break
                data = os.read(master, 4096)
                if not data:
                    logger.warning("ACP PTY EOF")
                    break
                buffer.extend(data)
                while b"\n" in buffer:
                    idx = buffer.index(b"\n")
                    line = buffer[:idx].decode("utf-8", errors="replace").strip()
                    buffer = buffer[idx + 1:]
                    if not line:
                        continue
                    logger.debug("← %s", line[:500])
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning("Non-JSON line from ACP: %s", line[:200])
                        continue
                    self._dispatch(msg)
            except Exception as exc:
                logger.exception("ACP PTY reader loop error: %s", exc)
                break

        logger.info("ACP reader loop exited")

    def _dispatch(self, msg: dict) -> None:
        """Route a JSON-RPC message to response waiter, notification handler, or agent request handler."""
        if "method" in msg and "id" in msg:
            # PTY echo: when running over a pseudo-tty, our own requests can be echoed back.
            # If the id is still in _pending, this is an echo of our own request, not a real agent request.
            with self._lock:
                if msg["id"] in self._pending:
                    logger.debug("Ignoring PTY echo for request %s", msg["id"])
                    return
            # It's a request FROM the agent TO us (e.g. session/request_permission)
            self._handle_agent_request(msg)
        elif "id" in msg:
            # It's a response to one of our requests
            req_id = msg["id"]
            with self._lock:
                self._responses[req_id] = msg
                event = self._pending.get(req_id)
            if event is not None:
                event.set()
        elif "method" in msg:
            # It's a notification
            if self._notification_handler is not None:
                try:
                    self._notification_handler(msg)
                except Exception:
                    logger.exception("Notification handler error")
        else:
            logger.warning("Unrecognized ACP message: %s", msg)

    def _handle_agent_request(self, msg: dict) -> None:
        """Handle JSON-RPC requests that come FROM the agent (e.g. permission requests)."""
        method = msg["method"]
        req_id = msg["id"]
        params = msg.get("params", {})

        if method == "session/request_permission":
            tool_title = ""
            try:
                content = params.get("toolCall", {}).get("content", [])
                if content:
                    tool_title = content[0].get("content", {}).get("text", "")[:200]
            except Exception:
                pass

            if self._permission_handler is not None:
                logger.info("Permission request waiting for user: %s", tool_title or method)
                event = threading.Event()
                self._permission_handler(
                    {"request_id": req_id, "session_id": params.get("sessionId"), "title": tool_title, "options": params.get("options", [])},
                    event,
                )
                # Wait for user decision (with 5 minute timeout)
                if not event.wait(timeout=300):
                    logger.warning("Permission request timed out, rejecting")
                    self._send_permission_response(req_id, "reject")
                return

            # Fallback: auto-approve if no permission handler registered
            logger.info("Auto-approving permission: %s", tool_title or method)
            self._send_permission_response(req_id, "approve")
        else:
            logger.warning("Unhandled agent request: %s", method)
            self._send_raw({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {method} not implemented"},
            })

    def _send_permission_response(self, req_id: int, option_id: str) -> None:
        """Send a session/request_permission response."""
        if option_id == "reject":
            self._send_raw({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"outcome": {"outcome": "cancelled"}},
            })
        else:
            self._send_raw({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"outcome": {"outcome": "selected", "optionId": option_id}},
            })
