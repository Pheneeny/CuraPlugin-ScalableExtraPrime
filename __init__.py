# Copyright (c) 2018 Pheneeny
# The LinearExtraPrime is released under the terms of the AGPLv3 or higher.

from . import LinearExtraPrime
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("LinearExtraPrime")

def getMetaData():
    return {}

def register(app):
    return {"extension": LinearExtraPrime.LinearExtraPrime()}
