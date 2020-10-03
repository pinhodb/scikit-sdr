# scikit-sdr

**scikit-sdr** is a Python 3 library that provides algorithms for building digital communication systems and for experimenting with DSP and SDR.
The structure of the library is as follows:

- ``sksdr``:&nbsp;source code for algorithms
- ``tests``:&nbsp;units tests using the pytest framework
- ``demo``:&nbsp;demonstrations using Jupyter notebooks
- ``gnuradio``:&nbsp;GNU Radio wrappers contained in an OOT module (``gnuradio/gr-grsksdr``) and some demonstration flowgraphs (``gnuradio/demo``)
- ``docs``:&nbsp;Sphinx documentation

Some of this work as been inspired and/or based of other libraries such as [komm](https://github.com/rwnobrega/komm) and [scikit-dsp-comm](https://github.com/mwickert/scikit-dsp-comm). Other sources include the books:
-  "Digital Communications: A Discrete-time Approach" by Michael Rice
- "Understanding Digital Signal Processing" by Richard G. Lyons
- "Digital Signal Processing: Principles, Algorithms and Applications" by John G. Proakis and Dimitris G. Manolakis

