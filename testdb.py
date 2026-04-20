from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres.esjtvitlrhetrspnliju:THPTHTTTNT88888888@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres")

with engine.connect() as conn:
    print("OK")