from app import create_app

app = create_app()
from app import db

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
