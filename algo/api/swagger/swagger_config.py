from flasgger import Swagger

def init_swagger(app):
    return Swagger(app, template={
        "info": {
            "title": "Mosaic Trading API",
            "description": "Trading api built with Flask and using Alpaca as broker",
            "version": "1.0.0"
        }
    })