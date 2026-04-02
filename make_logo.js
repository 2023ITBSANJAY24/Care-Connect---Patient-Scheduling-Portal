const fs = require('fs');
const content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200"><rect width="200" height="200" fill="white"/><circle cx="100" cy="85" r="55" fill="#0d9488"/><circle cx="100" cy="85" r="48" fill="#14b8a6"/><rect x="92" y="60" width="16" height="50" rx="2" fill="white"/><rect x="75" y="77" width="50" height="16" rx="2" fill="white"/><text x="100" y="155" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#0d9488" text-anchor="middle">MEDICAL</text><text x="100" y="172" font-family="Arial, sans-serif" font-size="8" fill="#6b7280" text-anchor="middle">your slogan here</text></svg>';
fs.writeFileSync('static/images/careconnect-logo.svg', content);
console.log('SVG Logo created');

