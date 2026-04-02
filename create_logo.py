#!/usr/bin/env python3
"""Script to create the MedNova hospital logo"""

svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 120" width="450" height="120">
  <defs>
    <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0A2A43"/>
      <stop offset="100%" style="stop-color:#0EA5E9"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0A2A43" flood-opacity="0.12"/>
    </filter>
  </defs>
  <rect width="450" height="120" fill="none"/>
  <g transform="translate(15, 15)" filter="url(#softShadow)">
    <rect x="0" y="0" width="75" height="75" rx="14" fill="url(#iconGradient)"/>
    <g fill="#ffffff">
      <rect x="28" y="18" width="19" height="39" rx="2.5"/>
      <rect x="18" y="28" width="39" height="19" rx="2.5"/>
    </g>
  </g>
  <g transform="translate(105, 0)">
    <text x="0" y="45" font-family="Montserrat, Arial, sans-serif" font-size="32" font-weight="700" fill="#0A2A43" letter-spacing="0.5">MedNova</text>
    <text x="0" y="65" font-family="Poppins, Arial, sans-serif" font-size="15" font-weight="600" fill="#0EA5E9" letter-spacing="1.5">MULTISPECIALITY HOSPITAL</text>
  </g>
  <rect x="103" y="72" width="2" height="32" fill="#0A2A43" opacity="0.2" rx="1"/>
  <text x="120" y="100" font-family="Poppins, Arial, sans-serif" font-size="13" font-weight="400" fill="#64748B" letter-spacing="0.3">CareConnect - Patient Scheduling Portal</text>
</svg>'''

with open('static/images/mednova-hospital-logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print('Logo created successfully!')
