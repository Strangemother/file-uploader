# Tools

Functions to action tasks on files and directories, such as "copy".
A _tool_ may interact with an entity through several methods:


+ Right Click (Alt Menu)
+ Text Hightlight
+ Box tool
+ View Button


## Alt Menu

A user may opt to use the view alt-menu. This can manifest as a _right click_
to present chosen functions.

+ Open (Directory)
    + Current Tab
    + In new tab
    + New Window
+ Cut: path to box
+ Copy
    + Name: Text to clipboard
    + Path: Text to clipboard
    + File: path to box
+ Paste:
    + [cut|copy box] to here
    > List of historical cuts|copies


## Text Highlight

A User may _highlight_ a selected element, options should spawn around the selection. This is similar to the alt-menu.


## Box Tool

A _box_ groups many arbitrary paths under one label. _actions_ on the box can
be applied; such as a "clipboard" box collects all "copy" actions.
A "paste" on the box be another tool.


## View Button

A _button_ may exist in the explorer or a file-content page. It actions through user selection.


---

# Considerations

A tool may need to interact with the UI immediately. e.g. the _cut_ tool will flag the UI element. A _Paste_ tool will add an entity to a view.

Some actions are _pre_ and _post_ steps for a the process.
E.g. A "copy" should _accept_ a path and store it. A "Paste" should _accept_ a destination, and its target.

---

# Actions

Some actions the tools should perform:

    copy | paste -> duplicate
    cut  | paste -> move

---

# Move

A Primary function is "Move", where we accept a file or DIR to and phyically
move the file. This can be accessed through several methods:

# Action `Copy -> Paste`.

A copy records the given paths, the 'paste' finalises the move.

A user may access:

+  _alt menu_ copy
+  UI button "copy" function
+  UI button "move" function
+ a CTRL+P Panel "move" -> [input dest.]

## Copy

The copy _registers_ the path in a box. This should be the automated 'clipping'
box of some description.

Given there is information in _a box_, the UI can present a "paste" button. This serves the "move".

## Move

Move is the entire process and is the fundamental function for the copying.

If _move_ is performed without a copy, the UI should request the destination.
A user should be allowed to:

+ Input a path though an input field
+ navigate to a destination and set "here".