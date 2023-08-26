from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import PositionEnum
from src.container.container import Container
from src.domain.trade import Trade

from src.service_layer.indicators import Indicators
from src.service_layer.uow import MongoUnitOfWork

from src.logger import get_logger

logger = get_logger(__name__)


@inject
async def manage_closed_trades(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
) -> None:  # type: ignore
    async with uow:
        open_trades: list[Trade] = await uow.trade_repository.get_open_trades()
        for trade in open_trades:
            await update_trade_state(uow, trade)


async def update_trade_state(uow, trade):
    state, realised_pl = await uow.fxcm_connection.get_trade_state(
        trade.trade_id
    )
    if state is None:
        logger.error(f"Trade %s is not a valid trade" % trade.trade_id)

    if state != "OPEN":
        trade.position = PositionEnum.CLOSED
        trade.realised_pl = realised_pl
        trade.is_winner = True if realised_pl > 0 else False
        logger.warning(f"Trade %s closed by the broker" % trade.trade_id)
        await uow.trade_repository.save(trade)
