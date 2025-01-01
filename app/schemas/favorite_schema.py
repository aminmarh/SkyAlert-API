from marshmallow import Schema, fields, validate


class CityNameType(fields.Str):
    """Type personnalisé pour valider les noms de ville."""

    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Regexp(
                r"^[a-zA-Z\s]+$",
                error="City name must be a string containing only letters and spaces",
            )
        ]
        kwargs["description"] = "Name of the city"
        super().__init__(*args, **kwargs)


class AddFavoriteCitySchema(Schema):
    """Schéma pour ajouter une ville aux favoris."""

    city = CityNameType(required=True)


class DeleteFavoriteCitySchema(Schema):
    """Schéma pour supprimer une ville des favoris."""

    city = CityNameType(required=True)
