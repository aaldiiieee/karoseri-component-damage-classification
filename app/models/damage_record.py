from sqlalchemy import Column, String, Float, Integer, Text, Enum, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.configs.db import Base
import enum
import uuid


class DamageLevel(str, enum.Enum):
    """Enum for damage level classification."""
    ringan = "ringan"
    sedang = "sedang"
    berat = "berat"


class DamageRecord(Base):
    """
    Model for component damage records (training data).
    
    Features for Naive Bayes classification:
    1. damage_area - Damage area in cm²
    2. damage_depth - Damage depth in mm
    3. damage_point_count - Number of damage points/spots
    4. component_age - Component age in months
    5. usage_frequency - Usage intensity (scale 1-10)
    6. corrosion_level - Corrosion level (scale 1-5)
    7. deformation - Deformation level in mm
    """
    __tablename__ = "damage_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to component
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id"), nullable=False)

    # 7 Features for Naive Bayes
    damage_area = Column(Float, nullable=False)            # cm²
    damage_depth = Column(Float, nullable=False)           # mm
    damage_point_count = Column(Integer, nullable=False)   # count
    component_age = Column(Integer, nullable=False)        # months
    usage_frequency = Column(Integer, nullable=False)      # 1-10
    corrosion_level = Column(Integer, nullable=False)      # 1-5
    deformation = Column(Float, nullable=False)            # mm

    # Classification label (target)
    damage_level = Column(Enum(DamageLevel), nullable=False)

    # Additional notes
    notes = Column(Text, nullable=True)

    # Relationship
    component = relationship("Component", back_populates="damage_records")

    def __repr__(self):
        return f"<DamageRecord {self.id}: {self.damage_level.value}>"

    def get_features(self) -> list:
        """Return features as list for model input."""
        return [
            self.damage_area,
            self.damage_depth,
            self.damage_point_count,
            self.component_age,
            self.usage_frequency,
            self.corrosion_level,
            self.deformation
        ]