import hashlib
import hmac
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Optional

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, UnicodeSetAttribute
from pynamodb.constants import NULL
from pynamodb.exceptions import UpdateError
from pynamodb.expressions.operand import Path
from pynamodb.models import Model

from ddb.datetime_attribute import DateTimeAttribute
from util.date_util import get_jst_datetime_now, as_jst
from util.logger_util import setup_logger

_REGION = os.environ["AWS_REGION"]
_MAX_SLUG_LENGTH = 255
_SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]+(?:/[a-zA-Z0-9\-_]+)*$', re.ASCII)

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

    memo: str = ""
    tag: set[str] = None

    expiration_date: Optional[datetime] = None
    expired_origin: Optional[str] = None

    _passphrase: Optional[str] = None

    query_omit: bool = False
    query_whitelist: set[str] = None

    max_uses: Optional[int] = None

    @staticmethod
    def _validation(link: "DelibirdLink") -> None:
        # domain
        if not link.domain:
            raise ValueError("Domain is required.")
        # slug
        if (not (slug := link.link_slug)) or (len(slug) > _MAX_SLUG_LENGTH) or (not _SLUG_PATTERN.fullmatch(slug)):
            raise ValueError(f"Invalid slug: {slug}")
        # origin
        if not link.link_origin:
            raise ValueError("Origin is required.")
        # status
        if not link.status.is_redirection:
            raise ValueError(f"Status code {link.status} is not a redirection status.")

    def __post_init__(self):
        if self.query_whitelist is None:
            self.query_whitelist = set()
        if self.tag is None:
            self.tag = set()
        DelibirdLink._validation(self)

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
                condition=(DelibirdLinkTableModel.max_uses.does_not_exist()) |
                          (Path(DelibirdLinkTableModel.max_uses).is_type(NULL)) |
                          (DelibirdLinkTableModel.uses < DelibirdLinkTableModel.max_uses)
            )
        except UpdateError as e:
            if e.cause_response_code == "ConditionalCheckFailedException":
                return False
            raise e
        self.uses += 1
        return True

    def is_protected(self) -> bool:
        return self._passphrase is not None

    def validate_challenge(self, nonce: str, challenge: str) -> bool:
        if not self.is_protected():
            raise ValueError("Link is not protected.")
        if not nonce:
            raise ValueError("Nonce is required.")
        expected = hashlib.sha256(f"{self._passphrase}#{nonce}".encode()).hexdigest()
        return hmac.compare_digest(challenge, expected)

    @staticmethod
    def from_model(model: "DelibirdLinkTableModel") -> "DelibirdLink":
        return DelibirdLink(
            _model=model,
            domain=model.domain,
            link_slug=model.slug,
            link_origin=model.origin,
            status=HTTPStatus(model.status),
            disabled=model.disabled,
            uses=int(model.uses),
            memo=model.memo,
            tag=set(model.tag) if model.tag is not None else None,
            expiration_date=as_jst(model.expiration_date) if model.expiration_date is not None else None,
            expired_origin=model.expired_origin,
            _passphrase=model.passphrase,
            query_omit=model.query_omit,
            query_whitelist=model.query_whitelist,
            max_uses=int(model.max_uses) if model.max_uses is not None else None
        )


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
    memo = UnicodeAttribute(null=False, default="")
    tag = UnicodeSetAttribute(null=True)

    expiration_date = DateTimeAttribute(null=True)
    expired_origin = UnicodeAttribute(null=True)
    passphrase = UnicodeAttribute(null=True)
    query_omit = BooleanAttribute(null=False, default=True)
    query_whitelist = UnicodeSetAttribute(null=True)
    max_uses = NumberAttribute(null=True)

    @classmethod
    def get_from_request(cls, domain: str, slug: str) -> Optional[DelibirdLink]:
        try:
            result = cls.get(hash_key=domain, range_key=slug, consistent_read=True)
        except cls.DoesNotExist:
            return None
        return DelibirdLink.from_model(result)

    @classmethod
    def scan_domain(cls, domain: str) -> list["DelibirdLink"]:
        try:
            return [DelibirdLink.from_model(model) for model in cls.query(hash_key=domain, consistent_read=True)]
        except Exception as e:
            logger.exception(f"Failed to scan delibird link data for domain: {domain}, Table: {cls.Meta.table_name}")
            raise RuntimeError('Failed to scan delibird link data.') from e

    def __str__(self):
        try:
            return json.dumps({k: list(v.values())[0] for k, v in self.serialize().items()}, indent=2)
        except Exception:
            return super().__str__()
