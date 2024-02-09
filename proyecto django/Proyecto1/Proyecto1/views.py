from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import maude

#Cada funcion que hay aquí es una vista

def home(request):
    # Lógica de tu vista aquí
    return render(request, 'home.html')

def run_maude_command(request):
    user_input = request.POST.get('maude_command')

    maude.init()

    # Cargar el módulo, aquí podrías cargar un módulo que entienda tu operación
    module = maude.getModule('NAT')

    # Parsear el término ingresado por el usuario
    term = module.parseTerm(user_input)

    # Reducir el término
    term.reduce()

    # Convertir el resultado a string para la visualización
    result_str = str(term)

    return render(request, 'home.html', {'result': result_str})

    
