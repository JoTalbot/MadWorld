"""B3 Advanced Economy read-model services."""
from uuid import UUID
from sqlalchemy import text
from app.application.errors import NotFound


def regional_state(conn, region_id: UUID):
    row=conn.execute(text("SELECT * FROM regional_economic_state WHERE region_id=:r"),{"r":region_id}).mappings().first()
    if row is None: raise NotFound("regional economic state not found")
    return dict(row)


def market_metrics(conn, region_id: UUID, item_id: UUID):
    r=conn.execute(text("SELECT COALESCE(SUM(quantity),0) volume,COALESCE(SUM(total_amount),0) value,COALESCE(SUM(total_amount)::numeric/NULLIF(SUM(quantity),0),0) vwap FROM market_trade_history WHERE region_id=:r AND item_definition_id=:i AND created_at>=now()-interval '24 hours'"),{"r":region_id,"i":item_id}).mappings().one()
    b=conn.execute(text("SELECT COALESCE(SUM(CASE WHEN side='buy' THEN remaining_quantity ELSE 0 END),0) bids,COALESCE(SUM(CASE WHEN side='sell' THEN remaining_quantity ELSE 0 END),0) asks FROM market_orders WHERE region_id=:r AND item_definition_id=:i AND status='open'"),{"r":region_id,"i":item_id}).mappings().one()
    return {"volume_24h":int(r["volume"]),"value_24h":int(r["value"]),"vwap_24h":int(r["vwap"]),"bid_volume":int(b["bids"]),"ask_volume":int(b["asks"])}
