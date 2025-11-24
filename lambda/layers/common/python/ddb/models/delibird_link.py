import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Optional

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute, UnicodeSetAttribute
from pynamodb.models import Model

from util.date_util import get_jst_datetime_now
from util.logger_util import setup_logger

_REGION = os.environ["AWS_REGION"]

logger = setup_logger("delibird.link_table", logging.INFO)


class DelibirdLinkInactiveStatus(Enum):
    DISABLED = auto()
    EXPIRED = auto()
    MAX_USES_EXCEEDED = auto()


@dataclass
class DelibirdLinkInactiveReason:
    status: DelibirdLinkInactiveStatus
    reason: str


@dataclass
class DelibirdLink:
    _model: "DelibirdLinkTableModel"
    link_slug: str
    link_origin: str
    status: HTTPStatus
    disabled: bool = False
    uses: int = 0

    expiration_date: Optional[datetime] = None
    expired_origin: Optional[str] = None

    query_omit: bool = False
    query_whitelist: set[str] = None

    max_uses: Optional[int] = None

    def __post_init__(self):
        if self.query_whitelist is None:
            self.query_whitelist = set()

    def check_active(self) -> tuple[bool, Optional[DelibirdLinkInactiveReason]]:
        if self.disabled:
            return False, DelibirdLinkInactiveReason(
                status=DelibirdLinkInactiveStatus.DISABLED, reason="Link is disabled.")
        if (self.expiration_date is not None) and (self.expiration_date < get_jst_datetime_now()):
            return False, DelibirdLinkInactiveReason(
                status=DelibirdLinkInactiveStatus.EXPIRED, reason=f"Link is expired at {self.expiration_date}.")
        if (self.max_uses is not None) and (self.uses >= self.max_uses):
            return False, DelibirdLinkInactiveReason(
                status=DelibirdLinkInactiveStatus.MAX_USES_EXCEEDED,
                reason=f"Link has exceeded max uses: {self.max_uses}, current uses: {self.uses}.")
        return True, None

    def increment_uses(self) -> None:
        """リンクの使用回数をインクリメントする"""
        self._model.update(
            actions=[
                DelibirdLinkTableModel.uses.add(1)
            ]
        )
        self.uses += 1


class DelibirdLinkTableModel(Model):
    class Meta:
        table_name = os.environ["LINK_TABLE_NAME"]
        region = _REGION

    slug = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)

    origin = UnicodeAttribute(null=False)
    status = NumberAttribute(null=False)
    disabled = BooleanAttribute(null=False, default=False)
    uses = NumberAttribute(null=False, default=0)

    expiration_date = UTCDateTimeAttribute(null=True)
    expired_origin = UnicodeAttribute(null=True)
    query_omit = BooleanAttribute(null=False, default=False)
    query_whitelist = UnicodeSetAttribute(null=True)
    max_uses = NumberAttribute(null=True)

    @classmethod
    def get_by_slug(cls, slug: str) -> Optional[DelibirdLink]:
        try:
            results = list(cls.query(
                hash_key=slug,
                filter_condition=(cls.disabled == False),
                consistent_read=True
            ))
            if not results:
                return None

            if len(results) == 1:
                result = results[0]
            else:
                result = max(results, key=lambda x: x.created_at)

            return DelibirdLink(
                _model=result,
                link_slug=result.slug,
                link_origin=result.origin,
                status=HTTPStatus(result.status),
                disabled=result.disabled,
                uses=result.uses,
                expiration_date=result.expiration_date,
                expired_origin=result.expired_origin,
                query_omit=result.query_omit,
                query_whitelist=result.query_whitelist,
                max_uses=result.max_uses
            )
        except Exception as e:
            logger.exception(f"Failed to fetch delibird link data for slug: {slug}, Table: {cls.Meta.table_name}")
            raise RuntimeError('Failed to fetch delibird link data.') from e
