from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():

    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    # Salesman module
    from app.routes.salesman import salesman_bp
    app.register_blueprint(salesman_bp)

    # Admin module
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Purchase module
    from app.routes.purchases import purchase_bp
    app.register_blueprint(purchase_bp)

    # Production module
    from app.routes.production import production_bp
    app.register_blueprint(production_bp)

    # Invoice module
    from app.routes.invoices import invoice_bp
    app.register_blueprint(invoice_bp)

    # Dispatch module
    from app.routes.dispatch import dispatch_bp
    app.register_blueprint(dispatch_bp)

    # Payment module
    from app.routes.payments import payment_bp
    app.register_blueprint(payment_bp)

    # Reports module
    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp)

    # Main Dashboard module
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Authentication module
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Home page - redirect to login
    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    return app