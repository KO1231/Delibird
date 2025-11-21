import logging
import os
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.models import Model
from util.logger_util import setup_logger

_REGION = os.environ["AWS_REGION"]

logger = setup_logger("delibird.link_table", logging.INFO)


@dataclass
class DelibirdLink:
    link_slug: str
    link_origin: str
    status: HTTPStatus
    disabled: bool = False

    # TODO expiration_date: Optional[datetime] = None
    # TODO max_uses: Optional[int] = None
    # TODO uses: Optional[int] = None
    # TODO expired_url: Optional[str] = None

    # TODO query_omit: bool = False
    # TODO query_whitelist: Optional[set[str]] = None


class DelibirdLinkTableModel(Model):
    class Meta:
        table_name = os.environ["LINK_TABLE_NAME"]
        region = _REGION

    slug = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)

    origin = UnicodeAttribute(null=False)
    status = NumberAttribute(null=False)
    disabled = BooleanAttribute(null=False, default=False)

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
                link_slug=result.slug,
                link_origin=result.origin,
                status=HTTPStatus(result.status),
                disabled=result.disabled
            )
        except Exception as e:
            logger.exception(f"Failed to fetch delibird link data for slug: {slug}, Table: {cls.Meta.table_name}")
            raise RuntimeError('Failed to fetch delibird link data.') from e
