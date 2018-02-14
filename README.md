### This plugin is still in testing.
# ScalableExtraPrime

A Cura plugin to add a scaling amount of extra filament extrusion after a travel.

Filament can leak out of the nozzle during a long travel, especially on larger nozzles. 
This causes under-extrusion when printing starts again at the end of the travel. Adding extra filament to prime the nozzle after the travel can eliminate the issue,
but the existing option in Cura sets a single amount of prime on any retraction, no matter how long the travel is. This plugin addresses this issue by
 scaling the amount of extra filament to prime the nozzle with based on the distance that is traveled between extrusions.
 
This plugin modifies the gcode that is created by Cura by tracking all travel moves and inserting additional filament extrusion at the end of the move.

The amount of filament added is scaled linearly, roughly using this equation:

extra filament = ((actual_travel - min_travel) / ( max_travel - min_travel)) * (max_prime - min_prime) + min_prime

### Settings

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
