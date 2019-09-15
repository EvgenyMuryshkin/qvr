# Quokka + VR Streaming Project
Quick and dirty integration prototype of Raspberry Pi, FPGA, and Unity3D for image streaming from camera to headset with axis control - a weekend project to hack around.

Watch demo on YouTube - https://www.youtube.com/watch?v=7mvU3ZHIpUw

[![Demo](https://img.youtube.com/vi/7mvU3ZHIpUw/0.jpg)](https://www.youtube.com/watch?v=7mvU3ZHIpUw)

# Setup

We are going to build integrated system like that

![Setup](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/setup.png "Setup")

# What is it doing?
* Camera fixture is made of 3 servos to give 3 axis control for direction of view
* Pi is running web server API to serve images and receive servos data
* VR headset displays image from Pi camera by periodically polling for latest frame with augmented face detection layer. 
* VR headset periodically sends internal camera direction to Pi as json payload e.g. { x: 45, y: -45, z: 0 }
* Pi translates incoming camera direction into servo rotation data.
* Pi sends servos data to FPGA using UART with ad-hoc protocol as byte array **\[marker, servo1, servo2, servo3]** e.g. \[255, 135, 45, 90\]
* FPGA reads data from UART and sets values for each servo
* FPGA runs parallel servo drivers and each driver sends PWM signal to attached servo motor

# Prerequisites
To make this project, you will need bunch of hardware, please run through setup and make sure you got all required bits and pieces.

Choose FPGA vendor and dev board. There are plenty around, wide range on boards from proprietary and open source projects.

I designed my own board for Quokka Toolkit and using it in this project. 
(https://www.kickstarter.com/projects/quokka-robotics/quokka-fpga-iot-controller)

![Quokka Board](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/quokka.png "Quokka Board")

Sample design will also work on any device of your choice.

# Installing and Assembling 

## FPGA

* FPGA board with 2000+ LUTs (I am using my own board, but any will do, nothing specific is needed from it, bare metal and couple of GPIOs) (https://www.ebay.com.au/sch/i.html?_nkw=FPGA+development+board)
* 3 servo motors MG996R (https://www.ebay.com.au/sch/i.html?_nkw=mg996r)
* Breadboard and assorted wiring (M-M, F-F, M-F) 
* Power distribution board. I did this small distribution board, it also can be done using breadboard.

![PDB](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/pdb.png "PDB")

![PDBImg](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/pdbimg.png "PDBImg")

Choose some pins on your board to be used for servo control and connect things together.

![FPGA](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/fpga.png "FPGA")

Once you have all connected, you need to make sample design for FPGA.

**I am creating a toolkit for quick FPGA development using C# language instead of traditional HDL languages. (https://github.com/EvgenyMuryshkin/QuokkaEvaluation)**


**FPGA part is built using components that already available as part of my toolkit. All required drivers are included in this tutorial, so no need to download anything in addition. Please refer to main toolkit page for more examples and drivers** 

NOTE: example is using Verilog. VHDL is also supported with configuration change in quokka cli

* Clone this repo into some directory e.g. qvr
* Open solution from **qvr\fpga\qvr.sln** in Visual Studio
* Edit **qvr\verilog.json** configuration file and set your board clock rate in Hz
* Run **cli** project, it is already configured for sample parameters. You should see console output like next

![CLI](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/cli.png "CLI")

* Create new project in **qvr\fpga\Verilog** folder using EDA software for your device
* Add all \*.v files from Verilog folder and from *generated* subfolder (sample project for Quokka board already provided for reference, if you use similar device, project can be reused).

There are two controller - Main and Test. 

**Main controller** is reading data from UART and applying it to servos

**Test controller** is self contained, driving servos from side to side, can be used to test FPGA setup independently

* Set top-level controller, run compilation, pin assignment, synthesys and programming. 
You should get working FPGA device if everything was setup properly. 
If it does not work - please refer to troubleshooting section and have fun debugging :) 

* Use Test controller to check your setup, then switch to main contoller and carry on with the tutorial

Watch test controller demo on YouTube - https://www.youtube.com/watch?v=JQwfiyl2v78

[![Demo](https://img.youtube.com/vi/JQwfiyl2v78/0.jpg)](https://www.youtube.com/watch?v=JQwfiyl2v78)

## Raspberry Pi

* Raspberry Pi 4 (might well run on 3, but I did not test) (https://core-electronics.com.au/raspberry-pi-4-model-b-2gb.html)
* Small fan (optional, in case your Pi overheats when running face detection)
* Camera module with long cable 30+ cm (https://core-electronics.com.au/raspberry-pi-camera-board-v2-8-megapixels-38552.html)
* Intel Neural Computing Stick 2 if you want to apply face detection or other NN (https://www.ebay.com.au/sch/i.html?_nkw=Intel+Movidius+Neural+Compute+Stick+2)
* USB to TTL UART cable (https://www.ebay.com.au/sch/i.html?_nkw=USB+UART+Cable)


My final setup looks like that
![PI](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/pi.png "PI")

Most of the required packages already come with NOOBS disto, which I am using. 
If you have another setup, you need to install missing packages as you go.

* Connect camera cable, neural stick, fan and UART extension wires
* Configure and update Pi, enable SSH, Camera and UART.
* Set fixed IP (e.g. 192.168.1.201) so unity app can find it all the times
* Install OpenVINO if using image recognition (https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html) (https://www.pyimagesearch.com/2019/04/08/openvino-opencv-and-movidius-ncs-on-the-raspberry-pi/)
* Clone this repo into home directory ~/qvr
```
cd ~
git clone https://github.com/EvgenyMuryshkin/qvr.git
```
* Run setup to download nets and configure environment
```
cd ~/qvr/pi
chmod 777 setup
./setup
source ~/.bashrc
```

Setup script downloads nets and creates alias **snn** to run streaming server. If all went well, you should be able to run it from terminal

```
snn
```

* Run **snn** to start web server and image processing, you should see next console output
![SNN](https://github.com/EvgenyMuryshkin/VRStreaming/blob/master/images/snn.png "SNN")
* Test connection from PC browser by navigating to << PI_ADDRESS >>:8000 (http://192.168.1.201:8000)

Pi is all set up and ready to go

## Camera fixture

* Robotic Arm Kit to make fixture for camera (https://www.ebay.com.au/sch/i.html?_nkw=ROT2U)

Assembly something like that with parts from ROT2U kit. 
I tried to keep all axis close together so it moves similar to head movement.
Make sure it is balanced and does not tip over when rotates.

![Fixture](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/fixture.png "Fixture")

## PC
* PC with Windows Mixed Reality
* VR headset (emulator will work as well, but feels better in headset)
* Microsoft .NET Core 2.2 (https://dotnet.microsoft.com/download/dotnet-core/2.2)
* Microsoft Visual Studio 2019 Community (https://visualstudio.microsoft.com/vs/)
* Unity3D 2019.2 (https://store.unity.com/products/unity-personal)
* VS Code Insiders with Remote SSH extension (https://code.visualstudio.com/insiders/)
* EDA for FPGA design for your board

Install and configure all required software, make sure you are familiar with how to open projects, build and run tools etc.

I am using VSCode Remote SHH on PC to edit and run software on Pi side, it is super awesome and time saving tool.
![VSCode](https://github.com/EvgenyMuryshkin/qvr/blob/master/images/vscode.png "VSCode")

If you don't have a VR headset, please refer to instructions on how to emulate it inside Mixed Reality Portal.


* Open unity project from **qvr\unity** in Unity Hub
* Install JSON.NET asset in Unity Asset Store (https://assetstore.unity.com/packages/tools/input-management/json-net-for-unity-11347)
* Download and import Mixed Reality Foundation Assets from here, apply and accept all confirmation dialogs  (https://github.com/microsoft/MixedRealityToolkit-Unity/releases/tag/v2.0.0)
* Apply Microsoft Mixed Reality to Scene (Menu => Mixed Reality Toolkit => Add to Scene and Configure => Default Profile)
* Run scene, you should see initial image from Pi camera
* Move camera\headset around, servos should respond and change direction of the camera


That is about it, hope you have fun and learn new thing while doing this small exercise

# Challenges

## Challenge 1
Disable face detection to increase frame rate.

Replace polling of image with direct handling of mjpg to get smooth video stream from Raspberry Pi

See links for reference

(https://answers.unity.com/questions/1228247/unity-5-c-simple-html-viewer.html)

(https://github.com/DanielArnett/SampleUnityMjpegViewer)

## Challenge 2

Modify servo angle adjustment logic in FPGA to make it as real time as possible to actual head movement

## Challenge 3

Add VR controllers handling and wheel base to Pi and FPGA so they can be moved around.

# Troubleshooting

Most of the issues can be found on Stack Overflow. Many of them related to missing packages, lack of permissions, different hardware configuration. If you encounter any issues, please create PR so we can update this section accordigly.


| Problem | Solution |
| ------- | ---------|
| No UART communications | Make sure that RXD-TXD pairs are connected property, try to make loopback (connect it to itself) to test it locally |
| Pi server does not receive data on UART | If you don't have permission to serial port, it might just silently not work, no errors, no crashes, no data. One of provided solutions might work for you (https://lb.raspberrypi.org/forums/viewtopic.php?t=197823) |
| No image from camera appears in Unity | **snn** server is not running in Pi - run server and check stream in browser |
| No image from camera appears in Unity | Make sure that you have correct IP address of Pi in component. Open Assets/AxisComponent.cs and edit Pi address if is not correct |



# Contacts
Follow me on Twitter - https://twitter.com/ITMayWorkDev

E-mail: evmuryshkin@gmail.com


