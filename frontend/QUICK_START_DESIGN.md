# 🚀 Quick Start - Diseño FutFactos Aplicado

## ✨ Cambios Aplicados

Se ha implementado el diseño de FutFactos capturado con Selenium en todo el proyecto CARC, manteniendo los colores de Rosario Central y toda la funcionalidad existente.

---

## 📦 Archivos Nuevos/Modificados

### Nuevos
- `src/styles/variables.css` - Sistema completo de variables CSS

### Modificados
- `src/styles/index.css` - Estilos globales y botones
- `src/styles/App.css` - Navbar y footer
- `src/styles/HomePage.css` - Página principal
- `src/styles/TrayectoriaGame.css` - Juego de trayectoria
- `src/styles/OrbitaGame.css` - Juego de órbita
- `src/styles/EquipoGame.css` - Juego de equipo

---

## 🎨 Sistema de Diseño

### Colores Principales
```css
Azul RC:    #003f7f
Amarillo RC: #FFD100
Texto:       #000000
Fondo:       #ffffff
```

### Botones (Especificaciones de FutFactos)
```css
Principal:   12px 24px, radius 8px, height 51px
Secundario:  6px 12px, radius 4px, height 40px
```

### Espaciado (Base 4px)
```css
XS: 4px   SM: 8px   MD: 16px
LG: 24px  XL: 32px  2XL: 48px  3XL: 64px
```

---

## 🏃 Iniciar el Proyecto

```bash
# 1. Instalar dependencias (si no están)
npm install

# 2. Iniciar servidor de desarrollo
npm run dev

# 3. Abrir en el navegador
http://localhost:3000
```

---

## ✅ Verificación Rápida

### 1. Home Page
- [ ] Hero section con gradiente azul
- [ ] Logo con animación pulse
- [ ] Cards con hover elevation
- [ ] Botones amarillos con texto oscuro

### 2. Navbar
- [ ] Gradiente azul
- [ ] Links con underline animado
- [ ] Hover amarillo

### 3. Juegos
- [ ] Headers con gradiente
- [ ] Botones con diseño FutFactos
- [ ] Animaciones suaves
- [ ] Responsive funcionando

---

## 🔧 Troubleshooting

### Estilos no se aplican
```bash
# Limpiar cache
rm -rf node_modules/.vite
npm run dev
```

### Colores incorrectos
Verificar `src/styles/variables.css`:
```css
--rc-blue: #003f7f
--rc-yellow: #FFD100
```

---

## 📚 Documentación Completa

Ver `../FUTFACTOS_DESIGN_APPLIED.md` para documentación detallada con:
- Especificaciones completas
- Guía de mantenimiento
- Troubleshooting avanzado
- Ejemplos de código

---

## 🎯 Características Destacadas

1. **Sistema de Variables Centralizado**
   - Fácil personalización
   - Mantenimiento simple
   - Escalable

2. **Botones con Diseño FutFactos**
   - Padding, radius y height exactos
   - Animaciones suaves
   - Estados hover/focus/disabled

3. **Responsive Completo**
   - Desktop (>1024px)
   - Tablet (768-1024px)
   - Mobile (480-768px)
   - Small Mobile (<480px)

4. **Animaciones Profesionales**
   - fadeIn, slideIn, pulse
   - Hover con elevación
   - Transiciones suaves

5. **Funcionalidad Preservada**
   - Backend sin cambios
   - Todos los juegos funcionando
   - API calls correctas

---

## 🚀 Todo Listo!

El proyecto está completamente estilizado con el diseño de FutFactos adaptado a Rosario Central.

**Ejecuta `npm run dev` y disfruta! ⚽🔵⚪**
