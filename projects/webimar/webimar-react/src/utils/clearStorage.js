// Storage temizlik utility
console.log('🧹 Clearing all browser storage...');

// LocalStorage temizle
if (typeof localStorage !== 'undefined') {
  const keys = Object.keys(localStorage);
  console.log('📦 LocalStorage keys:', keys);
  localStorage.clear();
  console.log('✅ LocalStorage cleared');
}

// SessionStorage temizle
if (typeof sessionStorage !== 'undefined') {
  const keys = Object.keys(sessionStorage);
  console.log('📦 SessionStorage keys:', keys);
  sessionStorage.clear();
  console.log('✅ SessionStorage cleared');
}

// Cookies temizle
if (typeof document !== 'undefined') {
  document.cookie.split(";").forEach((c) => {
    const eqPos = c.indexOf("=");
    const name = eqPos > -1 ? c.substr(0, eqPos) : c;
    document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
  });
  console.log('🍪 Cookies cleared');
}

console.log('✨ All storage cleared successfully!');
