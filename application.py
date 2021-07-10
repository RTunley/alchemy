from alchemy import application, db

if __name__ == '__main__':
    application.run(debug=True)
    db.create_all()
