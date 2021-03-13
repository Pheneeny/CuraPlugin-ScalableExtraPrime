# ScalableExtraPrime

A Cura plugin to add a scaling amount of extra filament extrusion after a travel.

Filament can leak out of the nozzle during a long travel, especially on larger nozzles. 
This causes under-extrusion when printing starts again at the end of the travel. Adding extra filament to prime the nozzle after the travel can eliminate the issue,
but the existing option in Cura sets a single amount of prime, only if there is a retraction, no matter how long the travel is. This plugin addresses this issue by
 scaling the amount of extra filament to prime the nozzle with based on the distance that is traveled between extrusions, and (optionally) applying it whether there was a retraction or not.
 
This plugin modifies the gcode that is created by Cura by tracking all travel moves and inserting additional filament extrusion at the end of the move. If you also use the built in [Retraction Extra Prime Amount] setting, this plugin will add additional filament on top of the extra added by that setting. There should be no reason to use [Retraction Extra Prime Amount] when using this plugin.

The amount of filament added is scaled linearly, roughly using this equation:

extra filament = ((actual_travel - min_travel) / ( max_travel - min_travel)) * (max_prime - min_prime) + min_prime

Original concept and version by github user [Pheneey](https://github.com/Pheneeny)
Updated and maintained to support newer versions of Cura.

### Settings
* Located in the Travel category

##### Enable Scalable Extra Prime
* Enables scalable extra prime. If this is false, no extra prime is added by the plugin  

##### Extra Prime Min Travel
* The minimum travel distance required before adding extra prime 

##### Extra Prime Max Travel
* The maximum travel distance used to calculate extra prime. If a travel occurs that is longer than this, the extra distance is ignored and [Max Extra Prime] filament will be added

##### Min Extra Prime
* The minimum amount of filament to add after a travel of at least [Extra Prime Min Travel] distance

##### Max Extra Prime
* The maximum amount of filament to add after a travel

##### Enable For All Travels
* Enable scaled extra prime for all travels. If this is disabled, extra prime will only be added after retractions

### Supported Cura Versions
This has been tested on Cura 3.2.0. through 4.7.1

### Installation
MacOS: Copy plugin folder to /Users/USERNAME/Library/Application Support/cura/VERSION/plugins
Windows:

Alternatively you can download the following [curapackage](https://github.com/Funkton/CuraPlugin-ScalableExtraPrime/releases/download/1.0.2/ScalableExtraPrime-v7.3.0.curapackage) file Cura 4.7, drag and drop into Cura, then restart.

