# Pascal

## Description
Small app to plot Pascal-like triangles. 

Instead of using the recursion:

`x_i,j = x_{i-1,j-1} + x_{i-1,j}`

where the `x` are `ints`, the update formula:

`x_i,j = (a*x_{i-1,j-1} + b*x_{i-1,j}) mod m`

is used, where `a`, `b`, and `m` are complex numbers, which can be configured in the left panel.
Values that equal to zero mod `m` are shown as black boxes.

## Requirements
* python3
* pyqt5

## Screenshots
![Pascal1](https://i.imgur.com/dTUDCKr.png)

![Pascal2](https://i.imgur.com/r7G3rG6.png)
