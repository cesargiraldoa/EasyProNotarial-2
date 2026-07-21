import type { ActoCode } from "@/lib/motor-escritura";

export type BibliotecaRedaccionItem = {
  titulo: string;
  detalle: string;
  html: string;
};

export const BIBLIO: BibliotecaRedaccionItem[] = [
  {
    titulo: "Renuncia a la condicion resolutoria (pago)",
    detalle: "Titulo firme e irresoluble",
    html: '<p class="cl"><span class="clh">PARAGRAFO - RENUNCIA A LA CONDICION RESOLUTORIA (FORMA DE PAGO).</span> No obstante la forma de pago, la parte vendedora renuncia expresamente al ejercicio de la accion resolutoria que de ella pueda derivarse y en consecuencia otorga el presente titulo firme e irresoluble.</p>',
  },
  {
    titulo: "Afectacion a vivienda familiar (SI)",
    detalle: "Ley 258/1996 - comparece conyuge",
    html: '<p class="cl"><span class="clh">EFECTOS DE LA LEY 258 DE 1996.</span> Indagados los compradores senores <span class="campo" data-field="comprador">LOS COMPRADORES</span> sobre su estado civil, manifiestan bajo la gravedad de juramento que de comun acuerdo han decidido que el inmueble que se adquiere SI queda afectado a vivienda familiar.</p>',
  },
  {
    titulo: "Paz y salvo de administracion (PH)",
    detalle: "Art. 29 Ley 675/2001",
    html: '<p class="cl"><span class="clh">PAZ Y SALVO DE ADMINISTRACION.</span> La parte vendedora presento el paz y salvo de las expensas comunes de la copropiedad; de existir deudas posteriores, el comprador se hace solidario conforme al articulo 29 de la Ley 675 de 2001.</p>',
  },
  {
    titulo: "Nota REDAM",
    detalle: "Ley 2097/2021",
    html: '<p class="para"><span class="clh">NOTA - REDAM.</span> Ante la indisponibilidad de la base de datos del Registro de Deudores Alimentarios Morosos, el compareciente declara bajo juramento no tener obligaciones alimentarias en mora superiores a tres meses.</p>',
  },
  {
    titulo: "Origen de fondos / SARLAFT",
    detalle: "Ley 2195/2022",
    html: '<p class="para"><span class="clh">ORIGEN DE LOS INGRESOS.</span> <span class="campo" data-field="comprador">EL COMPRADOR</span> declara que los recursos con que adquiere provienen de actividades licitas y que no se encuentra en listados de prevencion de lavado de activos (OFAC u otros).</p>',
  },
  {
    titulo: "Servidumbre",
    detalle: "A favor de predio vecino",
    html: '<p class="cl"><span class="clh">SERVIDUMBRE.</span> El inmueble se transfiere con la servidumbre de <span class="campo" data-field="servidumbre">transito</span> a favor del predio vecino, que la parte compradora declara conocer y aceptar.</p>',
  },
];

export const BIBLIO_CANC: BibliotecaRedaccionItem[] = [
  {
    titulo: "Acto sin cuantia (Ley 546/1999)",
    detalle: "Cancelacion de credito de vivienda",
    html: '<p class="cl"><span class="clh">PARAGRAFO - ACTO SIN CUANTIA.</span> De acuerdo con el articulo 23 de la Ley 546 de 1999, que regula la cancelacion de gravamenes hipotecarios de creditos para vivienda, la presente cancelacion se considera un acto sin cuantia.</p>',
  },
  {
    titulo: "No paz y salvo del deudor",
    detalle: "Solo se libera el gravamen",
    html: '<p class="cl"><span class="clh">NO PAZ Y SALVO.</span> La cancelacion de esta hipoteca no implica paz y salvo a favor del Deudor, ya que este acto solo conlleva la cancelacion del gravamen hipotecario identificado, sin exoneracion de las obligaciones que por otros conceptos pudiere tener el Deudor como deudor principal, avalista o deudor solidario.</p>',
  },
  {
    titulo: "Valor asignado para liquidacion",
    detalle: "Contrato de hipoteca",
    html: '<p class="cl"><span class="clh">VALOR PARA LIQUIDACION.</span> Para efectos de la liquidacion de derechos notariales y de registro, se asigno al contrato de hipoteca un valor de <span class="campo" data-field="cHipMonto">$0</span>.</p>',
  },
  {
    titulo: "NOTA - Firma fuera de la sede",
    detalle: "Art. 12 Dcto 2148/1983",
    html: '<p class="para"><span class="clh">NOTA - FIRMA FUERA DE LA SEDE.</span> <span class="campo" data-field="cApoNombre">El apoderado</span>, actuando como <span class="campo" data-field="cRepCargo">Apoderado(a) Especial</span> de <span class="campo" data-field="cBanco">el banco</span>, por autorizacion de la suscrita notaria, suscribe la presente escritura fuera de las instalaciones de la Notaria Dieciseis de Medellin, en su despacho, conforme al articulo 12 del Decreto 2148 de 1983.</p>',
  },
  {
    titulo: "NOTA - SARLAFT / STRADATA",
    detalle: "Ley 1581/2012 - Circular 1536/2013",
    html: '<p class="para"><span class="clh">NOTA - SARLAFT.</span> AUTORIZACION DE TRATAMIENTO DE DATOS PERSONALES. STRADATA SEARCH: en cumplimiento de la Circular 1536 del 17 de septiembre de 2013 de la S.N.R. y del articulo 17 de la Ley 282 de 1996, se consulto la informacion del otorgante en el programa STRADATA.</p>',
  },
  {
    titulo: "NOTA - Notificaciones electronicas",
    detalle: "Art. 15 Dcto 1579/2012",
    html: '<p class="para"><span class="clh">NOTA - NOTIFICACIONES ELECTRONICAS.</span> El compareciente manifiesta que SI da su consentimiento, concedido con la firma de esta escritura, para ser notificado por medio electronico sobre el estado del tramite ante la Oficina de Instrumentos Publicos, al correo: <span class="campo" data-field="cCorreoNotif">correo@dominio.com</span>.</p>',
  },
];

export function bibliotecaRedaccionPorActo(acto: ActoCode) {
  return acto === "cancelacion" ? BIBLIO_CANC : BIBLIO;
}
