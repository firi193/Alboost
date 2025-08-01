from sqlalchemy import text
from datetime import datetime
import uuid
import os
import sys

# Handle imports for different execution contexts
try:
    from .connect import engine, SessionLocal
    from .models import onboarding_info
except ImportError:
    # Fallback for direct execution or when imported from different paths
    try:
        from connect import engine, SessionLocal
        from models import onboarding_info
    except ImportError:
        # Add the current directory to path and try again
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from connect import engine, SessionLocal
        from models import onboarding_info

def save_onboarding_data(
    brand_name=None,
    industry=None,
    product=None,
    voice=None,
    aesthetic=None,
    campaign_objective=None,
    campaign_type=None,
    urgency=None,
    channels=None,
    age_range=None,
    location=None,
    gender=None,
    values=None,
    interests=None,
    behavior=None,
    brand_doc_vector_ids=None,
    audience_doc_vector_ids=None,
    form_vector_id=None
):
    """
    Save onboarding information to the database
    """
    try:
        with SessionLocal() as session:
            # Create the insert statement
            insert_stmt = onboarding_info.insert().values(
                id=uuid.uuid4(),
                created_at=datetime.utcnow(),
                brand_name=brand_name,
                industry=industry,
                product=product,
                voice=voice,
                aesthetic=aesthetic,
                campaign_objective=campaign_objective,
                campaign_type=campaign_type,
                urgency=urgency,
                channels=channels,
                age_range=age_range,
                location=location,
                gender=gender,
                values=values,
                interests=interests,
                behavior=behavior,
                brand_doc_vector_ids=brand_doc_vector_ids or [],
                audience_doc_vector_ids=audience_doc_vector_ids or [],
                form_vector_id=form_vector_id
            )
            
            result = session.execute(insert_stmt)
            session.commit()
            
            return {
                "success": True,
                "id": result.inserted_primary_key[0],
                "message": "Onboarding data saved successfully"
            }
            
    except Exception as e:
        print(f"Error saving onboarding data: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save onboarding data"
        }

def get_onboarding_data(onboarding_id=None):
    """
    Retrieve onboarding information from the database
    """
    try:
        with SessionLocal() as session:
            if onboarding_id:
                # Get specific onboarding record
                query = text("SELECT * FROM onboarding_info WHERE id = :id")
                result = session.execute(query, {"id": onboarding_id})
                return result.fetchone()
            else:
                # Get all onboarding records
                query = text("SELECT * FROM onboarding_info ORDER BY created_at DESC")
                result = session.execute(query)
                return result.fetchall()
                
    except Exception as e:
        print(f"Error retrieving onboarding data: {e}")
        return None 