// Diccionario de normas para los popups de la escritura asistida.
// Portado 1:1 del prototipo congelado `docs/ecosistema-notarial/prototipos/escritura-asistida.html`
// (bloque `var NORMAS = {...}`). Es texto de REFERENCIA — validar siempre contra fuente oficial.
// La clave es el texto exacto del badge de cita (`.cite`) que emite el motor.

export type NormaTip = {
  norma: string;
  estado?: string;
  art: string;
  texto: string;
  fuente?: string;
};

export const NORMAS: Record<string, NormaTip> = {
  "art. 6 · Ley 258/1996": {
    norma: "Ley 258/1996 (mod. Ley 854/2003)",
    estado: "Vigente",
    art: "Artículo 6 — Deber del notario",
    texto:
      "En toda escritura de enajenación o gravamen de un inmueble destinado a vivienda, el Notario indagará al propietario si tiene sociedad conyugal, matrimonio o unión marital de hecho vigente y si el inmueble se encuentra afectado a vivienda familiar. La respuesta se dará bajo la gravedad del juramento y se dejará constancia en la escritura.",
    fuente: "Gestor Normativo i=10794",
  },
  "art. 3 · Ley 258/1996": {
    norma: "Ley 258/1996",
    estado: "Vigente",
    art: "Artículo 3 — Consentimiento de ambos",
    texto:
      "Los inmuebles afectados a vivienda familiar solo podrán enajenarse, gravarse o constituir sobre ellos derecho real, con el consentimiento libre de ambos cónyuges, expresado con su firma. La falta de este requisito genera la nulidad del acto.",
    fuente: "Gestor Normativo i=10794",
  },
  "art. 90 E.T.": {
    norma: "Estatuto Tributario (mod. art. 61 Ley 2010/2019)",
    estado: "Vigente",
    art: "Artículo 90 — Declaración de valor real",
    texto:
      "En la escritura de enajenación las partes declararán, bajo la gravedad del juramento, que el precio incluido es real y no ha sido objeto de pactos privados con valor diferente; de existir, deberán informar el precio convenido. Si se omite esta declaración, la renta, la ganancia ocasional, el impuesto de registro y los derechos notariales se liquidan sobre una base de cuatro (4) veces el valor incluido en la escritura.",
    fuente: "Senado — E.T.; Gestor i=159687",
  },
  "art. 61 Ley 2010/2019 (art. 90 E.T.)": {
    norma: "Estatuto Tributario (mod. art. 61 Ley 2010/2019)",
    estado: "Vigente",
    art: "Artículo 90 — Declaración de valor real",
    texto:
      "En la escritura de enajenación las partes declararán, bajo la gravedad del juramento, que el precio incluido es real y no ha sido objeto de pactos privados con valor diferente; de existir, deberán informar el precio convenido. Si se omite esta declaración, la renta, la ganancia ocasional, el impuesto de registro y los derechos notariales se liquidan sobre una base de cuatro (4) veces el valor incluido en la escritura.",
    fuente: "Senado — E.T.; Gestor i=159687",
  },
  "art. 398 E.T.": {
    norma: "Estatuto Tributario",
    estado: "Vigente",
    art: "Artículo 398 — Retención en la fuente",
    texto:
      "La enajenación de activos fijos de una persona natural está sometida a una retención en la fuente del uno por ciento (1%) del valor de la enajenación. Tratándose de bienes inmuebles, la retención se efectúa ante el notario, que actúa como agente retenedor y debe recaudarla previamente a la enajenación.",
    fuente: "DIAN — E.T.; Oficios 4860 y 6547 de 2019",
  },
  "art. 29 · Ley 675/2001": {
    norma: "Ley 675/2001 (mod. Ley 2079/2021)",
    estado: "Vigente",
    art: "Artículo 29 — Expensas y paz y salvo",
    texto:
      "Cada propietario participa en las expensas comunes según su coeficiente. En la transferencia del dominio, el Notario exige el paz y salvo de expensas comunes expedido por el representante legal de la copropiedad; de no obtenerse, se deja constancia en la escritura y el nuevo propietario responde solidariamente por las deudas pendientes.",
    fuente: "Gestor i=4162",
  },
  "arts. 25–26 · Ley 675/2001": {
    norma: "Ley 675/2001",
    estado: "Vigente",
    art: "Artículos 25 y 26 — Coeficientes",
    texto:
      "Art. 25. El reglamento señalará los coeficientes de copropiedad de los bienes de dominio particular.\nArt. 26. Los coeficientes se calcularán con base en el área privada construida de cada bien respecto del área privada construida total del edificio o conjunto.",
    fuente: "Gestor i=4162",
  },
  "Ley 675/2001": {
    norma: "Ley 675 de 2001 — Propiedad horizontal",
    estado: "Vigente (mod. 2079/2021)",
    art: "Régimen de propiedad horizontal",
    texto:
      "Regula la propiedad horizontal: bienes privados y comunes, coeficientes de copropiedad, administración y expensas. El derecho sobre los bienes comunes es inseparable del bien privado y se transfiere con él.",
    fuente: "Gestor i=4162",
  },
  "art. 13 · Ley 2079/2021": {
    norma: "Ley 2079 de 2021 — Vivienda y hábitat",
    estado: "Vigente",
    art: "Artículo 13 — Restricción VIS",
    texto:
      "La vivienda de interés social adquirida con subsidio familiar de vivienda 100% en especie (SFVE) no puede transferirse durante cinco (5) años contados desde la transferencia del dominio, salvo autorización de la entidad otorgante; el subsidio es restituible si el beneficiario transfiere derechos reales o deja de residir antes del término. Se elimina la restricción para las demás modalidades (antes eran 10 años).",
    fuente: "Gestor i=160946; Minvivienda ER0015805/2021",
  },
  "art. 230 Ley 223/1995": {
    norma: "Ley 223 de 1995 — Impuesto de registro",
    estado: "Vigente",
    art: "Artículo 230 — Tarifas",
    texto:
      "Las asambleas departamentales fijan las tarifas del impuesto de registro. Para actos con cuantía sujetos a registro en las oficinas de registro de instrumentos públicos, la tarifa está entre el 0,5% y el 1% (1% en Antioquia). La base no puede ser inferior al avalúo catastral o autoavalúo.",
    fuente: "Gestor i=6968",
  },
  "art. 16 · Ley 1579/2012": {
    norma: "Ley 1579 de 2012 — Estatuto de Registro",
    estado: "Vigente",
    art: "Artículo 16 — Calificación",
    texto:
      "La calificación es el análisis jurídico y la verificación de que el título reúne los requisitos legales para su inscripción. No procede el registro si el inmueble no está plenamente identificado (matrícula, nomenclatura, linderos y área en sistema métrico) y las partes por su documento de identidad; en tal caso se inadmite mediante nota de devolución.",
    fuente: "Gestor i=49731",
  },
  "art. 8 · Ley 1579/2012": {
    norma: "Ley 1579 de 2012 — Estatuto de Registro",
    estado: "Vigente",
    art: "Artículo 8 — Matrícula inmobiliaria",
    texto:
      "La matrícula inmobiliaria es un folio destinado a la inscripción de los actos referentes a un bien inmueble, distinguido con un código alfanumérico. Señala la oficina de registro, el departamento y el municipio, el número predial o cédula catastral, si el inmueble es urbano o rural, y lo describe por su número o dirección, sus linderos, perímetro y cabida.",
    fuente: "Gestor i=49731",
  },
  "Ley 1579/2012": {
    norma: "Ley 1579 de 2012 — Estatuto de Registro",
    estado: "Vigente",
    art: "Registro de instrumentos públicos",
    texto:
      "Regula el registro de los documentos que afectan bienes inmuebles: radicación, calificación, inscripción, matrícula, títulos sujetos a registro y causales de devolución.",
    fuente: "Gestor i=49731",
  },
  "Ley 70/1931 · 495/1999": {
    norma: "Ley 70 de 1931 y Ley 495 de 1999",
    estado: "Vigente",
    art: "Patrimonio de familia inembargable",
    texto:
      "La Ley 495 de 1999 permite constituir el patrimonio de familia por escritura pública (tope 250 SMLMV; dominio pleno, sin proindiviso ni hipoteca). Se cancela de la misma forma en que se constituyó: por escritura con ambos cónyuges o judicialmente; con menores, autorización judicial. Mientras exista, el inmueble no puede venderse libremente.",
    fuente: "Gestor i=39265, i=38938",
  },
  "art. 1546 C.C.": {
    norma: "Código Civil",
    estado: "Vigente",
    art: "Artículo 1546 — Condición resolutoria tácita",
    texto:
      "En los contratos bilaterales va envuelta la condición resolutoria en caso de no cumplirse por uno de los contratantes lo pactado. En tal caso, el otro contratante podrá pedir a su arbitrio la resolución o el cumplimiento del contrato, con indemnización de perjuicios.",
    fuente: "Código Civil",
  },
  "arts. 1893, 1914 C.C.": {
    norma: "Código Civil — Saneamiento",
    estado: "Vigente",
    art: "Artículos 1893 y 1914",
    texto:
      "Art. 1893. El vendedor está obligado a sanear al comprador todas las evicciones que tengan una causa anterior a la venta.\nArt. 1914. La acción redhibitoria permite al comprador rescindir la venta o rebajar el precio por los vicios ocultos de la cosa vendida.",
    fuente: "Código Civil",
  },
  "arts. 2445–2446 C.C.": {
    norma: "Código Civil — Hipoteca",
    estado: "Vigente",
    art: "Artículos 2445 y 2446 — Extensión",
    texto:
      "Art. 2445. La hipoteca sobre bienes raíces afecta los muebles que por accesión se reputan inmuebles.\nArt. 2446. La hipoteca se extiende a todos los aumentos y mejoras que reciba la cosa hipotecada.",
    fuente: "Código Civil",
  },
  "Dcto 960/1970": {
    norma: "Decreto-Ley 960 de 1970 — Estatuto del Notariado",
    estado: "Vigente (mod.)",
    art: "Artículo 13 — Otorgamiento",
    texto:
      "La escritura pública se perfecciona en cuatro fases: recepción (el notario percibe las declaraciones), extensión (versión escrita del instrumento), otorgamiento (asentimiento expreso de los comparecientes) y autorización (fe que imprime el notario verificados los requisitos legales).",
    fuente: "Gestor i=149249",
  },
  "Dcto 1069/2015": {
    norma: "Decreto 1069 de 2015 — DUR Sector Justicia",
    estado: "Vigente",
    art: "Reglamentación notarial (ex Dcto 2148/1983)",
    texto:
      "Compila la reglamentación notarial: protocolización de documentos habilitantes, requisitos de los poderes y la identificación del inmueble en los poderes especiales para enajenar. Sustituye como norma vigente al Decreto 2148 de 1983.",
    fuente: "Gestor i=74174",
  },
  "C. Comercio": {
    norma: "Código de Comercio",
    estado: "Vigente",
    art: "Representación de personas jurídicas",
    texto:
      "La sociedad comparece por su representante legal, cuya calidad y facultades constan en el certificado de existencia y representación de la Cámara de Comercio. Cuando los estatutos o la cuantía del acto lo exijan, se requiere autorización del órgano social competente (junta o asamblea), que se protocoliza con la escritura.",
    fuente: "Código de Comercio",
  },
  "art. 1939 C.C.": {
    norma: "Código Civil",
    estado: "Vigente",
    art: "Artículo 1939 — Pacto de retroventa",
    texto:
      "Por el pacto de retroventa el vendedor se reserva la facultad de recobrar la cosa vendida reembolsando al comprador el precio; el plazo no puede pasar de cuatro (4) años. Se inscribe para su oponibilidad frente a terceros.",
    fuente: "Código Civil",
  },
  "art. 1935 C.C.": {
    norma: "Código Civil",
    estado: "Vigente",
    art: "Reserva de dominio",
    texto:
      "La reserva de dominio subordina la transferencia del dominio al pago del precio. En bienes inmuebles su eficacia es discutida y la doctrina la asimila a una condición resolutoria por incumplimiento (el registro transfiere el dominio). Validar en cada caso.",
    fuente: "Código Civil",
  },
  "art. 313 E.T.": {
    norma: "Estatuto Tributario (mod. Ley 2277/2022)",
    estado: "Vigente",
    art: "Ganancia ocasional",
    texto:
      "La utilidad en la venta de un activo fijo poseído dos (2) años o más se grava como ganancia ocasional a la tarifa del quince por ciento (15%). Si la posesión es inferior a dos años, la utilidad tributa como renta ordinaria. La venta de la casa de habitación tiene exención hasta 5.000 UVT (art. 311-1).",
    fuente: "E.T. arts. 300, 311-1, 313",
  },
  "Ley 3ª/1991": {
    norma: "Ley 3 de 1991 y Decreto 1077/2015",
    estado: "Vigente",
    art: "Subsidio familiar de vivienda",
    texto:
      "El subsidio familiar de vivienda se acredita con el acto de asignación de la entidad otorgante (Fonvivienda, cajas de compensación, entes territoriales). Suele conllevar la constitución de patrimonio de familia inembargable y restricciones de enajenación.",
    fuente: "Ley 3ª/1991; Dcto 1077/2015",
  },
  "Ley 795/2003": {
    norma: "Ley 795 de 2003; Dcto 1787/2004",
    estado: "Vigente",
    art: "Leasing habitacional",
    texto:
      "En el leasing habitacional la entidad financiera es la propietaria del inmueble durante el contrato y solo lo transfiere al locatario cuando este ejerce la opción de compra. Para vender a un tercero debe terminarse previamente el contrato de leasing.",
    fuente: "Ley 795/2003; Dcto 1787/2004",
  },
  "Dcto 830/2021": {
    norma: "Decreto 830 de 2021 (LA/FT)",
    estado: "Vigente",
    art: "Beneficiario final y PEP",
    texto:
      "Impone identificar al beneficiario final (persona natural que en último término posee o controla) y aplicar debida diligencia reforzada a las Personas Expuestas Políticamente (PEP), con verificación de la fuente de riqueza y aprobación de instancia superior.",
    fuente: "Dcto 830/2021",
  },
  "art. 38 · Dcto 960/70": {
    norma: "Decreto-Ley 960 de 1970",
    estado: "Vigente",
    art: "Artículo 38 — Intérprete",
    texto:
      "Cuando alguno de los otorgantes no conozca el idioma castellano, el notario exigirá la intervención de un intérprete que traduzca el instrumento; los documentos en idioma extranjero se acompañan de traducción oficial.",
    fuente: "Dcto 960/1970",
  },
  "art. 39 · Dcto 960/70": {
    norma: "Decreto-Ley 960 de 1970",
    estado: "Vigente",
    art: "Artículo 39 — Firma a ruego",
    texto:
      "Cuando el otorgante no sepa o no pueda firmar, lo hará por él otra persona a su ruego, en presencia de dos testigos que también firmarán; se tomará la impresión de la huella dactilar del otorgante.",
    fuente: "Dcto 960/1970",
  },
  "Ley 2195/2022 · SIPLAFT": {
    norma: "Ley 2195/2022 + SIPLAFT notarial",
    estado: "Vigente",
    art: "Prevención de lavado (LA/FT)",
    texto:
      "La Ley 2195 de 2022 refuerza la prevención de lavado de activos y el registro de beneficiarios finales. En notarías rige el SIPLAFT (Circular SNR 1536/2013 e Instrucciones 17/2016 y 08/2017): debida diligencia, conocimiento del cliente, declaración de origen lícito de fondos y reporte de operaciones sospechosas a la UIAF.",
    fuente: "Gestor i=175606; UIAF/SNR",
  },
  "Ley 2195/2022": {
    norma: "Ley 2195/2022 + SIPLAFT notarial",
    estado: "Vigente",
    art: "Prevención de lavado (LA/FT)",
    texto:
      "La Ley 2195 de 2022 refuerza la prevención de lavado de activos y el registro de beneficiarios finales. En notarías rige el SIPLAFT: debida diligencia, conocimiento del cliente, declaración de origen lícito de fondos y reporte de operaciones sospechosas a la UIAF.",
    fuente: "Gestor i=175606; UIAF/SNR",
  },
  "RES-2026-000964-6": {
    norma: "Superintendencia de Notariado y Registro",
    estado: "Vigente 2026",
    art: "Resolución RES-2026-000964-6 — Tarifas notariales 2026",
    texto:
      "Fija las tarifas por el ejercicio de la función notarial para 2026 (vigentes desde el 1 de febrero de 2026; ajuste IPC 5,10%). Actos con cuantía igual o inferior a $189.700: $22.500; sobre el excedente, tarifa única del tres por mil (3‰). Las VIS/VIP tienen 50% de descuento en derechos notariales.",
    fuente: "Supernotariado; asuntoslegales.co",
  },
  "art. 2457 C.C.": {
    norma: "Código Civil",
    estado: "Vigente",
    art: "Artículo 2457 — Extinción de la hipoteca",
    texto:
      "La hipoteca se extingue junto con la obligación principal, y por la cancelación que el acreedor otorgue por escritura pública, de la cual se tome razón al margen de la inscripción respectiva. Cancelado el gravamen, el inmueble queda libre para el propietario.",
    fuente: "Código Civil",
  },
  "art. 23 · Ley 546/1999": {
    norma: "Ley 546 de 1999 — Financiación de vivienda",
    estado: "Vigente",
    art: "Artículo 23 — Cancelación de gravámenes",
    texto:
      "La cancelación de los gravámenes hipotecarios constituidos en garantía de créditos para la financiación de vivienda individual a largo plazo se considera un acto sin cuantía para efectos de los derechos notariales y de registro.",
    fuente: "Gestor Normativo; Ley 546/1999",
  },
  "art. 12 · Dcto 2148/1983": {
    norma: "Decreto 2148 de 1983 (compilado en Dcto 1069/2015)",
    estado: "Vigente",
    art: "Artículo 12 — Otorgamiento fuera del despacho",
    texto:
      "El notario podrá autorizar que un compareciente suscriba el instrumento fuera de las instalaciones de la notaría, en el sitio donde se encuentre, dejando constancia de la circunstancia en el propio instrumento.",
    fuente: "Dcto 2148/1983; Dcto 1069/2015",
  },
  "Circular SNR 1536/2013 · Ley 1581/2012": {
    norma: "Circular SNR 1536 de 2013 + Ley 1581 de 2012",
    estado: "Vigente",
    art: "Tratamiento de datos y consulta STRADATA",
    texto:
      "La Ley 1581 de 2012 exige la autorización previa, expresa e informada del titular para el tratamiento de datos personales. La Circular 1536 de 2013 de la S.N.R. dispone la consulta de los intervinientes en el sistema STRADATA como control de prevención de lavado de activos y financiación del terrorismo.",
    fuente: "S.N.R.; Ley 1581/2012",
  },
};

/** Busca el detalle de una norma por el texto exacto del badge de cita. */
export function lookupNorma(text: string | null | undefined): NormaTip | null {
  if (!text) return null;
  return NORMAS[text.trim()] ?? null;
}
