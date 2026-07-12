import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database import engine

async def seed_database():
    print("Connecting to database...")
    
    # Notice I made the role_names lowercase to match your API schema expectations!
    statements = [
        """
        INSERT INTO roles (id, role_name)
        VALUES
        (1,'creator'),
        (2,'agency'),
        (3,'marketing_team'),
        (4,'administrator')
        ON CONFLICT (id) DO UPDATE SET role_name = EXCLUDED.role_name;
        """,

        """
        INSERT INTO users (id, full_name, email, phone_number, password_hash, role_id)
        VALUES
        ('crt11','Rahul Sharma','rahul@gmail.com','9876543210','hashed_password1',1),
        ('crt32','Priya Reddy','priya@gmail.com','9876543211','hashed_password2',1),
        ('agc21','ABC Agency','agency@gmail.com','9876543212','hashed_password3',2)
        ON CONFLICT (id) DO NOTHING;
        """,

        """
        INSERT INTO creator_profiles (id, user_id, username, bio, youtube_url, instagram_url, linkedin_url)
        VALUES
        ('crt11','crt11','rahulYT','Tech Content Creator','https://youtube.com/@rahul','https://instagram.com/rahul','https://linkedin.com/in/rahul'),
        ('crt32','crt32','priyaCodes','Programming Tutorials','https://youtube.com/@priya','https://instagram.com/priya','https://linkedin.com/in/priya')
        ON CONFLICT (id) DO NOTHING;
        """,

        """
        INSERT INTO agency_profiles (id, user_id, agency_name, website, contact_number)
        VALUES
        ('agc21','agc21','ABC Digital Agency','https://abcagency.com','9876543210')
        ON CONFLICT (id) DO NOTHING;
        """,

        """
        INSERT INTO account_settings (id, user_id, theme, notifications, language)
        VALUES
        ('set11','crt11','Dark',TRUE,'English'),
        ('set32','crt32','Light',TRUE,'English'),
        ('set21','agc21','Dark',FALSE,'English')
        ON CONFLICT (id) DO NOTHING;
        """,

        """
        INSERT INTO agency_creators (id, agency_id, creator_id)
        VALUES
        ('map11','agc21','crt11'),
        ('map12','agc21','crt32')
        ON CONFLICT (id) DO NOTHING;
        """
    ]
    
    async with engine.begin() as conn:
        print("Running seed script...")
        for stmt in statements:
            await conn.execute(text(stmt))
        print("Database successfully seeded!")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_database())
