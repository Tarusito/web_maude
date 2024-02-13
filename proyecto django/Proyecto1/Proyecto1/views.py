from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import maude

#Cada funcion que hay aquí es una vista

def home(request):
    # Lógica de tu vista aquí
    return render(request, 'home.html')

def run_maude_command(request):
    if request.method == "POST":
        command_type = request.POST.get('maude_operation')
        maude_execution = request.POST.get('maude_execution')
        user_code = request.POST.get('maude_code')

        maude.init()
        maude.input(user_code)
        module = maude.getCurrentModule()

        term = module.parseTerm(maude_execution)

        # Ejecutar la operación elegida por el usuario
        if command_type == "reduce":
            term.reduce()
        elif command_type == "rewrite":
            term.rewrite()
        elif command_type == "search":
            # Para search, necesitarás ajustar esto según cómo quieras usarlo
            pass
        elif command_type == "frewrite":
            term.frewrite()
        elif command_type == "xrewrite":
            term.xrewrite()

        # Convertir el resultado a string para visualización
        result_str = str(term)

        return render(request, 'home.html', {'result': result_str})
    else:
        return render(request, 'home.html')
