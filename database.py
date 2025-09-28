from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_premium = Column(Boolean, default=False)
    free_generations_used = Column(Integer, default=0)
    premium_generations_used = Column(Integer, default=0)
    free_generations_limit = Column(Integer, default=2)  # Лимит бесплатных генераций
    premium_generations_limit = Column(Integer, default=50)  # Лимит премиум генераций
    premium_expires_at = Column(DateTime)  # Дата истечения премиум подписки
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bots = relationship("Bot", back_populates="owner")

class Bot(Base):
    __tablename__ = 'bots'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    token = Column(String(255), unique=True)
    webhook_url = Column(String(500))
    owner_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(50), default='created')  # created, active, inactive, error
    generated_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="bots")

class Generation(Base):
    __tablename__ = 'generations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    bot_id = Column(Integer, ForeignKey('bots.id'))
    prompt = Column(Text, nullable=False)
    generated_code = Column(Text)
    status = Column(String(50), default='pending')  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", backref="generations")
    bot = relationship("Bot", backref="generations")

# Database setup
# Для Vercel используем PostgreSQL, для локальной разработки - SQLite
database_url = Config.DATABASE_URL
if database_url.startswith('sqlite'):
    # Локальная разработка
    engine = create_engine(database_url)
else:
    # Продакшн (Vercel)
    engine = create_engine(database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
