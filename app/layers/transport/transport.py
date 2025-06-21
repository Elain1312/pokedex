# app/layers/transport/transport.py

import requests
# from ...config import config # Puedes seguir usándolo si config.py tiene otras cosas útiles,
                              # pero la URL principal de la PokeAPI la pondremos aquí directamente.

# URL base de la PokeAPI para Pokémon
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

# comunicación con la REST API.
# este método se encarga de "pegarle" a la API y traer una lista de objetos JSON.
def getAllImages():
    json_collection = []
    
    # URL para obtener una lista limitada de Pokémon.
    # Por ejemplo, 150 Pokémon, para no hacer demasiadas peticiones al inicio.
    # La PokeAPI devuelve una lista de objetos {name: "...", url: "..."},
    # y cada 'url' lleva a los detalles del Pokémon.
    list_url = f"{POKEAPI_BASE_URL}?limit=30" # Ajusta el límite como desees

    print(f"DEBUG_TRANSPORT: Intentando obtener lista de Pokémon de: {list_url}")
    try:
        response = requests.get(list_url)
        response.raise_for_status() # Levanta una excepción para códigos de estado HTTP de error (4xx, 5xx)
        data = response.json()
        
        # La respuesta de PokeAPI para un listado tiene una clave 'results' que contiene la lista de Pokémon
        pokemon_list_summary = data.get('results', []) 
        
        print(f"DEBUG_TRANSPORT: Obtenidos {len(pokemon_list_summary)} resúmenes de Pokémon.")

        # Ahora, para cada resumen (que contiene nombre y URL), hacemos una petición para obtener los detalles completos
        for pokemon_summary in pokemon_list_summary:
            detail_url = pokemon_summary['url']
            print(f"DEBUG_TRANSPORT: Obteniendo detalles para: {detail_url}")
            detail_response = requests.get(detail_url)
            detail_response.raise_for_status() # Asegurarse de que la petición de detalles sea exitosa
            
            raw_data = detail_response.json()
            json_collection.append(raw_data)

    except requests.exceptions.RequestException as e:
        print(f"ERROR_TRANSPORT: Error de conexión o HTTP al obtener Pokémon: {e}")
        return []
    except ValueError as e: # Si la respuesta no es un JSON válido
        print(f"ERROR_TRANSPORT: Error al parsear JSON de la API: {e}")
        # Puedes imprimir response.text aquí para depurar el contenido si el JSON está mal
        return []
    except Exception as e:
        print(f"ERROR_TRANSPORT: Un error inesperado ocurrió: {e}")
        return []

    print(f"DEBUG_TRANSPORT: getAllImages() finalizó. Recolectados {len(json_collection)} Pokémon.")
    return json_collection

# Nueva función para obtener detalles de un Pokémon por ID, si la necesitas en services.py para favoritos
def get_pokemon_data_by_id(pokemon_id):
    detail_url = f"{POKEAPI_BASE_URL}{pokemon_id}/"
    print(f"DEBUG_TRANSPORT: Obteniendo detalles de Pokémon por ID: {detail_url}")
    try:
        response = requests.get(detail_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR_TRANSPORT: No se pudo obtener el Pokémon con ID {pokemon_id}: {e}")
        return None
    except ValueError as e:
        print(f"ERROR_TRANSPORT: Error al parsear JSON para Pokémon ID {pokemon_id}: {e}")
        return None


# obtiene la imagen correspondiente para un type_id especifico
def get_type_icon_url_by_id(type_id):
    base_url = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/types/generation-iii/colosseum/'
    return f"{base_url}{type_id}.png"