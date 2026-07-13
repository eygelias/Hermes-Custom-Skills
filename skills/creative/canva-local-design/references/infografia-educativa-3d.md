# Infografía educativa 3D en una página

Patrón reutilizable para convertir apuntes o una captura en una pieza vertical editable y exportable.

## Ruta recomendada

1. **Extraer contenido visualmente**
   - Leer imagen fuente con visión.
   - Separar título, introducción, conceptos y ejemplos.
   - Conservar redacción y datos; reestructurar solo jerarquía visual.

2. **Elegir lienzo**
   - Default social vertical: 1080×1350 px.
   - Una sola página, sin scroll ni contenido fuera del lienzo.

3. **Generar arte sin texto**
   - Pedir ilustración 3D/clay con objetos temáticos, bordes redondeados, composición compacta y fondo limpio.
   - Prohibir letras, números, palabras, marcas de agua y bordes.
   - Componer todo texto después en SVG/HTML para evitar errores ortográficos.

4. **Localizar recursos**
   - Descargar inmediatamente resultado generado a `source/assets/`; no depender de URL remota.
   - Referenciar mediante ruta relativa desde fuente maestra.

5. **Componer**
   - Usar HTML/CSS o SVG local.
   - Combinar ilustración principal 3D con tarjetas redondeadas, sombras sólidas y jerarquía tipográfica.
   - Para dos conceptos, funciona bien: cabecera con arte + introducción + dos tarjetas verticales.
   - Los intervalos o pasos pueden convertirse en una línea visual de chips, manteniendo explicación completa debajo.

6. **Renderizar exactamente**
   - Abrir fuente en navegador.
   - Capturar el nodo del lienzo, no ventana completa; así exportación conserva dimensiones exactas.
   - Guardar primera captura en `previews/` y final en `exports/`.

7. **Auditar render, no solo código**
   - Inspeccionar preview con visión.
   - Revisar recortes, solapes, legibilidad, jerarquía, márgenes, ortografía, equilibrio, resolución y cumplimiento del estilo.
   - Corregir y volver a renderizar si aparece cualquier defecto importante.

8. **Verificar entrega**
   - Confirmar dimensiones PNG desde archivo.
   - Confirmar HTML/SVG existente y no vacío.
   - Entregar PNG visible y ruta de fuente editable.

## Prompt base para arte

```text
Polished 3D clay-style educational illustration about {{TEMA}}. Include {{OBJETOS}}. Soft premium clay render, rounded edges everywhere, tactile matte materials, cohesive limited palette, soft studio lighting, gentle shadows, clean background, balanced compact composition, modern educational aesthetic, no people unless requested, no letters, no numbers, no words, no typography, no watermark, no border.
```

## Pitfalls

- No generar infografía completa con `image_generate`: texto puede salir corrupto.
- No dejar URL remota como asset final: puede caducar.
- No entregar solo PNG: conservar HTML/SVG editable.
- No usar screenshot de ventana si se requiere tamaño exacto: capturar nodo raíz del lienzo.
- No aprobar diseño sin mirar preview renderizado.