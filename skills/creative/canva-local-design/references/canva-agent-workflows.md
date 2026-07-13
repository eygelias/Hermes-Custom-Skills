# Capacidades adaptadas de Canva Agent Skills

## Procedencia y licencia

Adaptación local de conceptos y flujos del repositorio oficial:

- Fuente: https://github.com/canva-sdks/canva-skills
- Clon local inspeccionado: `C:\Users\ELY\Desktop\COSAS\canva-skills`
- Revisión integrada: commit `b56291ea0a36d0a941e1478b47959be5f1771dee`
- Licencia fuente: Apache License 2.0
- Archivos fuente: `plugins/canva/skills/*/SKILL.md` y `plugins/canva/inactive-skills/*/SKILL.md`

Contenido fue adaptado: operaciones Canva MCP se sustituyen por archivos locales SVG/HTML/PPTX, datos estructurados, versionado y renderizado en navegador. No implica afiliación con Canva ni acceso automático a Canva.

## Matriz de capacidades

| Flujo fuente | Capacidad local incorporada | Salida |
|---|---|---|
| `resize-for-social-media` | adaptar una fuente maestra a varios formatos, remaquetando en vez de estirar | SVG/HTML + PNG por formato |
| `bulk-create` | crear una variante por fila desde CSV/TSV/JSON/tabla y plantilla local | diseños + reporte CSV |
| `edit-design` | edición segura por versión, operaciones agrupadas, preview y aprobación cuando corresponda | nueva versión editable |
| `get-design-feedback` | crítica visual priorizada por página y severidad | informe accionable |
| `brand-check` | comprobar color, tipografía, logo, voz y consistencia | On brand / Off brand / No verificable |
| `implement-feedback` | reunir comentarios, clasificar, aprobar plan una vez, ejecutar y reportar pendientes | versión corregida + checklist |
| `design-translation` | traducir copia conservando original, formato y términos protegidos | variante por idioma |
| `branded-presentation` | convertir brief en deck con arco narrativo y plan visual | PPTX o HTML deck |
| `classroom-helper` | convertir plan de clase en presentación pedagógica | deck docente + notas |
| `presentation-time-fitting` | ajustar notas del presentador a duración y ritmo objetivo | notas por diapositiva |

## 1. Redimensionado multicanal

1. Identificar fuente maestra y relación original.
2. Elegir destinos. Defaults heredados del flujo fuente:
   - Facebook post: 1200×630
   - Facebook story: 1080×1920
   - Instagram post: 1080×1080
   - Instagram story: 1080×1920
   - LinkedIn post: 1200×627
3. Crear un archivo fuente por relación; Facebook/Instagram story pueden compartir composición si contenido es idéntico.
4. **Remaquetar**, no escalar ciegamente:
   - recolocar título, imagen, CTA y logo
   - mantener zonas seguras
   - recortar imagen con `object-fit: cover` o SVG `preserveAspectRatio`
   - reducir texto antes de volverlo ilegible
5. Renderizar y revisar cada formato independientemente.
6. Continuar si un formato falla y reportar éxito/error por destino.

## 2. Creación masiva desde datos

Entradas: CSV, TSV, Excel extraído, tabla Markdown, JSON o URL con datos tabulares.

Flujo:

1. Parsear encabezados y filas.
2. Mostrar cantidad, columnas y primeras 3 filas.
3. Inspeccionar placeholders de plantilla local, por ejemplo `{{PRODUCTO}}`, `{{PRECIO}}`, `{{IMAGEN}}`.
4. Proponer mapeo por coincidencia exacta y luego fuzzy, sin distinguir mayúsculas.
5. Confirmar campos ambiguos/no mapeados antes de lote grande.
6. Generar secuencialmente para localizar fallos y evitar picos de recursos.
7. Para imágenes URL, descargarlas a `assets/` con nombre estable y registrar origen/licencia; nunca depender del URL final.
8. Omitir filas donde todos los campos mapeados estén vacíos.
9. En 50+ filas, ejecutar prueba de 3 primero salvo usuario ordene lote completo.
10. Crear `results.csv`: `row,status,source,output,error`.

No requiere Canva Enterprise: usa plantillas locales y herramientas estándar ya disponibles.

## 3. Edición segura

Modelo local equivalente a transacción:

1. Resolver archivo exacto.
2. Copiar fuente a nueva versión antes de cambios grandes, traducción o lote.
3. Inspeccionar fuente y preview actuales.
4. Convertir pedido en lista concreta de operaciones.
5. Agrupar operaciones relacionadas en una sola edición.
6. Renderizar preview nuevo.
7. Mostrar cambios y pedir aprobación antes de sobrescribir original o realizar cambios destructivos. Si trabajo ya ocurre en una nueva versión no destructiva y pedido fue explícito, entregar nueva versión sin confirmación adicional.
8. Conservar o borrar borrador según decisión del usuario.

Operaciones locales admitidas superan API Canva: texto nuevo, familias tipográficas locales, fondos, páginas, formas, opacidad, agrupación, animación HTML y reordenado. Capacidad real depende del formato fuente; no prometer edición limpia de binarios/raster sin fuente editable.

## 4. Feedback de diseño

Inspeccionar render real y contenido. Evaluar:

- jerarquía visual
- layout, alineación, márgenes y espaciado
- claridad, longitud y ortografía
- consistencia entre páginas
- legibilidad y contraste
- accesibilidad: contraste, alt text, significado no dependiente solo de color
- adecuación a canal, audiencia y distancia de lectura

Formato:

```text
Top priorities
1. [High] Página/elemento — problema concreto. Fix: acción concreta.

Page-by-page
Página 1 — [Med] ...

What's working
- ...
```

Reglas: hallazgos observados, ubicación exacta, severidad High/Med/Low y reparación accionable. Crítica separada de edición; editar solo si usuario lo pidió.

## 5. Brand check

Fuentes válidas: guía de marca, DESIGN.md, logo, paleta, fuentes locales, ejemplos aprobados o datos entregados por usuario.

Marcar cada dimensión:

- `On brand`
- `Off brand`
- `No verificable`

Revisar color, tipografía, logo, tono/copy y consistencia. Nunca inventar hex, fuente ni margen de seguridad. Si solo existe captura, resultados de color/tipografía son aproximados. Comparar valor observado contra regla real y proponer sustitución.

## 6. Implementación de feedback

1. Reunir comentarios desde documento, lista, captura o texto del usuario.
2. Clasificar:
   - accionable
   - ambiguo/contradictorio
   - requiere material o acción manual
   - resuelto/positivo
3. Presentar plan completo y obtener una aprobación.
4. Aplicar cambios claros en lote y producir preview.
5. No pedir segunda aprobación para guardar una **nueva versión** cubierta por plan aprobado.
6. Entregar checklist manual con página, cambio, autor si consta, motivo y pasos.
7. Mantener comentarios sin inventar intención; contradicciones sí vuelven al usuario.

## 7. Traducción/localización

1. Siempre trabajar en copia por idioma.
2. Extraer todo texto visible, alt text y notas si aplican.
3. Traducir conservando saltos, énfasis, nombres propios, marcas y términos técnicos.
4. Reemplazar en lote.
5. Recalcular cajas: traducciones cambian longitud.
6. Revisar overflow, guiones, dirección, puntuación y fuentes con glifos completos.
7. Renderizar todas las páginas y aprobar variante antes de reemplazar cualquier versión publicada.

## 8. Presentaciones de marca

Estructura del brief:

- título, tema, alcance
- 3–5 mensajes principales
- tono e imágenes
- audiencia y CTA
- arco narrativo: Hook → Problem → Solution → Proof → CTA, adaptado al caso

Por diapositiva:

- título exacto y orientado a acción
- objetivo de diapositiva
- 3–6 bullets paralelos
- recomendación visual concreta
- 2–4 frases de notas

Usar `powerpoint` cuando salida necesita edición en PowerPoint/WPS/LibreOffice. Usar HTML fijo 1920×1080 solo cuando deck web es aceptable.

## 9. Presentación educativa

Convertir plan docente en deck multipágina. Conservar objetivos y secuencia del autor.

Incluir cuando exista:

- asignatura, unidad, grado, duración
- objetivos verbatim
- estándares solo si fuente los trae
- arco de clase: Engage/Explore/Explain/Elaborate/Evaluate o I Do/We Do/You Do
- una idea principal por slide
- preguntas, práctica, evaluación y cierre
- materiales, seguridad, diferenciación y extensiones
- notas docentes con timing, errores frecuentes y checks de comprensión

Imágenes educativas automáticas son borradores. Fechas, mapas, datos, vocabulario y texto evaluable deben estar como texto editable y verificarse humanamente; nunca dentro de imagen generada.

## 10. Ajuste a duración

1. Obtener duración total y número de slides.
2. Default: reparto igual, salvo apertura/cierre o peso solicitado.
3. Calcular segundos por slide.
4. Presupuesto guía: `palabras ≈ minutos × 150`; ritmo no es garantía.
5. Escribir/recortar **notas**, sin cambiar texto visible salvo pedido separado.
6. No inventar hechos; expandir con contexto, transiciones y señales de entrega.
7. Entregar tabla de tiempos y notas agrupadas por slide.
8. Si objetivo es irreal, señalarlo y proponer dividir/simplificar.

## Canva Connector opcional

Repositorio fuente depende de `https://mcp.canva.com/mcp`, inicio de sesión Canva y herramientas del conector. Algunas funciones, especialmente autofill, pueden requerir Canva Enterprise.

`canva-local-design` permanece **local-first**. Solo usar Canva Connector si:

- usuario lo pide explícitamente
- herramientas Canva están realmente disponibles
- usuario acepta iniciar sesión y posibles límites de plan

Nunca presentar capacidad MCP como gratuita, permanente u offline. Sin conector, aplicar flujos adaptados arriba con archivos locales.

## Verificación ampliada

- Cada variante conserva fuente editable.
- Todos los formatos/páginas fueron renderizados.
- Lotes tienen conteo esperado y reporte de fallos.
- Traducción no desborda cajas.
- Brand check distingue hechos de aproximaciones.
- Feedback aplicado coincide con plan aprobado.
- Notas respetan duración aproximada.
- Original permanece intacto en traducciones, lotes y cambios grandes.
