from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from databases.setting_connection import session_scope
from models.base import metadata

Base = declarative_base(metadata=metadata)

class Language(Base):
    __tablename__ = 'idioma'
    Id = Column(Integer, primary_key=True)
    Idioma = Column(String(2))
    
    def edit(id_lang, language):
        with session_scope() as session:
            edited_language = session.get(Language, id_lang)
            if edited_language:
                edited_language.Idioma = language
                return True

    def read(id_lang):
        with session_scope() as session:
            lang = session.query(Language).filter_by(Id=id_lang).first()
            if lang:
                return {
                    "lang": lang.Idioma,
                }
            else:
                return "Contacto no encontrada"
