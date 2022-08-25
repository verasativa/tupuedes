_Tú puedes_: an open source smart gym
==============================
_Tú puedes_ will count and correct you exercises using computer vision. _Tú puedes_ calculate you body pose and training equipment position using live computer vision, to count you repetitions, alert you on mistakes, track and motivate you to go further.
## Install

```bash
conda create -n tupuedes310 python=3.10
conda activate tupuedes310
git clone git@github.com:verasativa/tupuedes.git
cd tupuedes 
pip install -e .

```

## Usage
Usage like
```bash
tupuedes train
```
or 
```bash
tupuedes train --source=3
```

where you source is 0 for default web cam (other ints for other webcams), or a network camera like http://192.168.1.155:8080/video
### Sharing a camera from phone
 - Android
   - IP Webcam dose the work nice

## Philosophy
_Tú puedes_ could be **eventually** run on mobile devices, eventually. But before product-market fit, we rather to iterate fast; that why:
 - We manage video trough openCV from python
 - We provide a full pandas dataframe with structured data to exercise classes

_Tú puedes_ would like to be open source and commercial, like:
 - anaconda
 - posthog

_Tú puedes_ would like to be a feminist artifact:
 - _how this is empowering women?_ is **always** a good question
 - propietary software is kind patriarchal
 - we 

## dev goals
### To públic access
 - 1 naive working exercise
 - home dir writting (mac/windows/linux)
 - nice readme
   - videos
   - conda set up
   - windows / mac / linux
   - vision / press realease
     - import this
     - feminist
 - discord channel?
 - setting metrics
 - pass the source trough **kargs to super().__init__() in the fancy way at all pipeline child classes
### Maybe late
 - config manager