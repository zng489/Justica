class ExtraNodeSerializer:
    def __init__(self, obj_or_objs, many=False):
        self.many = many
        self.objs = list(obj_or_objs) if self.many else [obj_or_objs]

    @property
    def data(self):
        result = []
        for obj in self.objs:
            properties = {key: value for key, value in obj.properties.items() if key != "extra"}
            result.append(
                {
                    "id": obj.uuid,
                    "group": obj.entity.name,
                    "extra": obj.properties.get("extra", {}),
                    "properties": properties,
                    "label": obj._create_label(raw_properties=obj.raw_properties),
                }
            )
        return result if self.many else result[0]
