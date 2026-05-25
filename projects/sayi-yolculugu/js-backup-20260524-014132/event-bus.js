/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Event Bus
   Loose coupling için merkezi olay yönetimi.
   ═══════════════════════════════════════════════════════════ */

class EventBus {
  constructor() {
    this._events = new Map();
  }

  on(event, callback) {
    if (!this._events.has(event)) {
      this._events.set(event, new Set());
    }
    this._events.get(event).add(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    const set = this._events.get(event);
    if (set) set.delete(callback);
  }

  emit(event, payload) {
    const set = this._events.get(event);
    if (set) {
      set.forEach(cb => {
        try { cb(payload); } catch (e) { console.error(`EventBus error on ${event}:`, e); }
      });
    }
  }

  once(event, callback) {
    const wrapper = (payload) => {
      this.off(event, wrapper);
      callback(payload);
    };
    this.on(event, wrapper);
  }
}

export const events = new EventBus();
