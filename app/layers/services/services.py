# app/layers/services/services.py

from django.core.cache import cache # <--- NUEVA IMPORTACIÓN: Importa el sistema de caché de Django
from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user
from app.models import Favourite 

# Clave de la caché para almacenar todas las cartas de Pokémon
POKEMON_CARDS_CACHE_KEY = 'all_pokemon_cards'
# Tiempo en segundos que los datos permanecerán en caché (por ejemplo, 24 horas)
CACHE_TIMEOUT = 60 * 60 * 24 

# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # Paso 1: Intentar obtener las cartas de la caché
    cartas = cache.get(POKEMON_CARDS_CACHE_KEY)

    if cartas is not None:
        print("DEBUG_SERVICES: Devolviendo cartas desde la caché de Django.")
        return cartas # Si se encontraron en caché, las devuelve inmediatamente

    # Paso 2: Si no están en caché, cargarlas de la API (esto solo ocurrirá la primera vez o después de que expire la caché)
    pokemon_data = []
    try:
        pokemon_data = transport.getAllImages()
    except Exception as e:
        print(f"ERROR al obtener datos de la API en services.getAllImages(): {e}")
        return []

    cartas = []
    for pokemon in pokemon_data:
        try:
            card = translator.fromRequestIntoCard(pokemon)
            if card:
                cartas.append(card)
        except Exception as e:
            print(f"ERROR al convertir Pokémon a Card: {pokemon.get('name', 'N/A')} - {e}")
    
    # Paso 3: Almacenar las cartas cargadas en la caché de Django para futuras solicitudes
    cache.set(POKEMON_CARDS_CACHE_KEY, cartas, CACHE_TIMEOUT)
    print(f"DEBUG_SERVICES: Cartas cargadas y almacenadas en caché de Django: {len(cartas)}.")
    return cartas

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []
    # filterByCharacter ahora llamará a getAllImages(), que a su vez obtendrá de la caché si está disponible
    all_cards = getAllImages() 

    if name:
        name_lower = name.lower().strip()
        for card in all_cards:
            if card.name and name_lower in card.name.lower():
                filtered_cards.append(card)
    else:
        filtered_cards = all_cards

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []
    # filterByType también llamará a getAllImages(), usando la caché
    all_cards = getAllImages() 

    if type_filter:
        type_filter_lower = type_filter.lower().strip()
        for card in all_cards:
            if card.types and any(type_filter_lower in t.lower() for t in card.types):
                filtered_cards.append(card)
    else:
        filtered_cards = all_cards

    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    user = get_user(request)
    if not user.is_authenticated:
        print("DEBUG: Usuario no autenticado para guardar favorito.")
        return False

    pokemon_id = request.POST.get('pokemon_id')
    
    if not pokemon_id:
        print("DEBUG: No se encontró 'pokemon_id' en la solicitud POST para guardar favorito.")
        return False

    try:
        if Favourite.objects.filter(user=user, pokemon_id=pokemon_id).exists(): 
            print(f"DEBUG: El Pokémon {pokemon_id} ya es favorito para {user.username}.")
            return True 

        new_favourite = Favourite(user=user, pokemon_id=pokemon_id) 
        
        return repositories.save_favourite(new_favourite)
    except Exception as e:
        print(f"ERROR al guardar favorito para pokemon_id {pokemon_id}: {e}")
        return False

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)
        
        favourite_objects = []
        try:
            favourite_objects = repositories.get_all_favourites_by_user(user)
        except Exception as e:
            print(f"ERROR al obtener favoritos desde el repositorio para {user.username}: {e}")
            return []

        mapped_favourites = []
        for fav_obj in favourite_objects:
            try:
                # Aquí podrías usar get_pokemon_data_by_id si la API tiene un endpoint para eso
                # o buscar en tu caché global de Pokémon si tienes todos los detalles
                # Por simplicidad, asumimos que fav_obj.pokemon_id es suficiente para un placeholder o que
                # transport.get_pokemon_data_by_id existe y es eficiente.
                pokemon_data_for_card = transport.get_pokemon_data_by_id(fav_obj.pokemon_id)
                if pokemon_data_for_card:
                    card = translator.fromRequestIntoCard(pokemon_data_for_card)
                    if card:
                        mapped_favourites.append(card)
            except Exception as e:
                print(f"ERROR al cargar datos o convertir favorito '{fav_obj.pokemon_id}' a Card: {e}")
                continue 

        return mapped_favourites

def deleteFavourite(request):
    user = get_user(request)
    if not user.is_authenticated:
        print("DEBUG: Usuario no autenticado para borrar favorito.")
        return False

    fav_id = request.POST.get('fav_id') 
    
    if not fav_id:
        print("DEBUG: No se encontró 'fav_id' en la solicitud POST para borrar favorito.")
        return False

    try:
        return repositories.delete_favourite(fav_id, user) 
    except Exception as e:
        print(f"ERROR al borrar favorito {fav_id}: {e}")
        return False

# obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        print(f"DEBUG: No se encontró ID para el tipo: {type_name}")
        return None
    try:
        return transport.get_type_icon_url_by_id(type_id)
    except Exception as e:
        print(f"ERROR al obtener URL del ícono de tipo para ID {type_id}: {e}")
        return None