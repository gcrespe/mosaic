from flask import Flask, redirect
from algo.api.swagger.swagger_config import init_swagger
from algo.api.routes.trading_routes import trading_bp
from algo.api.routes.backtest_routes import backtest_bp

def create_app():

    app = Flask(__name__)
    
    # Initialize Swagger
    init_swagger(app)
    
    # Register blueprints
    app.register_blueprint(trading_bp)
    app.register_blueprint(backtest_bp)
    
    # Root route
    @app.get("/")
    def apidocs():
        return redirect("/apidocs")
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return "404"

    @app.errorhandler(500)
    def internal_server_error(e):
        return "500"
    
    return app

app = create_app()
app.run(debug=True)