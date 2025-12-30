''' 
src.prints.py: Módulo para no tener que repetir prints a lo menso
'''

def crear_headline(titulo, caracter="= = ", ancho=10):
    """
    Crea un headline y lo devuelve como string.
    
    Returns:
        String formateado con el headline
    """
    separador = caracter * ancho
    return f"{separador}\n{titulo}\n{separador}"