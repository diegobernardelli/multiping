Multiping is a tool built to ping multiple targets at the same time.<br>

It is possible to lookup the target location based on its subnet by filling the "locations_net.json" json file using the below format:<br>

<code>
{
    "sites": [
        {
            "site_name": "US-NewYork",
            "networks": ["10.100.10.0/24", "10.100.20.0/24", "10.100.30.0/24"]
        },
        {
            "site_name": "SITE NAME",
            "networks": ["x.x.x.x/yy", "..."]
        }
    ]
}
</code>

With -ll you enable the location lookup and the output is displayed like below:<br>

![image](https://github.com/diegobernardelli/multiping/assets/152480651/04c425b7-9ade-4948-b7f7-8d04709a2e63)<br>

Without location lookup:<br>

![image](https://github.com/diegobernardelli/multiping/assets/152480651/4c4cafca-dc7d-4b39-9e84-c60e7afbaa41)<br>

USAGE:<br>

./multiping.py -t <list of IPs space separated> <options><br>

![image](https://github.com/diegobernardelli/multiping/assets/152480651/b46d5323-4dde-4742-a6a1-f5a1618ffdd4)

Target IPs can be also imported via file by just listing them line by line<br>
