---
name: canva-local-design
description: "Use when user wants permanent Canva-like design workflows without subscriptions or trials: create/edit graphics, resize for channels, bulk-generate from data, translate/localize, review design quality, enforce brand rules, implement feedback, build branded or educational presentations, fit speaker notes to time, and export editable local SVG/HTML/PPTX plus PNG/PDF. Local-first; Canva Connector remains optional."
version: 2.0.0
author: Hermes Agent; workflows adapted from canva-sdks/canva-skills
license: Apache-2.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [design, canva, graphics, svg, html, png, pdf, social-media, bulk-create, translation, brand-check, feedback, presentations, templates]
    related_skills: [claude-design, baoyu-infographic, powerpoint, popular-web-designs, architecture-diagram]
---

# Canva Local Design

## Objetivo

Crear piezas visuales con capacidad práctica similar a Canva, sin cuenta, suscripción ni trial. Entregable principal siempre queda local, editable y reutilizable.

Esta skill no intenta clonar editor de Canva. Resuelve necesidad real: recibir contenido y recursos, diseñar pieza, mostrar vista previa, corregirla y exportarla en formatos utilizables.

## Cuándo usar

Usar para:

- posts, historias, carruseles y portadas de redes sociales
- miniaturas de YouTube
- flyers, afiches, menús, tarjetas e invitaciones
- banners, anuncios y material promocional
- certificados, hojas informativas y piezas imprimibles
- presentaciones visuales
- infografías
- logos simples, wordmarks y kits visuales básicos
- plantillas reutilizables
- rediseñar una pieza desde imagen, boceto o contenido existente

No usar sola cuando otra skill cubre mejor trabajo:

- infografía con mucha información → `baoyu-infographic`
- presentación PowerPoint editable → `powerpoint`
- sitio, prototipo o UI interactiva → `claude-design`
- estilo web inspirado en sistema conocido → `popular-web-designs`
- diagrama técnico → `architecture-diagram` o `excalidraw`
- ilustración/fondo/foto generada → `image_generate`, luego componer texto aquí

## Principio permanente y gratuito

1. Fuente maestra local: `.svg` para diseño estático o `.html` para varias páginas/interacción.
2. Sin dependencias remotas obligatorias. Evitar CDNs, fuentes pagas y enlaces que puedan caducar.
3. Usar fuentes del sistema o incluir fuente libre local solo si ya existe/licencia permite distribución.
4. Exportar PNG/JPG/PDF como derivados; nunca reemplazar fuente editable.
5. No requerir Canva, Adobe, Figma, cuentas externas ni trials.
6. `image_generate` es opcional. Si no está disponible, usar recursos suministrados, formas, tipografía y composición local.

## Formato de trabajo

Crear carpeta bajo ubicación pedida por usuario. Si no indica ubicación:

```text
<workspace>/Diseños/<nombre-corto>/
├── source/
│   ├── diseño.svg              # o index.html
│   └── assets/                 # imágenes/fuentes suministradas
├── exports/
│   ├── diseño.png
│   └── diseño.pdf              # solo si se necesita
├── previews/
│   └── preview.png
└── brief.md
```

En Windows y sin workspace indicado, preferir carpeta estable elegida por usuario para proyectos. No guardar solo en carpeta temporal.

Revisiones grandes conservan versión anterior:

```text
diseño-v1.svg
diseño-v2.svg
```

Cambios pequeños pueden editar versión actual.

## Brief mínimo

Extraer del mensaje y materiales:

- tipo de pieza
- texto exacto
- público y objetivo
- tamaño/plataforma
- colores o marca
- imágenes/logos disponibles
- estilo deseado
- formato final

Si falta dato con default obvio, actuar. Preguntar solo cuando falta texto esencial, logo obligatorio, tamaño no inferible o decisión cambia resultado de forma importante.

Nunca inventar teléfonos, precios, fechas, direcciones, estadísticas, testimonios ni beneficios comerciales. Marcar texto faltante como `PENDIENTE` si usuario autoriza borrador.

Guardar decisiones y contenido exacto en `brief.md`.

## Selección del lienzo

Defaults comunes:

| Pieza | Tamaño |
|---|---:|
| Instagram post cuadrado | 1080×1080 px |
| Instagram/Facebook vertical | 1080×1350 px |
| Story/Reel/TikTok | 1080×1920 px |
| YouTube thumbnail | 1280×720 px |
| Facebook cover | 1640×624 px |
| X/Twitter post | 1600×900 px |
| LinkedIn post | 1200×1200 px |
| Presentación | 1920×1080 px, 16:9 |
| A4 impresión | 210×297 mm |
| Carta impresión | 8.5×11 in |
| Tarjeta | tamaño pedido + 3 mm sangrado si imprenta lo exige |

Para plataformas, confirmar tamaño actual con web solo si usuario exige especificación vigente. Para imprenta, pedir requisitos de sangrado, CMYK y resolución si son críticos; SVG/HTML y capturas de navegador trabajan normalmente en RGB.

## Elección de fuente maestra

### SVG — default para pieza estática

Elegir SVG para una página, texto preciso, formas, imágenes, logos y salida escalable.

Reglas:

- `viewBox` igual al lienzo lógico.
- Incluir `width` y `height`.
- Usar grupos con IDs legibles: `background`, `image`, `headline`, `details`, `cta`, `brand`.
- Escapar XML.
- Mantener texto como `<text>` para edición; convertir a curvas solo si usuario lo pide y herramienta disponible.
- Incrustar imágenes como data URI solo cuando portabilidad pesa más que tamaño. Si no, usar rutas relativas bajo `source/assets/`.
- Añadir `aria-label` o `<title>` descriptivo.

### HTML — multipágina, carrusel, deck o plantilla dinámica

Elegir HTML para varias páginas, variaciones, controles editables o maquetación compleja.

Reglas:

- HTML/CSS/JS autocontenido cuando sea razonable.
- Cada página/slides tiene tamaño fijo y clase clara.
- Añadir modo impresión con `@page` y `@media print`.
- No cargar librerías si CSS nativo resuelve.
- Respetar `prefers-reduced-motion` si hay animación.

### PPTX

Si usuario necesita editar diapositivas en PowerPoint/WPS/LibreOffice, cargar skill `powerpoint`; no entregar solo imágenes pegadas salvo pedido explícito.

## Sistema visual mínimo

Antes de dibujar, definir en `brief.md`:

- una idea principal
- jerarquía: título → apoyo → acción/dato
- paleta: 1 color dominante, 1 acento, neutros
- máximo 2 familias tipográficas
- escala tipográfica consistente
- grid, márgenes y zonas seguras
- tratamiento de imágenes

Priorizar legibilidad y jerarquía sobre decoración.

### Reglas de composición

- Una pieza = un mensaje principal.
- Crear punto focal claro.
- Alinear elementos a grid real.
- Mantener contraste suficiente entre texto y fondo.
- No poner texto importante pegado a bordes.
- Evitar cinco estilos, múltiples sombras y exceso de iconos.
- Reducir contenido antes de reducir texto a tamaño ilegible.
- Para móvil, evaluar vista reducida: título y CTA deben seguir claros.
- Para impresión, texto normal mínimo aproximado 10–12 pt salvo notas secundarias.

### Anti-diseño genérico

Evitar por default:

- degradado violeta/azul de IA
- tarjetas iguales con icono sobre cada título
- glassmorphism sin función
- exceso de bordes redondeados
- emojis como iconos profesionales
- datos inventados para llenar espacio
- texto generado dentro de imágenes de IA

Texto, precios, fechas y logos siempre se componen como vectores/HTML, no dentro de imagen generada.

## Recursos

Orden de preferencia:

1. logo, fotos e identidad entregados por usuario
2. recursos ya presentes en proyecto
3. formas, patrones y tipografía creados en SVG/CSS
4. imágenes con licencia libre verificable
5. imagen generada opcional

No descargar ni reutilizar imágenes sin licencia clara. Guardar atribución/licencia en `brief.md` cuando aplique.

No clonar exactamente diseño protegido de otra marca. Extraer principios generales y producir composición original.

## Flujo de ejecución

1. **Inspeccionar contexto**
   - Leer mensaje, archivos, imágenes y referencias.
   - Verificar dimensiones de recursos importantes.
   - Termina cuando contenido exacto y restricciones están registrados.

2. **Elegir ruta**
   - Cargar skill especializada si corresponde.
   - Elegir SVG, HTML o PPTX según uso futuro.
   - Termina cuando fuente maestra y tamaño quedan definidos.

3. **Crear brief**
   - Guardar texto exacto, audiencia, objetivo, paleta, jerarquía y exportaciones.
   - Termina cuando no quedan datos críticos inventados.

4. **Diseñar primera versión**
   - Construir composición completa, no stub.
   - Usar mínimo código y assets.
   - Termina cuando fuente abre sin errores y todas las capas clave existen.

5. **Renderizar vista previa**
   - Abrir SVG/HTML en navegador.
   - Ajustar viewport al lienzo o relación correcta.
   - Capturar PNG.
   - Termina cuando preview refleja fuente actual.

6. **Auditoría visual**
   - Inspeccionar imagen renderizada, no solo código.
   - Revisar recortes, solapes, jerarquía, ortografía, contraste, márgenes, resolución y fidelidad del texto.
   - Corregir hallazgos y volver a capturar.
   - Termina sin errores visibles importantes.

7. **Exportar**
   - PNG: screenshot exacto o exportador local disponible.
   - JPG: solo para piezas fotográficas donde menor peso importa.
   - PDF: impresión del HTML/SVG mediante navegador o herramienta local disponible.
   - Mantener SVG/HTML editable.
   - Termina cuando archivos existen y abren.

8. **Entregar**
   - Mostrar preview.
   - Indicar rutas de fuente y exportaciones.
   - Resumir tamaño y formato.
   - Aclarar cualquier limitación real, especialmente CMYK, sangrado o fuentes.

## Verificación técnica

Siempre ejecutar controles reales:

- archivo fuente existe y no está vacío
- XML/HTML parsea o abre en navegador
- consola sin errores relevantes para HTML
- viewport coincide con tamaño/relación solicitada
- preview inspeccionado visualmente
- texto visible coincide con brief
- rutas de imágenes resuelven
- exportaciones existen y pueden abrirse

Para diseños multipágina, revisar todas las páginas, no solo primera.

## Logos

Puede crear logos simples y originales: wordmark, monograma, símbolo geométrico y variantes claro/oscuro.

Entregar mínimo:

- SVG vectorial
- PNG transparente
- versión clara y oscura cuando sea necesaria
- notas de tipografía y color

No prometer búsqueda legal de marca. No imitar logos existentes. Para identidad profesional crítica, advertir que diseño necesita revisión humana y comprobación de marca registrada.

## Plantillas reutilizables

Cuando usuario pide plantilla:

- separar contenido editable de decoración
- usar IDs/nombres claros
- documentar campos en `brief.md`
- mantener zonas de texto con límites predecibles
- crear ejemplo completo, no lienzo vacío
- conservar proporciones al reemplazar imágenes

Campos típicos:

```text
{{TITULO}}
{{SUBTITULO}}
{{FECHA}}
{{PRECIO}}
{{CTA}}
{{IMAGEN_PRINCIPAL}}
{{LOGO}}
```

Si usuario pedirá muchas variantes, preferir HTML con objeto de datos pequeño o plantilla SVG con reemplazo directo; no crear aplicación completa sin necesidad.

## Capacidades ampliadas: Canva Agent Skills adaptadas a local

Esta skill incorpora flujos del repositorio oficial `canva-sdks/canva-skills`, pero los adapta a archivos locales y herramientas abiertas. Cargar `references/canva-agent-workflows.md` cuando pedido incluya cualquiera de estas capacidades:

### Adaptación multiformato

Crear versiones para varias redes/plataformas desde una fuente maestra. **Remaquetar** cada relación; nunca estirar o recortar ciegamente. Renderizar y auditar cada destino. Si un formato falla, continuar con demás y reportar por formato.

### Creación masiva

Generar una pieza por fila desde CSV, TSV, Excel, JSON, tabla o URL:

1. mostrar columnas, conteo y muestra
2. mapear columnas a placeholders de plantilla
3. confirmar ambigüedades
4. probar 3 filas en lotes grandes
5. generar secuencialmente
6. entregar `results.csv` con éxitos y fallos

Plantillas locales reemplazan Autofill de Canva Enterprise; no requieren plan Canva.

### Edición segura y feedback

Para cambios grandes, traducciones y feedback:

- conservar original y crear nueva versión
- inspeccionar render actual
- agrupar operaciones
- mostrar preview nuevo
- pedir aprobación antes de sobrescribir o destruir
- entregar checklist de cambios no automatizables

Crítica de diseño siempre parte del render real y usa severidad `High / Med / Low`, ubicación exacta y fix concreto. Separar crítica de edición salvo pedido explícito.

### Brand check

Comparar diseño contra fuentes reales de marca: guía, `DESIGN.md`, paleta, tipografías, logos y ejemplos aprobados. Clasificar `On brand / Off brand / No verificable`. Nunca inventar hex, fuentes ni reglas. Si solo existe captura, declarar aproximación.

### Traducción y localización

Trabajar siempre en copia por idioma. Conservar estructura, nombres propios y términos protegidos. Recalcular cajas por expansión/contracción, verificar glifos y renderizar todas las páginas. Original nunca se modifica.

### Presentaciones avanzadas

- **Branded deck:** brief → arco narrativo → plan por slide → notas → PPTX/HTML.
- **Classroom deck:** plan de clase → objetivos → secuencia pedagógica → actividades/checks → notas docentes.
- **Time fitting:** duración ÷ slides; guía de 150 palabras/minuto; ajustar notas, no contenido visible, salvo pedido separado.

Para fechas, mapas, datos, vocabulario y contenido evaluable: texto editable y verificado, nunca texto dentro de imágenes generadas.

### Implementación de comentarios

Reunir feedback, clasificarlo como accionable/ambiguo/manual/resuelto, presentar plan y obtener una sola aprobación. Ejecutar cambios aprobados en nueva versión; luego entregar preview y checklist manual. Contradicciones vuelven al usuario; comentarios claros se interpretan y ejecutan.

### Canva Connector opcional

Fuente original usa Canva MCP, cuenta Canva y a veces Enterprise. Esta skill sigue **local-first, permanente y sin Canva**. Usar Canva Connector solo si usuario lo pide, herramientas existen y usuario acepta autenticación/límites. Nunca afirmar que funciones MCP son offline, gratuitas o disponibles sin verificar.

## Referencias reutilizables

- `references/infografia-educativa-3d.md` — patrón probado para transformar apuntes o capturas en una infografía vertical de una página, con arte 3D sin texto, assets locales, captura exacta del lienzo y auditoría visual.
- `references/canva-agent-workflows.md` — flujos detallados adaptados del repositorio oficial para resize multicanal, bulk create, edición segura, feedback, brand check, traducción, presentaciones y ajuste temporal.

## Errores comunes

1. **Entregar solo PNG.** Sin fuente editable, no es alternativa permanente a Canva. Entregar SVG/HTML/PPTX además.
2. **Usar IA para texto.** Produce errores. Generar solo fondo/ilustración y montar texto localmente.
3. **Depender de CDN.** Diseño rompe offline. Usar recursos locales o fallback estable.
4. **Diseñar sin tamaño objetivo.** Composición falla al publicar. Definir lienzo primero.
5. **No mirar render.** Código válido puede verse mal. Capturar e inspeccionar.
6. **Forzar PDF/CMYK desde navegador.** Declarar límites y usar herramienta de preimpresión adecuada si imprenta exige CMYK exacto.
7. **Crear editor completo.** YAGNI. Fuente editable + revisiones por Hermes cubre uso normal con menos mantenimiento.

## Checklist final

- [ ] objetivo y público definidos
- [ ] texto exacto, sin datos inventados
- [ ] tamaño y zona segura correctos
- [ ] fuente maestra local editable
- [ ] sin servicio pago/trial obligatorio
- [ ] recursos locales o con licencia documentada
- [ ] preview renderizado e inspeccionado
- [ ] ortografía, contraste, alineación y recortes revisados
- [ ] exportación pedida creada y abierta
- [ ] fuente + exportaciones entregadas con rutas exactas
