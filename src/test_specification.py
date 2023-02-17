
from structured_config.spec.config import Config, MakeScalarEntry, MakeListEntry, MakeCompositeEntry, MakeRequirements

def run():
    spec = Config.composite(
        entries=[
            MakeCompositeEntry.basic(
                name="person",
                entries=[
                    MakeScalarEntry.basic(name="first_name", type=str),
                    MakeScalarEntry.basic(name="last_name", type=str),
                    MakeScalarEntry.basic(name="age", type=int),
                    MakeScalarEntry.basic(name="gender", type=str),
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
                        MakeScalarEntry.basic(name="street", type=str),
                        MakeScalarEntry.basic(name="number", type=str),
                        MakeScalarEntry.basic(name="secondary", type=str),
                        MakeScalarEntry.basic(name="zip", type=str),
                        MakeScalarEntry.basic(name="city", type=str),
                    ],
                    requirements=MakeRequirements.mixed(required=[
                        "street", 
                        "number", 
                        "zip",
                        "city"
                    ], defaults={
                        "secondary": None,
                    }),
                )
            )
        ]
    )

    print(spec.specify())

if __name__ == "__main__":
    run()
