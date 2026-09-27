import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Ensure exports directory exists
        if not os.path.exists(app.config['EXPORT_DIR']):
            os.makedirs(app.config['EXPORT_DIR'])
            
    app.run(debug=True, host='127.0.0.1', port=5000)
