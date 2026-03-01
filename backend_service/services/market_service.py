from models import MarketPrice
from datetime import datetime

def create_market_entry(db, commodity: str, price: float, market_name: str = None):
    rec = MarketPrice(commodity=commodity, modal_price=price, market_name=market_name, created_at=datetime.utcnow())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
