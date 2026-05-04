# Brechas EasyProNotarial-2 vs EasyPro_1

## Lectura ejecutiva
- EasyPro_1 resuelve un flujo documental simple y estable con plantillas Word reales.
- EasyProNotarial-2 ya tiene mejor arquitectura, mas dominio y mejor trazabilidad, pero todavia no cierra el flujo de escritura de principio a fin para una compraventa.
- La brecha principal no es tecnica aislada; es de ensamblaje funcional entre plantilla, datos estructurados, participantes, reglas notariales y salida final.

## Matriz comparativa

| Funcionalidad | Estado en EasyPro_1 | Estado en EasyProNotarial-2 | Brecha | Prioridad | Recomendacion |
|---|---|---|---|---|---|
| Plantilla DOCX real como fuente base | Sostenida por `Template.file_name` y una plantilla real funcional | Sostenida por seeds en `backend/storage/templates` y DB | Baja | Alta | Reutilizar el enfoque de plantilla real, pero con versionado y catalogo por caso |
| Extraccion de etiquetas desde Word | Automatizada con regex sobre `{{...}}` | Automatizada para plantillas cargadas con `extract_highlighted_fields_from_docx()` | Media | Alta | Mantener la extraccion automatica, pero no depender solo de placeholders; sumar mapa semantico |
| Definicion de campos por plantilla | Manual luego de cargar la plantilla | Estructurada en `template_fields` | Baja | Alta | Reutilizar el modelo estructurado; esta mejor resuelto en EasyProNotarial-2 |
| Documento como unidad principal | Si | No; el caso es la unidad principal | Alta | Alta | Mantener el caso como centro, pero exportar documentos versionados por caso |
| Trazabilidad de estado | Basica: registered/approved/rejected | Completa: timeline + workflow + estados | Baja | Alta | Reutilizar la trazabilidad de EasyProNotarial-2 |
| Aprobacion por roles | Basica | Completa por roles y reglas de aprobacion | Baja | Alta | Mantener el flujo por roles y endurecer transiciones por tipo de escritura |
| Generacion DOCX desde plantilla | Si, directa y estable | Si, por `generate-from-template` y `generate-draft` | Media | Alta | Consolidar un unico camino de generacion con validacion de campos obligatorios |
| Generacion PDF | Si, via LibreOffice | Si, pero el export PDF del MVP es plano y no siempre fiel al DOCX | Alta | Media | Rehacer export PDF fiel a partir del DOCX cuando el flujo base de compraventa ya cierre |
| Vista previa del documento | No hay preview embebido real; solo descarga/visualizacion externa | No hay preview embebido real; hay descarga de versiones | Media | Media | Agregar preview HTML/DOCX/PDF solo despues de estabilizar el borrador |
| Reutilizacion de personas | No existe catalogo fuerte; todo es por documento | Si, con `persons` y lookup reutilizable | Baja | Alta | Reutilizar y ampliar el catalogo de personas |
| Reutilizacion de entidades juridicas y apoderados | No existe | Si, con `legal_entities` y representantes | Baja | Alta | Reutilizar; es clave para bancos, fiducias y constructoras |
| Reutilizacion de actos | No existe catalogo de actos | Si, con `act_catalog` y `case_acts` | Baja | Alta | Reutilizar el catalogo y convertirlo en motor de secuencias documentales |
| Reutilizacion de bancos / poderes / inmuebles | No existe | Parcialmente modelado y semantizado en seeds y prompts | Media | Alta | Amarrar estas entidades al flujo de compraventa, no solo al prompt |
| Generacion inteligente con IA | No existe | Si, con Gari | Media | Media | Usarla como apoyo de redaccion, no como unico motor del flujo |
| Reglas notariales implícitas codificadas | Muy pocas | Bastantes en prompt, seeds y validaciones | Media | Alta | Convertirlas gradualmente en reglas explicitas de dominio |
| Versionado documental | No existe como versionado fuerte | Si, con `case_document_versions` | Baja | Alta | Reutilizar el versionado de EasyProNotarial-2 |
| Secuencias notariales | Solo `Protocolo` por escritura/ano | Secuencia interna + escritura oficial | Alta | Alta | Mantener y consolidar secuencias por notaria y ano |
| Flujo de carga del documento final firmado | Registro simple de PDF | Carga base64 de archivo final | Media | Media | Mantener en EasyProNotarial-2 y agregar verificacion final de cierre |

## Brechas funcionales criticas para una compraventa completa
1. La compraventa no esta cerrada de punta a punta como flujo unico.
2. Faltan reglas de composicion de comparecientes, inmueble, hipoteca, fiducia y banco dentro de una sola ruta funcional.
3. El documento final sigue dependiendo de ramas de exportacion y no de una experiencia cerrada con validaciones claras.
4. La version AI/Gari existe, pero debe convertirse en apoyo de redaccion para una plantilla/flujo ya validado.
5. El preview sigue pendiente como experiencia de usuario, aunque no es bloqueante para el primer cierre funcional.

## Brechas por area
### Datos maestros
- EasyPro_1 no tiene reutilizacion robusta de personas, bancos, entidades o poderes.
- EasyProNotarial-2 ya los modela, pero falta conectar esos modelos con el flujo de compraventa.

### Plantillas
- EasyPro_1 depende de una plantilla Word concreta y de su mapeo manual.
- EasyProNotarial-2 tiene catalogo de plantillas, roles requeridos y campos, pero todavia falta homologar el flujo de una escritura comercial completa.

### Documentos
- EasyPro_1 genera un documento y lo convierte.
- EasyProNotarial-2 versiona, aprueba, exporta y guarda, pero no todos los caminos estan unificados.

### Trazabilidad
- EasyPro_1 registra poco.
- EasyProNotarial-2 ya tiene timeline y workflow, lo que conviene conservar como sistema de verdad operativa.

## Recomendacion por componente
- Reutilizar de EasyPro_1:
  - Reemplazo DOCX directo por placeholders.
  - Limpieza simple del flujo plantilla -> documento.
- Tomar solo como referencia:
  - Estructura de aprobacion basica.
  - Uso de LibreOffice para PDF cuando el objetivo sea salida rapida.
- Descatar como base de arquitectura:
  - Modelo centrado en `Document` sin expediente/caso.
  - Dependencia de edicion manual de cada campo sin semantica de dominio.
- Rehacer mejor en EasyProNotarial-2:
  - Flujo completo de compraventa.
  - Reglas de participantes por acto.
  - Consolidacion de salida DOCX/PDF/firmado en un solo historial versionado.

## Conclusion de brecha
- EasyPro_1 gana en simplicidad funcional.
- EasyProNotarial-2 gana en estructura y extensibilidad.
- La migracion correcta no es copiar el CRUD viejo, sino usarlo como referencia de salida documental mientras se consolida el dominio estructurado del sistema nuevo.
