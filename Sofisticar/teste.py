import requests
import json

def buscar_dados():
    request = requests.get("https://parallelum.com.br/fipe/api/v1/carros/marcas")
    print(request.content)

if __name__ == '__main__':
    buscar_dados()