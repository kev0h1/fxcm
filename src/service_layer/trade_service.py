from src.domain.trade import Trade
from src.service_layer.uow import MongoUnitOfWork


class TradeService:
    def __init__(self, uow: MongoUnitOfWork) -> None:
        self._uow: MongoUnitOfWork = uow

    async def create_trade_from_data_frame(self):
        fxcm_position = self.uow.fxcm_connection.get_open_positions()
        trade_id: str = fxcm_position.iloc[-1]["tradeId"]

        if not await self.uow.trade_repository.get_trade_by_trade_id(
            trade_id=trade_id
        ):
            trade = Trade(
                trade_id=trade_id,
                position_size=fxcm_position["amountK"],
                stop=fxcm_position["stop"],
                limit=fxcm_position["limit"],
                is_buy=fxcm_position["isBuy"],
            )
            await self.uow.trade_repository.save(trade)
