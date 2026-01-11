import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './styles/calculation-results.css'; // Backend inline styles → Frontend CSS
import App from './App';
import reportWebVitals from './reportWebVitals';
// Konsol log filtreleme aracını import et
import './utils/consoleLogFilter';
// Service Worker'ı kaldır
import { unregisterServiceWorker } from './serviceWorkerUnregister';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service Worker'ı devre dışı bırak
unregisterServiceWorker();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
