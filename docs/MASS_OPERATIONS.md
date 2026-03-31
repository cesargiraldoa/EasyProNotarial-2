# Dise?o previsto para operaciones masivas

## Objetivo
Dejar la arquitectura lista para soportar cargas de proyectos residenciales con m?ltiples escrituras y trazabilidad individual por registro.

## Capacidades contempladas
- Carga masiva de datos desde archivos estructurados.
- Creaci?n masiva de casos a partir de una configuraci?n de lote.
- Generaci?n masiva de documentos con reutilizaci?n de plantillas.
- Estado individual por caso dentro del lote.
- Registro de errores por fila o expediente.
- Reintentos parciales sin reprocesar lotes completos.

## Dise?o recomendado para Paquete 2
### Nuevos agregados
- `Batch`: definici?n del lote.
- `BatchItem`: fila/caso individual dentro del lote.
- `BatchTemplateBinding`: v?nculo entre lote y configuraci?n documental.
- `BatchExecution`: corridas de generaci?n, validaci?n o exportaci?n.
- `BatchError`: errores normalizados por registro y etapa.

### Estados sugeridos
- draft
- validating
- ready
- processing
- completed
- completed_with_errors
- failed
- cancelled

### Consideraciones t?cnicas
- Separar ingesti?n, validaci?n y generaci?n en servicios distintos.
- Mantener trazabilidad por `batch_id` y `batch_item_id`.
- Versionar reglas y plantillas aplicadas a cada lote.
- Dise?ar procesamiento as?ncrono desde el inicio.
- Registrar m?tricas por throughput, errores y tiempos por etapa.
