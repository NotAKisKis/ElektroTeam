from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Literal

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(
        default=None,
        min_length=1, 
        max_length=1000
    )
    price_grosz: int = Field(ge=0)
    stock: int = Field(ge=0)
    category_id: int = Field(ge=1)
    discount_type: Literal["none", "percent", "fixed"] = "none"
    discount_value: int = Field(ge=0, default=0)
    image_url: str | None = Field(
        default=None,
        min_length=1,
        max_length=2048
    )


    @model_validator(mode="after")
    def validate_discount(self):
        if self.discount_type == "percent" and self.discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100%")

        if self.discount_type == "fixed" and self.discount_value > self.price_grosz:
            raise ValueError("Fixed discount cannot exceed product price")

        if self.discount_type == "none" and self.discount_value != 0:
            raise ValueError("Discount value must be 0 when discount type is none")

        return self

    @field_validator("name", "description", "image_url")
    @classmethod
    def validate_text(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")

        return value