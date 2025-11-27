import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Optional

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, UnicodeSetAttribute
from pynamodb.exceptions import UpdateError
from pynamodb.models import Model

from ddb.datetime_attribute import DateTimeAttribute
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
    domain: str
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

    def increment_uses(self) -> bool:
        """リンクの使用回数をインクリメントする"""
        try:
            self._model.update(
                actions=[DelibirdLinkTableModel.uses.add(1)],
                condition=(DelibirdLinkTableModel.uses < self.max_uses) if self.max_uses else None
            )
        except UpdateError as e:
            if e.cause_response_code == "ConditionalCheckFailedException":
                return False
            raise e
        self.uses += 1
        return True


class DelibirdLinkTableModel(Model):
    class Meta:
        table_name = os.environ["LINK_TABLE_NAME"]
        region = _REGION

    domain = UnicodeAttribute(hash_key=True)
    slug = UnicodeAttribute(range_key=True)

    created_at = DateTimeAttribute(null=False)
    origin = UnicodeAttribute(null=False)
    status = NumberAttribute(null=False)
    disabled = BooleanAttribute(null=False, default=False)
    uses = NumberAttribute(null=False, default=0)

    expiration_date = DateTimeAttribute(null=True)
    expired_origin = UnicodeAttribute(null=True)
    query_omit = BooleanAttribute(null=False, default=True)
    query_whitelist = UnicodeSetAttribute(null=True)
    max_uses = NumberAttribute(null=True)

    @classmethod
    def get_from_request(cls, domain: str, slug: str) -> Optional[DelibirdLink]:
        try:
            result = cls.get(hash_key=domain, range_key=slug, consistent_read=True)
        except cls.DoesNotExist:
            return None
        except Exception as e:
            logger.exception(f"Failed to fetch delibird link data for domain: {domain}, slug: {slug}, Table: {cls.Meta.table_name}")
            raise RuntimeError('Failed to fetch delibird link data.') from e

        return DelibirdLink(
            _model=result,
            domain=result.domain,
            link_slug=result.slug,
            link_origin=result.origin,
            status=HTTPStatus(result.status),
            disabled=result.disabled,
            uses=int(result.uses),
            expiration_date=result.expiration_date,
            expired_origin=result.expired_origin,
            query_omit=result.query_omit,
            query_whitelist=result.query_whitelist,
            max_uses=int(result.max_uses) if result.max_uses is not None else None
        )

    def __str__(self):
        try:
            return json.dumps({k: list(v.values())[0] for k, v in self.serialize().items()}, indent=2)
        except Exception:
            return super().__str__()
