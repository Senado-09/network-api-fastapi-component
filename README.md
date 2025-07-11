# 🌐 Network API – FastAPI Component

This project is a reusable **FastAPI backend component** for managing hierarchical user networks, referrals, generations, and commercial network trees.

It is designed to be embedded in larger systems (SaaS, marketplace, MLM, etc.) or used standalone.

---

## 🚀 Features

- Create and manage user networks
- Assign users to networks via referral codes
- Auto-generate new networks when full
- Commercials can create and own networks
- Get full hierarchical network trees
- Fully modular (models, routes, schemas, utils)
- Compatible with MySQL and PostgreSQL


---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/senado-09/network-api–fastapi-component.git
cd network-api–fastapi-component

2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables
Create a .env file from the example:
cp .env.example .env
And fill in your credentials (DB, SECRET_KEY, etc.).


🗃️ Database
The app supports MySQL and PostgreSQL.
Set TYPE_DB=mysql or TYPE_DB=postgres in your .env file.
Run your migration system (e.g., Alembic) or manually create tables from models:

from app.database import Base, engine
from app.models import *  # All models

Base.metadata.create_all(bind=engine)


▶️ Run the App
uvicorn app.main:app --reload
Then visit http://localhost:8000/docs to test the API.


🧪 Run Tests
pytest


📦 Routes Overview
Method	                Endpoint	                          Description
GET	        /network/users/{user_id}/network-tree	    Get the full referral tree
POST	        /network/assign-user	                Add a user to a network by referral
POST	    /network/create-commercial-network	        Create a network for a commercial
POST	    /network/calculate-position	                Get generation/position from plan


🛠 Built With
FastAPI
SQLAlchemy
Pydantic
Uvicorn
Python-dotenv


🔒 Security Note
This repo assumes your main application handles authentication (e.g., JWT tokens, roles). 
You can extend config.py to include permission checks (get_current_user, etc.).


🧠 Author
Made with ❤️ by SENA DOMONHEDO

📝 License
MIT License
