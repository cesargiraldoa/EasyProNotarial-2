# Motor Biblioteca — Spike Tecnico

Plugin aislado para validar capacidades reales de ONLYOFFICE antes de habilitar
mutaciones del Motor de Biblioteca 2.0.0.

## Alcance

- No usa JWT.
- No usa backend.
- No consulta catalogo.
- No toca el plugin productivo `biblioteca`.
- Solo debe ejecutarse sobre un DOCX temporal y anonimizado.

## Documento de prueba

Crear o abrir una copia temporal y escribir exactamente una vez:

```text
EASYPRO_SPIKE_RANGE_2026
```

El plugin rechaza cero coincidencias y multiples coincidencias.

## Tag validado

```text
easypro:spike:v1:EASYPRO_SPIKE_RANGE_2026
```

## Flujo manual

1. Detectar capacidades.
2. Localizar rango.
3. Seleccionar rango.
4. Aplicar highlight.
5. Retirar highlight.
6. Crear Content Control.
7. Leer Content Controls.
8. Actualizar contenido.
9. Restaurar contenido.
10. Guardar, cerrar y reabrir el documento.
11. Verificar persistencia despues de reapertura.
12. Copiar informe tecnico.

## Seguridad

El spike no usa `SetColor`, no usa `ReplaceAllText`, no usa backend y no registra
datos personales. La accion de limpieza solo intenta eliminar Content Controls con
el prefijo `easypro:spike:v1`.
