"""
EasyPro 2 - Conversion de numeros a letras formato notarial colombiano
=======================================================================

Convierte valores monetarios al formato estandar de las notarias:
- MAYUSCULAS
- Sufijo "PESOS M/CTE"
- Numero entre parentesis al final

Ejemplo:
    numero_a_letras_notarial(212600000)
    -> "DOSCIENTOS DOCE MILLONES SEISCIENTOS MIL PESOS M/CTE ($212.600.000)"
"""
from num2words import num2words


def formatear_pesos(numero: int) -> str:
    """Formatea un entero como pesos colombianos con separador de miles."""
    return f"${numero:,}".replace(",", ".")


def numero_a_letras_notarial(numero: int) -> str:
    """
    Convierte un numero a su representacion en letras formato notarial.

    Args:
        numero: Valor entero en pesos (sin decimales)

    Returns:
        String en formato: "LETRAS PESOS M/CTE ($X.XXX.XXX)"
    """
    if numero == 0:
        return "CERO PESOS M/CTE ($0)"

    if numero < 0:
        return f"MENOS {numero_a_letras_notarial(abs(numero))}"

    # Convertir a letras en espanol
    letras = num2words(numero, lang='es').upper()

    # Limpieza para formato notarial:
    # num2words devuelve "uno" pero en notarial se usa "UN" antes de millon/mil
    letras = letras.replace("UNO MILLÓN", "UN MILLÓN")
    letras = letras.replace("UNO MIL", "UN MIL")

    # Formato final
    pesos_format = formatear_pesos(numero)
    return f"{letras} PESOS M/CTE ({pesos_format})"


def numero_a_letras_simple(numero: int) -> str:
    """Version corta solo con las letras, sin sufijo M/CTE."""
    if numero == 0:
        return "CERO"
    letras = num2words(numero, lang='es').upper()
    letras = letras.replace("UNO MILLÓN", "UN MILLÓN")
    letras = letras.replace("UNO MIL", "UN MIL")
    return letras
