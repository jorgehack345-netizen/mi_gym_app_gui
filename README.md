# Gimnasio · Control de Pagos (GUI · Offline)

![Banner](assets/banner.png)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows&logoColor=white)]()

Aplicación **con interfaz gráfica (Tkinter)** para gestionar clientes de un gimnasio:
- Registrar clientes con plan **semanal** o **mensual** (con precio propio)
- Ver **pendientes de pago**: atrasados, vencen hoy y próximos _N_ días
- **Cobrar/Renovar** con cálculo automático de adeudos y actualización de la **próxima fecha**
- Activar/Inactivar clientes
- Exportar a **CSV** (Excel)

> Funciona **100% offline** y no requiere instalar paquetes extras (Tkinter viene con Python).

---

## 🖼️ Vista previa

![Dashboard](assets/screenshot_dashboard.png)

---

## 🚀 Cómo ejecutar

### Opción 1 — Doble clic (Windows)
1. Descarga y descomprime este repositorio
2. Abre la carpeta `mi_gym_app_gui_github/`
3. **Doble clic:** `run_app.bat`

### Opción 2 — Terminal
```bat
cd mi_gym_app_gui_github
python app_gui.py
```

> Si usas **WinPython en USB**, abre `WinPythonCommandPrompt.exe`, navega a la carpeta y ejecuta el mismo comando.

---

## ⚙️ Configuración
En la pestaña **Configuración** puedes:
- Cambiar **precio semanal** y **mensual** por defecto
- Definir cuántos **días** se consideran "próximos"

Estos valores se guardan en `data/clientes.json` junto con la lista de clientes.

---

## 📦 Estructura
```
mi_gym_app_gui_github/
├─ app_gui.py          # Interfaz (ventanas, tablas, formularios)
├─ core.py             # Lógica de negocio y persistencia (JSON)
├─ data/               # Aquí se crea clientes.json
├─ assets/             # Imágenes para el README (banner, icono, screenshot)
├─ run_app.bat         # Doble clic para iniciar (Windows)
├─ LICENSE             # MIT
├─ .gitignore
└─ .gitattributes
```

---

## 🔄 Exportar datos
Desde la pestaña **Exportar** puedes generar `data/reporte_clientes.csv` para abrir en Excel.

---

## 📝 Licencia
Este proyecto está bajo licencia **MIT**. Ver [LICENSE](LICENSE).
