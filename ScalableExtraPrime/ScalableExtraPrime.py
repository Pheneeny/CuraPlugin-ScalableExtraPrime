# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

import os, json, re

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger

from math import sqrt
from . import ScalableExtraPrimeAdjuster

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("ScalableExtraPrime")


class ScalableExtraPrime(Extension):
    def __init__(self):
        super().__init__()

        self._application = Application.getInstance()

        self._i18n_catalog = None

        self._min_travel_key = "scalable_prime_min_travel"
        self._min_travel_dict = {
            "label": "Extra Prime Min Travel",
            "description": "Minimum distance of travel before adding extra prime",
            "type": "float",
            "unit": "mm",
            "default_value": 0,
            "minimum_value": 0,
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }

        self._max_travel_key = "scalable_prime_max_travel"
        self._max_travel_dict = {
            "label": "Extra Prime Max Travel",
            "description": "Maximum travel distance to scale extra prime",
            "type": "float",
            "unit": "mm",
            "default_value": 200,
            "minimum_value": "scalable_prime_min_travel",
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        self._min_prime_key = "scalable_prime_min_amount"
        self._min_prime_dict = {
            "label": "Min Extra Prime",
            "description": "Minimum amount of filament to add when priming after a retraction or travel",
            "type": "float",
            "unit": "mm",
            "default_value": 0,
            "minimum_value": 0,
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        self._max_prime_key = "scalable_prime_max_amount"
        self._max_prime_dict = {
            "label": "Max Extra Prime",
            "description": "Maximum amount of filament to add when priming after a retraction or travel",
            "type": "float",
            "unit": "mm",
            "default_value": 0,
            "minimum_value": "scalable_prime_min_amount",
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        self._enable_all_travels_key = "scalable_prime_enable_all_travels"
        self._enable_all_travels_dict = {
            "label": "Enable For All Travels",
            "description": "Disabling this sets the slicer to only add extra filament after a retraction. If combing is enabled, travels over infill may not retract, and won\'t trigger extra prime.",
            "type": "bool",
            "unit": "",
            "default_value": True,
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }
        self._enable_only_travels_key = "scalable_prime_enable_only_travels"
        self._enable_only_travels_dict = {
            "label": "Enable For Only Travels",
            "description": "Enabling this sets the slicer to only add filament after regular travel moves (i.e. moves without a retraction). This is so that you can use this plugin in combination with the Retraction Extra Prime Amount setting.",
            "type": "bool",
            "unit": "",
            "default_value": False,
            "enabled": "scalable_prime_enable",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }
        self._setting_key = "scalable_prime_enable"
        self._setting_dict = {
            "label": "Enable Scalable Extra Prime",
            "description": "Adds extra filament extrusion after a retraction or travel, scaling it based on the distance of the travel. This can help resolve filament oozing out during a travel, leaving a void in the nozzle and causing under extrusion when extrusion resumes",
            "type": "bool",
            "unit": "",
            "default_value": False,
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }

        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

        self._application.globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
        self._onGlobalContainerStackChanged()

        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)


    def _onContainerLoadComplete(self, container_id):
        container = ContainerRegistry.getInstance().findContainers(id=container_id)[0]
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        self.create_and_attach_setting(container, self._setting_key, self._setting_dict, "travel")
        self.create_and_attach_setting(container, self._min_travel_key, self._min_travel_dict, self._setting_key)
        self.create_and_attach_setting(container, self._max_travel_key, self._max_travel_dict, self._setting_key)
        self.create_and_attach_setting(container, self._min_prime_key, self._min_prime_dict, self._setting_key)
        self.create_and_attach_setting(container, self._max_prime_key, self._max_prime_dict, self._setting_key)
        self.create_and_attach_setting(container, self._enable_all_travels_key, self._enable_all_travels_dict, self._setting_key)
        self.create_and_attach_setting(container, self._enable_only_travels_key, self._enable_only_travels_dict, self._setting_key)

    def _onGlobalContainerStackChanged(self):
        self._global_container_stack = self._application.getGlobalContainerStack()

    def _filterGcode(self, output_device):

        scene = self._application.getController().getScene()
        # get settings from Cura
        scalable_enabled = self._global_container_stack.getProperty(self._setting_key, "value")
        if not scalable_enabled:
            return

        min_travel = self._global_container_stack.getProperty(self._min_travel_key, "value")
        max_travel = self._global_container_stack.getProperty(self._max_travel_key, "value")
        min_prime = self._global_container_stack.getProperty(self._min_prime_key, "value")
        max_prime = self._global_container_stack.getProperty(self._max_prime_key, "value")
        extra_prime_without_retraction = self._global_container_stack.getProperty(self._enable_all_travels_key, "value")
        extra_prime_only_travels = self._global_container_stack.getProperty(self._enable_only_travels_key, "value")

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict:  # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return

        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]
            if len(gcode_list) < 2:
                Logger.log("w", "Plate %s does not contain any layers", plate_id)
                continue

            if ";EOFFSETPROCESSED" not in gcode_list[0]:
                gcode_list = ScalableExtraPrimeAdjuster.parse_and_adjust_gcode(gcode_list, min_travel, max_travel, min_prime, max_prime, extra_prime_without_retraction, extra_prime_only_travels)

                gcode_list[0] += ";EOFFSETPROCESSED\n"
                gcode_dict[plate_id] = gcode_list
            else:
                Logger.log("d", "Plate %s has already been processed", plate_id)
                continue

            setattr(scene, "gcode_dict", gcode_dict)

    def create_and_attach_setting(self, container, setting_key, setting_dict, parent):
        parent_category = container.findDefinitions(key=parent)
        definition = container.findDefinitions(key=setting_key)
        if parent_category and not definition:
            # this machine doesn't have a scalable extra prime setting yet
            parent_category = parent_category[0]
            setting_definition = SettingDefinition(setting_key, container, parent_category, self._i18n_catalog)
            setting_definition.deserialize(setting_dict)

            parent_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition
            container._updateRelations(setting_definition)



