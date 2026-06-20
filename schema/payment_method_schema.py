from typing import Optional
from pydantic import BaseModel, ConfigDict

from model.payment_method_model import MethodType


class PaymentMethodRequest(BaseModel):
    method_name: str
    method_type: MethodType = MethodType.OTHER
    method_description: Optional[str] = None


class PaymentMethodResponse(PaymentMethodRequest):
    model_config = ConfigDict(from_attributes=True)

    method_id: int