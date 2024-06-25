# coding: utf-8
from sqlalchemy import Column, INTEGER, TEXT, BOOLEAN, DATETIME, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///./config/bot.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
DBSession = sessionmaker(bind=engine)
Base = declarative_base()


class Message(Base):
    __tablename__ = "message"

    _id = Column(INTEGER, primary_key=True)
    id = Column(INTEGER)
    link = Column(TEXT)
    type = Column(TEXT)  # 文本、图像、视频、音频、语音
    category = Column(TEXT)  # 分类
    text = Column(TEXT)
    video = Column(TEXT)
    photo = Column(TEXT)
    audio = Column(TEXT)
    voice = Column(TEXT)
    date = Column(DATETIME)
    from_id = Column(INTEGER)
    from_chat = Column(INTEGER)


class User(Base):
    __tablename__ = "user"

    id = Column(INTEGER, primary_key=True)
    fullname = Column(TEXT)
    username = Column(TEXT)


class Chat(Base):
    __tablename__ = "chat"

    id = Column(INTEGER, primary_key=True)
    title = Column(TEXT)
    enable = Column(BOOLEAN)


Base.metadata.create_all(engine)


class OpenableDBSession:
    def __init__(self):
        self.db = None
        pass

    def _open(self):
        if self.db is None:
            self.db = DBSession()

    def _close(self):
        if self.db is not None:
            self.db.close()
            self.db = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._close()

    def query(self, *args, **kargs):
        self._open()
        return self.db.query(*args, **kargs)

    def add(self, *args, **kargs):
        self._open()
        return self.db.add(*args, **kargs)

    def commit(self):
        self._open()
        return self.db.commit()

    def destroy(self) -> None:
        self._close()
