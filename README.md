Multiping is a tool built to ping multiple targets at the same time.<br>

It is possible to lookup the target location based on its subnet by filling the "locations_net.json" json file using the below format:<br>

{<br>
    "sites": [<br>
    	{<br>
            "site_name": "US-NewYork",<br>
            "networks": ["10.100.10.0/24", "10.100.20.0/24", "10.100.30.0/24"]<br>
        },<br>
        {<br>
            "site_name": "SITE NAME",<br>
            "networks": ["x.x.x.x/yy", "...", ...]<br>
        },<br>
        ....<br>
    ]<br>
}<br>

With -ll you enable the location lookup and the output is displayed like below:<br>

![image](https://github.com/diegobernardelli/multiping/assets/152480651/04c425b7-9ade-4948-b7f7-8d04709a2e63)<br>

Without location lookup:<br>

![image](https://github.com/diegobernardelli/multiping/assets/152480651/4c4cafca-dc7d-4b39-9e84-c60e7afbaa41)<br>

USAGE:<br>

./multiping.py -t <list of IPs space separated> <options>

options:
  -h, --help    show this help message and exit
  -t T [T ...]  In line IPv4 Targets. EG: multiping -t 8.8.8.8 1.1.1.1
  -f F          Input file with target list line by line
  -ll           enable location lookup

  Target IPs can be also imported via file by just listing them line by line
