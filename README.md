# sb4dfritz
This project is mainly an exercise an object oriented programming in Python, but it also has real life applications. It provides customized functionality for a smart plug in my home automation setup. 

* For a (virtual) demonstration, please run the script `sb4dfritz_demo.py`.
* The main features are provided in `sb4dfritz.py` build on the `fritzconnection` API.
* The script `sb4dfritz_test` provides virtual simulations of electrical appliances connected to AVM FRITZ! smart plugs.
* [This notebook](https://github.com/SB4D/sb4dfritz/blob/main/Notebooks/NOTES--writing_a_test_mode.ipynb) contains extensive notes on the development of `sb4dfritz_test` and the quirks of AVM FRITZ! smart plugs.

In the future, I plan to add further functionality, in particular, a simple option to toggle between automatic and manual switching. This will also be an exercise in network communication using the SOAP protocol (see [here](https://github.com/SB4D/sb4dfritz/blob/main/Notebooks/NOTES--toggle_automatic_switching.ipynb) for more notes on this issue). 
