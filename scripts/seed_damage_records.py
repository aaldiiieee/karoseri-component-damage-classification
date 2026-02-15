import asyncio
import sys
import os
import random
import uuid
from sqlalchemy import select

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.configs.db import AsyncSessionLocal
from app.models.component import Component
from app.schemas.damage_record import DamageRecordCreate
from app.services.damage_record_service import damage_record_service
from app.services.model_metrics_service import model_metrics_service
from app.services.component_service import component_service

async def ensure_component_exists(db):
    """Ensure at least one component exists to associate records with."""
    result = await db.execute(select(Component))
    component = result.scalars().first()
    
    if not component:
        print("No component found. Creating a dummy component...")
        from app.schemas.component import ComponentCreate
        from app.models.component import ComponentType
        
        comp_data = ComponentCreate(
            name="Dummy Component",
            code="DUMMY-001",
            type="body",  # Assuming 'body' is valid, might need adjustment based on enum
            description="Created for seeding damage records"
        )
        component = await component_service.create(db, comp_data)
        print(f"Created component: {component.id}")
    
    return component

def generate_record(component_id, rules):
    """Generate a single record based on specific rules."""
    return DamageRecordCreate(
        component_id=component_id,
        damage_area=random.uniform(*rules["area"]),
        damage_depth=random.uniform(*rules["depth"]),
        damage_point_count=random.randint(*rules["points"]),
        component_age=random.randint(1, 60), # 1-5 years
        usage_frequency=random.randint(1, 10),
        corrosion_level=random.randint(*rules["corrosion"]),
        deformation=random.uniform(*rules["deformation"]),
        damage_level=rules["level"],
        notes=f"Synthetic data for {rules['level']} damage"
    )

async def seed_damage_records():
    async with AsyncSessionLocal() as db:
        print("Starting damage record seeding...")
        
        # 1. Get or Create Component
        component = await ensure_component_exists(db)
        component_id = component.id
        
        # 2. Define Rules (Karoseri General Rules)
        # Ringan: Area < 20, Depth < 2, Points < 5, Corrosion 1-2, Def < 10
        # Sedang: Area 20-50, Depth 2-10, Points 5-15, Corrosion 2-3, Def 10-50
        # Berat: Area > 50, Depth > 10, Points > 15, Corrosion 4-5, Def > 50
        
        rules = [
            {
                "level": "ringan",
                "area": (1.0, 19.9),
                "depth": (0.1, 1.9),
                "points": (1, 4),
                "corrosion": (1, 2),
                "deformation": (0.0, 9.9)
            },
            {
                "level": "sedang",
                "area": (20.0, 49.9),
                "depth": (2.0, 9.9),
                "points": (5, 14),
                "corrosion": (2, 3),
                "deformation": (10.0, 49.9)
            },
            {
                "level": "berat",
                "area": (50.0, 100.0),
                "depth": (10.0, 30.0),
                "points": (15, 30),
                "corrosion": (4, 5),
                "deformation": (50.0, 100.0)
            }
        ]
        
        records_to_create = []
        
        # Generate 20 records for each level (Total 60 > 10 requested)
        for rule in rules:
            for _ in range(20):
                records_to_create.append(generate_record(component_id, rule))
        
        # Shuffle records
        random.shuffle(records_to_create)
        
        # 3. Bulk Create Records
        success, errors, error_msgs = await damage_record_service.bulk_create(db, records_to_create)
        print(f"Seeding completed: {success} created, {errors} errors.")
        if errors > 0:
            print("Sample errors:", error_msgs[:3])
            
        # 4. Train Model
        print("\nTriggering model training...")
        try:
            result = await model_metrics_service.train_model(db, test_size=0.2, notes="Auto-trained after seeding")
            print("Model training successful!")
            print(f"Accuracy: {result['accuracy']:.2%}")
            print(f"Precision: {result['precision']:.2%}")
            print(f"Recall: {result['recall']:.2%}")
            print(f"F1 Score: {result['f1_score']:.2%}")
            print(f"Training Samples: {result['training_samples']}")
        except Exception as e:
            print(f"Model training failed: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_damage_records())
