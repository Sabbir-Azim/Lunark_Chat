from datetime import datetime
import logging
import sqlite3

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from runtime_paths import (
    CHAT_DATABASE_PATH,
    CHECKPOINT_DATABASE_PATH,
    sqlite_url,
)

DATABASE_URL = sqlite_url(CHAT_DATABASE_PATH)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
logger = logging.getLogger(__name__)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def create_or_update_conversation(thread_id: str, first_message: str | None = None):
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if not conversation:
            title = "New Chat"

            if first_message:
                title = first_message.strip()[:40]
                if len(first_message.strip()) > 40:
                    title += "..."

            conversation = Conversation(
                thread_id=thread_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(conversation)

        else:
            conversation.updated_at = datetime.utcnow()

        db.commit()

    finally:
        db.close()


def list_conversations():
    db = SessionLocal()

    try:
        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    finally:
        db.close()


def save_chat_message(thread_id: str, role: str, content: str):
    db = SessionLocal()

    try:
        msg = ChatMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )

        db.add(msg)

        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()

    finally:
        db.close()


def get_chat_history(thread_id: str):
    db = SessionLocal()

    try:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    finally:
        db.close()


def save_memory(thread_id: str, memory: str):
    db = SessionLocal()

    try:
        item = LongTermMemory(
            thread_id=thread_id,
            memory=memory,
            created_at=datetime.utcnow()
        )

        db.add(item)
        db.commit()

        return "Memory saved successfully."

    finally:
        db.close()


def search_memory(thread_id: str, query: str):
    db = SessionLocal()

    try:
        memories = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.thread_id == thread_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(20)
            .all()
        )

        if not memories:
            return "No saved memory found."

        return "\n".join([f"- {m.memory}" for m in memories])

    finally:
        db.close()


def delete_conversation(thread_id: str) -> bool:
    """Delete one conversation and all data scoped to its thread."""
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if not conversation:
            return False

        db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).delete(
            synchronize_session=False
        )
        db.query(LongTermMemory).filter(LongTermMemory.thread_id == thread_id).delete(
            synchronize_session=False
        )
        db.delete(conversation)
        db.commit()
    finally:
        db.close()

    try:
        delete_thread_checkpoints(thread_id)
    except sqlite3.Error:
        # The primary chat data is already deleted. A locked/corrupt checkpoint
        # store should not make the API report the whole operation as failed.
        logger.warning(
            "Could not remove checkpoints for deleted thread %s",
            thread_id,
            exc_info=True,
        )
    return True


def delete_thread_checkpoints(thread_id: str):
    """Remove LangGraph checkpoint rows for a deleted conversation thread."""
    checkpoint_path = CHECKPOINT_DATABASE_PATH

    if not checkpoint_path.exists():
        return

    with sqlite3.connect(checkpoint_path, timeout=10) as conn:
        table_names = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        ]

        for table_name in table_names:
            safe_table_name = table_name.replace('"', '""')
            columns = {
                row[1]
                for row in conn.execute(
                    f'PRAGMA table_info("{safe_table_name}")'
                ).fetchall()
            }

            if "thread_id" in columns:
                conn.execute(
                    f'DELETE FROM "{safe_table_name}" WHERE thread_id = ?',
                    (thread_id,),
                )

        conn.commit()
