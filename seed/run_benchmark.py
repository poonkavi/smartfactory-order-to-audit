from app import create_app
from seed.benchmark_data import load_benchmark_data

app = create_app()

with app.app_context():
    load_benchmark_data()