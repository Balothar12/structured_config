
from structured_config.spec.config import Config, MakeScalarEntry, MakeListEntry, MakeCompositeEntry, MakeRequirements, ListValidator

import json

def run():
    spec = Config.composite(
        entries=[
            MakeCompositeEntry.basic(
                name="person",
                entries=[
                    MakeScalarEntry.typed(name="first_name", type=str),
                    MakeScalarEntry.typed(name="last_name", type=str),
                    MakeScalarEntry.typed(name="age", type=int),
                    MakeScalarEntry.typed(name="gender", type=str),
                ],
                requirements=MakeRequirements.required([
                    "first_name", 
                    "last_name", 
                    "age",
                    "gender"
                ]),
            ),
            MakeListEntry.basic(
                name="addresses",
                elements=Config.composite(
                    entries=[
                        MakeScalarEntry.typed(name="street", type=str),
                        MakeScalarEntry.typed(name="number", type=str),
                        MakeScalarEntry.typed(name="secondary", type=str),
                        MakeScalarEntry.typed(name="zip", type=str),
                        MakeScalarEntry.typed(name="city", type=str),
                    ],
                    requirements=MakeRequirements.mixed(required=[
                        "street", 
                        "number", 
                        "zip",
                        "city"
                    ], defaults={
                        "secondary": None,
                    }),
                ),
            )
        ]
    )

    data = {
        "person": {
            "first_name": "Max",
            "last_name": "Mustermann",
            "age": 39,
            "gender": "male",
        },
        "addresses": [
            {
                "street": "Musterstr.",
                "number": "111c",
                "zip": 12345,
                "city": "Berlin",
            }
        ]
    }

    print(json.dumps(
        spec.convert(data),
        indent=True,
        ensure_ascii=True,
    ))

    print(spec.specify())

if __name__ == "__main__":
    run()
