# Campos por tipo documental

## Lectura general
- En EasyPro_1, el campo documental real nace del placeholder `{{...}}` del DOCX y luego se guarda como `TemplateDetails` y `DocumentDetails`.
- En EasyProNotarial-2, el campo documental vive como `template_fields` y `case_act_data`.
- Este inventario separa:
  - campos del esquema,
  - campos obligatorios por tipo,
  - y campos estructurados por plantilla semilla.

## EasyPro_1
### Documento generico basado en plantilla
- Campos base del documento:
  - `client_name`
  - `title`
  - `template`
  - `status`
  - `comments`
- Campos dinamicos:
  - uno por cada etiqueta `{{ETIQUETA}}` detectada en el Word.
  - se guardan en `TemplateDetails` y luego en `DocumentDetails.value_field`.

### Protocolo
- `escritura`
- `ano`
- `archivo_pdf`

### Tabla maestra
- `table_name`
- `value`
- `status`

## EasyProNotarial-2

## Plantilla: `poder-general`
- `slug`: `poder-general`
- `document_type`: `Poder General`
- Roles requeridos:
  - `poderdante`
  - `apoderado`
- Campos requeridos:
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `aporte_superintendencia`
  - `fondo_notariado`
  - `consecutivos_hojas_papel_notarial`
  - `extension`
- Campos opcionales o de soporte:
  - `clase_cuantia_acto`

## Plantilla: `compraventa-vis`
- `slug`: `compraventa-vis`
- `document_type`: `Compraventa de Interes Social`
- Roles requeridos:
  - `comprador_1`
  - `comprador_2` opcional
  - `comprador_3` opcional
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
  - `apoderado_banco_libera`
  - `apoderado_banco_hipoteca` opcional

### Campos requeridos confirmados
- `proyecto`
- `tipo_inmueble`
- `banco_hipotecante` opcional segun variante
- `numero_apartamento`
- `matricula_inmobiliaria`
- `cedula_catastral`
- `linderos`
- `numero_piso` opcional
- `area_privada`
- `area_total` opcional
- `altura` opcional
- `coeficiente_copropiedad`
- `avaluo_catastral`
- `valor_venta`
- `valor_venta_letras`
- `cuota_inicial` opcional
- `cuota_inicial_letras` opcional
- `valor_hipoteca` opcional
- `valor_hipoteca_letras` opcional
- `origen_cuota_inicial` opcional
- `fecha_promesa_compraventa`
- `inmueble_sera_casa_habitacion`
- `tiene_bien_afectado`
- `paz_salvo_predial_numero`
- `paz_salvo_predial_fecha`
- `paz_salvo_predial_vigencia`
- `dia_elaboracion`
- `mes_elaboracion`
- `ano_elaboracion`

### Nota funcional
- El flujo actual ya acepta compraventa como plantilla estructurada, pero todavia falta cerrar una experiencia de usuario completa y unica para esa escritura.

## Plantilla: `aragua-parq-1c`
- `document_type`: `Compraventa VIS`
- Roles:
  - `comprador_1`
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
- Campos:
  - `numero_parqueadero`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `aragua-parq-2c`
- Roles:
  - `comprador_1`
  - `comprador_2` opcional
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
- Campos:
  - `numero_parqueadero`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `aragua-parq-3c`
- Roles:
  - `comprador_1`
  - `comprador_2` opcional
  - `comprador_3` opcional
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
- Campos:
  - `numero_parqueadero`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `torre6-contado`
- Roles:
  - `comprador_1`
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
- Campos:
  - `numero_apartamento`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `jaggua-bogota-1c`
- `document_type`: `Compraventa VIS + Hipoteca`
- Roles:
  - `comprador_1`
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
  - `apoderado_banco_hipoteca`
- Campos:
  - `numero_apartamento`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `valor_del_acto_hipoteca`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `jaggua-bogota-2c`
- Roles:
  - `comprador_1`
  - `comprador_2` opcional
  - `apoderado_banco_libera`
  - `apoderado_fideicomiso`
  - `apoderado_fideicomitente`
  - `apoderado_banco_hipoteca`
- Campos:
  - `numero_apartamento`
  - `numero_matricula`
  - `valor_de_la_venta`
  - `valor_del_acto_hipoteca`
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `correccion-registro-civil`
- Roles:
  - `inscrito`
- Campos:
  - `notaria_donde_inscrito`
  - `numero_libro`
  - `numero_folio`
  - `inconsistencias_a_corregir`
  - `numero_resolucion_notario` opcional
  - `fecha_resolucion_notario` opcional
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Plantilla: `salida-del-pais`
- Roles:
  - `otorgante`
  - `aceptante`
  - `menor`
- Campos:
  - `dia_elaboracion`
  - `mes_elaboracion`
  - `ano_elaboracion`
  - `derechos_notariales`
  - `iva`
  - `superintendencia`
  - `fondo_notariado`
  - `consecutivo_hojas` opcional

## Campos transversales confirmados en EasyProNotarial-2
- `Case`
  - `notary_id`
  - `template_id`
  - `case_type`
  - `act_type`
  - `consecutive`
  - `year`
  - `internal_case_number`
  - `official_deed_number`
  - `official_deed_year`
  - `current_state`
  - responsables por rol
  - `requires_client_review`
  - `final_signed_uploaded`
  - `metadata_json`
- `CaseParticipant`
  - `role_code`
  - `role_label`
  - `person_id`
  - `legal_entity_id` opcional
  - `snapshot_json`
- `CaseActData`
  - `data_json`
  - `gari_draft_text`

## Pendientes de verificacion
- Validar si todas las variantes de compraventa usan exactamente los mismos campos en produccion real o si existen ajustes por notaria.
- Validar si nuevas escrituras ya quedaron en seeds o solo en prompts/Gari.
