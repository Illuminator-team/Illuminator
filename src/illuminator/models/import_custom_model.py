import illuminator.models

def import_custom_model(Model)-> None:
    """
    Imports a custom model from a specified file path and adds it to the Illuminator models.
    Parameters
    ----------
    Model: Class
        A custom model class that inherits from Illuminator's base model class.
    Returns
    -------
    None
    """

    setattr(illuminator.models, Model.__name__, Model)
    illuminator.models.__all__.append(Model.__name__)
    return