# Proof of Concept for a Python Script as Document Object

## About

The motivation here is to enable the user to perform more complex calculations more easily.
Expressions in properties are powerful, but expressing more complex stuff becomes cumbersome,
hard to maintain/understand or even impossible.

The idea is to provide a new kind of document object, that has some input properties, performs
some calculations when rcomputed, and populates some output propeties. Those calculations are
provided as python code by the user.

The goal is not to "provide macros with the document". This could be maybe useful on its own,
but its a different story (which has also been discussed on the forum already).
The goal is to address those use cases that a custom WB could fulfill, but where its an overkill
to create such a thing; especially for one-off stuff.


## Security

Generally, embedding executable code in a document is dangerous!

Do not execute a script, unless the user has explicitly allowed it.
The allow-list is stored as part of the local FreeCAD settings
 - filename
 - script name (i.e. name of document object)
   - unlock them one by one, to "enforce" user to review
 - script hash
   - to prevent allowence of an earlier ~/downloads/test.fcstd to execute the new one
   - see https://docs.python.org/3/library/importlib.html#importlib.util.source_hash
 - timestamp

Yes, it still can be harmful, but its not more dangerous than 3rd party macros or workbenches.

## How to use

- Create a new Script object
  No shape, just props, i.e. "App::FeaturePython"
  - later, maybe different flavors (each with different template) could be offered
    - one with Shape, i.e. "Part::FeaturePython"
      - For PD: "PartDesign::FeaturePython", "PartDesign::FeatureAdditivePython"
    - one with 2D Shape, i.e. "Part::Part2DObjectPython"
    - add extension "Part::AttachExtensionPython"
- Add "Input" properties
  - using dynamic properties, later maybe via Wizzard or toolbar, too
  - just ordinary properties, nothing special.
  - Recommendation: use "Input" as category
- Add "Output" properties
  - using dynamic properties, later maybe via Wizzard, too
  - flag them `read-only` and `output`
  - Recommendation: use "Output" as category
- Edit script via build-in python editor ("macro ditor")
- Execution happens automatically on recalculation.
  - if unlocked, see &Security

## GUI

use the python icon in the document tree
 - use variants for scripts producing no shape, 3D shape or 2D shape
use a lock overlay icon if it's execution is not allowed
use the build-in python editor
use a task panel to set the `AllowExecution` check box and set in/out props

creating new Scripts automatically allows their execution
changing an unlocked script, does not lock it again

use various templates
add own templates (can we use pyyaml?, i.e. is it always available)
{
  Type: "Part::FeaturePython",
  InProps: [{Name: "InOne", Type: "App::PropertyFloat"}]
  OutProps: []
  Script: "def execute(obj): ...."
}


## How it works

The `onDocumentRestored` hook checks whether the script is unlocked or not.
The result is stored in the `IsUnlocked` (better `AllowExecution`?) transient, boolean, property.
We need to prevent this being overwritten by an Expression!
So maybe a property is not good, use python member instead (and don't serialize it)

When the proxy's `execute` method is called, it checks wether it is unlocked.
If unlocked, then the code is loaded as a module, to execute in its own namespace.
Code is in the `Definition` (or `Script`?) string property (similar to `Text` of "App::Text" objects)
This module instance may be cached on a transient property
Next it is checked whether the module has an `execute` attribtue.
If yes, it is called with the document object as argument.
On document save, if the scipt is unlocked, save its name/document/hash in the allow-list

```py
src = "def execute(obj): pass"
code = compile(src, "DynamicProxy001", 'exec')
mod = type(sys)("DynamicProxy001")
# maybe better use importlib.machinery.ModuleSpec?
# and https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
exec(code, mod.__dict__)
mod.execute(obj)
```

https://docs.python.org/3/library/modules.html
https://docs.python.org/3/library/functions.html#compile
https://docs.python.org/3/library/zipimport.html
https://github.com/python/cpython/blob/3.11/Lib/zipimport.py#L271

## Script Template
```py
import FreeCAD as App
import Part
from FreeCAD import Base

# TODO: get a logger? use FreeCAD.Console directly? use magic build in Log/Err/Wrn? use FreeCAD.Logger?

def execute(obj):
    obj.SomeOutput = obj.SomeInput**2
```

## Design Rationale

Using properties make it easier for the user to "parametrizise" her scripts

Using properties make it easier to interact with other objects via expressions

Using in/out properties allows FreeCAD to track dependencies for recalculation

Using a dedicated method as entry point
 - allows explicit argument passing, e.g. a `obj`
 - gives more freedom in code organization, e.g. call methods defined *later*
 - makes the code cleaner
 - makes it future proof, as other hooks could be exposed, too.

## Showcase

something like this https://forum.freecad.org/viewtopic.php?t=65875

## meta
How to call this?
 - freecad.scripts? maybe too generic
 - freecad.script? maybe too generic
 - freecad.pyobj? maybe too generic
 - freecad.pydocobj? too weired
 - freecad.pysdob? (Python Scripts as Document OBject) still weired, but pronoucable
 - "scripted document objects"?
 - "dynamic proxy"? in fact, its similar to what the "dynamic data" WB offered...
 - "scripting host", "scripted proxy", "scripted object

### Related

Mnesarco's Utils for FreeCAD
 - https://forum.freecad.org/viewtopic.php?f=22&t=54026
 - https://github.com/mnesarco/FreeCAD_Utils

Idea from onkk: A "Scripted object" in FreeCAD maybe a separate WB.
 - https://forum.freecad.org/viewtopic.php?t=76193

## Running the Tests

On macOS:
```sh
~/src/freecad.scripts$ /Applications/FreeCAD.app/Contents/MacOS/FreeCAD --python-path . --console --run-test "freecad.scripts.tests"
```
