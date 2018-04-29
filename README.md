# GrassyKnoll

What is it?
----

Anemometer-responsive LED matrix animations on a Raspberry Pi, designed to look like grass blowing in the wind. 

![grassy](http://i.imgur.com/TUlSLOH.png)
![grassy](http://i.imgur.com/OSjcz6f.jpg)

And a bonus photo with our art neighbor Stan's totally amazing inflatables. 

![grassy](http://i.imgur.com/XniOTVK.jpg)

See it in action: https://vimeo.com/174775305

Hardware requirements: a raspberry pi connected to a chain of four 32x32 RGB LED matrix panels (e.g. adafruit) using a matrix hat (adafru.it/2345). The panels must be arranged in a grid like so:

```
[3][4]
[2][1]
```
Signal enters through panel 1 and snakes through the others in order. The animation uses simplex noise to define the pattern of color. There's a blue animation and a yellow animation; when there's no wind, the two are in sync and the color appears as shades of green. Increasing signal from the anemometer causes the blue and yellow to become out of sync, visually "splitting" the green color into its constituent blue and yellow components.

Anemometer: any reed-switch anemometer such as http://www.maplin.co.uk/p/maplin-replacement-anemometer-for-n96gy-n09qr. Wire into one of Pi's GPIO pins and ground pins. The channel pin in the code should match the pin in the hardware. 

Software requirements: Tested on Raspbian. Requires Adafruit raspberry pi RGB matrix control code (https://github.com/adafruit/rpi-rgb-led-matrix) and Bibliopixel animation library (https://github.com/ManiacalLabs/BiblioPixel). 

Some useful reference learning:

- [How does a reed switch anemometer work?](http://www.explainthatstuff.com/anemometers.html)

- [How does simplex noise work?](https://en.wikipedia.org/wiki/Simplex_noise) 

- [How do LED matrix panels work?](https://learn.adafruit.com/32x16-32x32-rgb-led-matrix/)
