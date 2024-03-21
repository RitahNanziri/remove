from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# Initialize SQLAlchemy db object
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize JWTManager with secret key
    app.config['JWT_SECRET_KEY'] = '33333'  # secret key
    jwt = JWTManager(app)

    # Import blueprints
    from authors_app.controllers.auth.auth_controller import auth
    from authors_app.controllers.auth.books_controller import book
    from authors_app.controllers.auth.company_controller import company

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/api/v1/auth')
    app.register_blueprint(book, url_prefix='/api/v1/book')
    app.register_blueprint(company, url_prefix='/api/v1/company')


    @app.route('/')
    def home():
        return "Hello world"

    # Routes for protected resources
    @app.route('/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        return jsonify(logged_in_as=current_user_id), 200

    return app

if __name__ == "_main_":
    app = create_app()
    app.run(debug=True)
