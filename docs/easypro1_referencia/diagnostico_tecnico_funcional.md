# Diagnostico tecnico-funcional

## Estado actual de EasyPro_1
- Sistema funcional, simple y estable en salida documental.
- Arquitectura basada en Django monolitico con CRUDs clasicos.
- La salida documental depende de una plantilla Word real y de una conversion local a PDF.
- El sistema resuelve bien un flujo corto, pero no escala en modelo de dominio.

## Estado actual de EasyProNotarial-2
- Stack moderno:
  - Backend FastAPI + SQLAlchemy.
  - Frontend Next.js 15 + React 19.
  - Auth por JWT.
  - Versionado documental por caso.
  - Trazabilidad de timeline y workflow.
- El sistema ya modela:
  - casos,
  - plantillas,
  - personas,
  - entidades juridicas,
  - actos,
  - documentos versionados,
  - aprobaciones,
  - carga del final firmado.
- Todavia falta cerrar una escritura de compraventa como experiencia completamente integrada y sin huecos.

## Diagnostico comparativo
### EasyPro_1
- Ventaja principal: genera documentos correctos con una mecánica corta y comprobada.
- Debilidad principal: el dominio es manual, poco estructurado y no reutiliza bien entidades del negocio.

### EasyProNotarial-2
- Ventaja principal: tiene la estructura correcta para un sistema notarial escalable.
- Debilidad principal: la complejidad aun no se traduce en un flujo cerrado de compraventa con resultado final consistente.

## Lo que ya esta bien resuelto en EasyProNotarial-2
- Modelo de caso con secuencia interna y numero oficial de escritura.
- Catalogo de plantillas con roles y campos.
- Reutilizacion de personas.
- Reutilizacion de entidades juridicas y representantes.
- Versionado documental por caso.
- Aprobacion por roles notariales.
- Descarga de versiones y carga del firmado.
- Generacion asistida por IA con Gari.

## Lo que sigue incompleto para una compraventa de principio a fin
- Una sola experiencia guiada que conecte:
  - plantilla,
  - participantes,
  - datos del acto,
  - validacion,
  - borrador DOCX,
  - versionado,
  - aprobacion,
  - exportacion,
  - documento final firmado.
- Un preview documental claro para usuario final.
- Una validacion de compraventa que no dependa de correr por varias rutas.
- Un contrato semantico firme entre template, campos y datos capturados.

## Riesgos tecnicos
- Fragmentacion entre flujo clasico de plantilla y flujo Gari.
- Plantillas con campos requeridos no totalmente homogenizados.
- Dependencia de variables de entorno para OpenAI y Supabase.
- Posible divergencia entre el texto generado por IA y la estructura necesaria por notaria.
- PDF de exportacion que todavia no es la salida canonica fiel del DOCX en todos los casos.

## Riesgos funcionales
- Que la compraventa quede dividida entre varios modos de generar el borrador.
- Que la semantica de campos quede repartida entre `template_fields`, JSON libre y prompts.
- Que la trazabilidad documente el proceso, pero el usuario siga percibiendo pasos sueltos.

## Recomendacion tecnica
- Tomar EasyPro_1 como referencia de comportamiento de salida documental.
- Tomar EasyProNotarial-2 como base de arquitectura.
- No migrar CRUD viejo tal cual.
- En su lugar:
  - fijar una variante de compraventa,
  - cerrar el contrato de campos,
  - conectar participantes y entidades juridicas,
  - usar la plantilla real como base,
  - guardar versiones,
  - y luego sumar Gari como capa de redaccion.

## Recomendacion funcional
- El proximo sprint debe buscar solo una cosa:
  - una escritura de compraventa generada de principio a fin,
  - con un caso real o semilla,
  - con documento descargable,
  - con aprobacion,
  - y con cierre documental verificable.

## Siguiente sprint recomendado
1. Definir la variante de compraventa a cerrar primero.
2. Congelar los campos requeridos de esa variante.
3. Alinear plantilla, participantes y entidades juridicas.
4. Generar borrador DOCX desde la plantilla real.
5. Asegurar versionado y descarga.
6. Probar aprobacion y carga del firmado.
7. Recién despues, agregar preview y mejora de PDF.

## Nota tecnica del sprint DOCX
- Se corrigio el motor de reemplazo para trabajar sobre `python-docx` a nivel de parrafos y runs, en lugar de reescribir el XML completo.
- Esa decision preserva estilos, margenes, fuente y estructura original del Word.
- El relleno notarial `[[--]]` se convierte en un tab literal (`\t`), igual que en EasyPro_1.
- El lider de guiones no se fabrica por conteo de caracteres; debe existir en la plantilla como tab stop con leader de dashes.
- Queda pendiente evaluar si alguna plantilla antigua no trae ese tab stop configurado, porque ese caso no estaba confirmado en el muestreo actual.
