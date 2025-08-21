# sb4dfritz - Specialized Functionality for AVM FRITZ! Home Automation Systems

This is mainly a learning project for object oriented programming and network communication using Python. It provides specialized functionality for controlling smart plugs in home automation systems within an AVM FRITZ!Box home network.

* For a (virtual) demonstration, please run the script `sb4dfritz_demo.py`.
* The main features are provided in `sb4dfritz.py`, currently building on the `fritzconnection` library.
* The script `sb4dfritz_test.py` provides virtual simulations of electrical appliances connected to AVM FRITZ! smart plugs.
* In progress: `sb4dfritzlib` is a self-written library meant to replace `fritzconnection` in future versions. 

`sb4dfritzlib` already implements the TR-064 and AHA-HTTP interfaces provided by AVM. I plan to add further functionality, icluding a simple method to toggle between automatic and manual switching. Since the latter is not available via the official APIs, a certain amount of trickery is needed (essentially reverse engineering the behavior of the web-interface). 