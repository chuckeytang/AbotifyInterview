from typing_extensions import Annotated
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

PyObjectId = Annotated[
    ObjectId,
    PlainSerializer(
        lambda s: str(s),
        return_type=str,
        when_used="json",
    ),
]


class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    def model_dump(self, **kwargs):
        """
        Override the default `.dict()` method to exclude the 'id' field automatically,
        unless explicitly included.
        """
        return super().model_dump(**kwargs, exclude={"id"})
