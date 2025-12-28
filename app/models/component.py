from sqlalchemy import Column, Integer, String, DateTime, Enum, func, UUID, Index, Boolean
from sqlalchemy.orm import relationship
from app.configs.db import Base
import uuid

class Component(Base):
    """Model form component karoseri product"""
    __tablename__ = "components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    damage_records = relationship("DamageRecord", back_populates="component", cascade="all, delete-orphan")
    prediction_histories = relationship("PredictionHistory", back_populates="component", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Component {self.code}: {self.name}>"