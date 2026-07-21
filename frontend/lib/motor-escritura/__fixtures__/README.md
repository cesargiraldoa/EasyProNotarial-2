# Golden fixtures — motor-escritura

Salida de referencia (ground truth) capturada del **HTML congelado** `docs/ecosistema-notarial/prototipos/escritura-asistida.html` para los 3 actos, con sus **datos de muestra por defecto** (los que trae el HTML al elegir cada acto en el lanzador). El motor portado a TypeScript (WP-2) debe reproducir estos fixtures.

## Archivos
`compraventa.json`, `hipoteca.json`, `cancelacion.json`. Cada uno:
- `doc_text` — texto normalizado de la escritura (`#escritura`).
- `liquidacion_text` — texto normalizado de la liquidación.
- `estado` — barra de estado (con/sin bloqueantes).
- `cumplimiento_tiles` — `["8:Cumple","2:Advertencia","0:Bloqueante"]`.
- `cumplimiento_items` — lista de títulos de las verificaciones (orden del render).

## Caso canónico (input)
Para cada acto, el input es el **estado por defecto del formulario del HTML** al pulsar su tarjeta en el lanzador (`.lz-card[data-acto="…"]`):
- **compraventa** → `credito=false` (los `data.vendedores/compradores`, inmueble, precio 420M/120M/300M por defecto).
- **hipoteca** → `credito=true` (mismos datos + sección de hipoteca).
- **cancelacion** → los valores por defecto de `Gc()` (Bancolombia, apoderada Paulina, deudora Angélica, E.P. 1.858, etc.).

El motor en TS debe exponer estos mismos defaults como fixtures de entrada (extraerlos del HTML, que es la spec).

## Normalización (DETERMINISTA — replicar idéntica en el test TS)
La salida del motor es un **string HTML** (como en el HTML). Para comparar contra `doc_text`/`liquidacion_text`, aplicar exactamente esta función sobre ese string:

```js
function normalize(html){
  return html
    .replace(/<span class="fill"[^>]*>[\s\S]*?<\/span>/g,'')      // quita guiones de relleno (dependen del layout)
    .replace(/<\/(p|div|tr|h4|h3|li)>/g,'\n')                      // salto por bloque
    .replace(/<br\s*\/?>/g,'\n')
    .replace(/<[^>]+>/g,'')                                        // strip de tags
    .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>')
    .replace(/&quot;/g,'"').replace(/&#(\d+);/g,(m,n)=>String.fromCharCode(+n)).replace(/&nbsp;/g,' ')
    .replace(/—{2,}/g,'')                                          // guiones remanentes
    .split('\n').map(l=>l.replace(/[ \t]+/g,' ').trim()).filter(Boolean).join('\n');
}
```

> Los **guiones de relleno** (`.fill`) se excluyen a propósito: su ancho depende del layout del navegador y no son deterministas. El motor puede seguir generándolos para el render real; el golden test los ignora.

## Regenerar (solo si cambia el HTML congelado — no debería)
Se capturan con Playwright abriendo el HTML, pulsando cada tarjeta y serializando `#escritura`/`#liquidacion`/`#cumplimiento`/`#estado`. El script vive en el historial de la sesión; si se necesita, pedirlo.
