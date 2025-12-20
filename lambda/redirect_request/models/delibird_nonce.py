import os
from datetime import datetime
from typing import Optional

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.constants import NULL
from pynamodb.exceptions import UpdateError
from pynamodb.expressions.operand import Path
from pynamodb.models import Model

from ddb.datetime_attribute import DateTimeAttribute
from util.date_util import get_jst_datetime_now

_REGION = os.environ["AWS_REGION"]


class DelibirdNonceTableModel(Model):
    class Meta:
        table_name = os.environ["NONCE_TABLE_NAME"]
        region = _REGION

    nonce = UnicodeAttribute(hash_key=True)
    expired_timestamp = NumberAttribute(null=False)

    domain = UnicodeAttribute(null=False)
    slug = UnicodeAttribute(null=False)
    used_at = DateTimeAttribute(null=True, default=None)

    def is_active(self) -> bool:
        if self.used_at is not None:
            # 使用済み
            return False
        if self.expired_timestamp <= get_jst_datetime_now().timestamp():
            # 期限切れ
            return False
        return True

    def mark_used(self) -> tuple[bool, Optional[datetime]]:
        if not self.is_active():
            # usedな状態でmark_usedされていないか、呼び出し時点で期限切れしていないか
            return False, None
        try:
            self.update(
                actions=[DelibirdNonceTableModel.used_at.set(int(get_jst_datetime_now().timestamp()))],
                condition=(DelibirdNonceTableModel.used_at.does_not_exist()) |
                          (Path(DelibirdNonceTableModel.used_at).is_type(NULL))
            )
        except UpdateError as e:
            if e.cause_response_code == "ConditionalCheckFailedException":
                return False, None
            raise e
        return True, now
