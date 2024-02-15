from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
import maude

#Cada funcion que hay aquí es una vista

def home(request):
    # Lógica de tu vista aquí
    return render(request, 'home.html')

@require_http_methods(["POST"])
def run_maude_command(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        command_type = request.POST.get('maude_operation')
        maude_execution = request.POST.get('maude_execution')
        user_code = request.POST.get('maude_code')

        maude.init()
        maude.input(user_code)
        module = maude.getCurrentModule()

        term = module.parseTerm(maude_execution)

        if command_type == "reduce":
            term.reduce()
        elif command_type == "rewrite":
            term.rewrite()
        elif command_type == "search":
            term.serch()
        # Añadir más condiciones según sea necesario

        result_str = str(term)

        # Devolver la respuesta como JSON
        return JsonResponse({'result': result_str})
    else:
        # Manejar solicitudes no AJAX si es necesario
        return render(request, 'home.html')
