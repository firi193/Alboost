from sqlalchemy import Table, Column, Text, TIMESTAMP, ARRAY, MetaData
from sqlalchemy.dialects.postgresql import UUID
import uuid

metadata = MetaData()

onboarding_info = Table(
    "onboarding_info",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("created_at", TIMESTAMP, nullable=False),
    
    Column("brand_name", Text),
    Column("industry", Text),
    Column("product", Text),

    Column("voice", Text),
    Column("aesthetic", Text),

    Column("campaign_objective", Text),
    Column("campaign_type", Text),
    Column("urgency", Text),
    Column("channels", ARRAY(Text)),

    Column("age_range", Text),
    Column("location", Text),
    Column("gender", Text),
    Column("values", Text),
    Column("interests", Text),
    Column("behavior", Text),

    Column("brand_doc_vector_ids", ARRAY(Text)),
    Column("audience_doc_vector_ids", ARRAY(Text)),
    Column("form_vector_id", Text),
)
