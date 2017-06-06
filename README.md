# Sweet16
This code is for running my [@Pi_Borg](https://twitter.com/Pi_Borg) [Diddyborg Metal](https://www.piborg.org/diddyborg/metaledition) special edition number 16.

Requires the following to be set up:

[inputs](https://github.com/zeth/inputs) library
- `sudo pip3 install inputs`

A couple of files need to be made executable
- `chmod +x runsweet16.sh`
- `chmod +x drivesweet16.py`

And if you want to run the code on startup, ensure that the __pi__ user is logged in on when the Pi starts, and add edit cron with:
- `crontab -e`

Adding the line
- `@reboot \home\pi\Sweet16\runSweet16.sh`
