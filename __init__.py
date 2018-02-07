# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

from . import ScalableExtraPrime
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("ScalableExtraPrime")

def getMetaData():
    return {}

def register(app):
    return {"extension": ScalableExtraPrime.ScalableExtraPrime()}
