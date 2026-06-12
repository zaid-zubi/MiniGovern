MiniGovern is Lightweight Data Governance Service

1. Create .env file and copy content from .env.example
    - Use this command to copy => cp .env.exmaple .env

2. Build Postgresql database with MiniGovern

3. Generate your encryption key by this : python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())", and update in .env

4. Use "make migrate" for migrating the changes on your database

5. Create Admin by running this command: make defaultAdmin