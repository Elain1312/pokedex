# app/views.py
# capa de vista/presentación

from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request):
    # Llama al servicio para obtener todas las imágenes de Pokémon
    images = services.getAllImages() # <--- ¡Aquí se obtiene la lista de Cards!
    
    # Llama al servicio para obtener los favoritos del usuario actual
    # Asegúrate de que getAllFavourites en services.py maneje el request.user
    favourite_list = services.getAllFavourites(request) 

    # Agrega mensajes de depuración para ver qué está pasando
    print(f"DEBUG_VIEW_HOME: Obtenidas {len(images)} imágenes de Pokémon.")
    print(f"DEBUG_VIEW_HOME: Obtenidos {len(favourite_list)} favoritos para el usuario.")

    context = {
        'images': images,
        'favourite_list': favourite_list,
        'message': "La búsqueda no arrojó resultados..." if not images else "" # Solo muestra el mensaje si 'images' está vacía
    }
    
    return render(request, 'home.html', context)

# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '')

    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if name != '':
        # Llama al servicio para filtrar por nombre del Pokémon
        images = services.filterByCharacter(name) # <--- Filtrando por nombre
        
        # Obtén la lista de favoritos para que también estén disponibles en la plantilla
        favourite_list = services.getAllFavourites(request)

        print(f"DEBUG_VIEW_SEARCH: Obtenidas {len(images)} imágenes de Pokémon para la búsqueda '{name}'.")

        context = {
            'images': images,
            'favourite_list': favourite_list,
            'message': f"No se encontraron resultados para '{name}'." if not images else ""
        }
        
        return render(request, 'home.html', context)
    else:
        # Si el buscador está vacío, redirige a la página principal para mostrar todos los Pokémon
        return redirect('home')

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    type_filter = request.POST.get('type', '') # Cambié el nombre de la variable para evitar conflicto con 'type' de Python

    if type_filter != '':
        # Llama al servicio para filtrar por tipo de Pokémon
        images = services.filterByType(type_filter) # <--- Filtrando por tipo
        
        # Obtén la lista de favoritos
        favourite_list = services.getAllFavourites(request)

        print(f"DEBUG_VIEW_FILTER: Obtenidas {len(images)} imágenes de Pokémon para el tipo '{type_filter}'.")

        context = {
            'images': images,
            'favourite_list': favourite_list,
            'message': f"No se encontraron resultados para el tipo '{type_filter}'." if not images else ""
        }
        
        return render(request, 'home.html', context)
    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    # La lógica para obtener favoritos ya está en home.
    # Esta función podría ser redundante si ya se muestran en home.
    # Si esta es para una página de favoritos dedicada, debería llamar a services.getAllFavourites(request)
    # y luego renderizar una plantilla específica para favoritos.
    # Por ahora, simplemente redirige a home, o implementa una vista para 'favourites.html'
    favourite_cards = services.getAllFavourites(request)
    print(f"DEBUG_VIEW_FAVOURITES: Obtenidos {len(favourite_cards)} favoritos para el usuario logueado.")
    context = {
        'favourite_list': favourite_cards,
        'message': "No tienes favoritos guardados." if not favourite_cards else ""
    }
    return render(request, 'favourites.html', context) # Asume que tienes un template 'favourites.html'


@login_required
def saveFavourite(request):
    if request.method == 'POST':
        # services.saveFavourite espera el objeto request completo
        success = services.saveFavourite(request) 
        if success:
            print(f"DEBUG_VIEW_SAVE_FAV: Favorito guardado exitosamente para el usuario {request.user.username}.")
        else:
            print(f"DEBUG_VIEW_SAVE_FAV: Fallo al guardar favorito para el usuario {request.user.username}.")
    return redirect('home') # Redirige a home después de guardar

@login_required
def deleteFavourite(request):
    if request.method == 'POST':
        # services.deleteFavourite espera el objeto request completo
        success = services.deleteFavourite(request) 
        if success:
            print(f"DEBUG_VIEW_DELETE_FAV: Favorito eliminado exitosamente para el usuario {request.user.username}.")
        else:
            print(f"DEBUG_VIEW_DELETE_FAV: Fallo al eliminar favorito para el usuario {request.user.username}.")
    return redirect('home') # Redirige a home después de eliminar

@login_required
def exit(request):
    logout(request)
    print("DEBUG_VIEW_EXIT: Sesión de usuario cerrada.")
    return redirect('home')