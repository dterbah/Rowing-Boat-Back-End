import sys
sys.path.append('../')

from RowingBoat import db, create_app
from RowingBoat.config import Config
import os
    
c = Config()
file = c.SQLALCHEMY_DATABASE_URI[10:]
if os.path.exists(file):
    print(f'{file} deleted')
    os.remove(file)
else:
    print('file not found')

db.create_all(app=create_app())