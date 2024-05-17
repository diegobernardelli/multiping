#!/usr/bin/env python3

import os
import sys
import subprocess
import concurrent.futures
import argparse
import time
import re
import json
from netaddr import IPNetwork, IPAddress

class TargetIPv4:
	def __init__(self, ip, stats, totPkts, failedPkts):
		self.ip = ip
		self.stats = stats
		self.totPkts = totPkts
		self.failedPkts = failedPkts
		self.location = ""

	def appendStat(self, result):
		self.stats = self.stats + result

	def clearStats(self):
		self.stats=""

	def addProbe(self):
		self.totPkts = self.totPkts + 1

	def addFailedProbe(self):
		self.failedPkts = self.failedPkts + 1
	
	def clearOldestStat(self):
		self.stats = self.stats[1:]

	def keepLastNstats(self, n):
		self.stats = self.stats[-n:]

	def getLastNstats(self, n):
		return self.stats[-n:]

	def setLocation(self, siteName):
		self.location = siteName

def pinger(ip):

	reachable = True
	try:
		response = subprocess.check_output( ['ping', '-c', '1', '-W', '1', ip], stderr=subprocess.STDOUT, universal_newlines=True)
	except Exception:
		reachable = False

	if reachable and "0 packets received" not in response:
		time.sleep(1)
		return "!"
	else:
		time.sleep(1)
		return "."

def percentage(part, total):
  return round(100 * float(part)/float(total), 2)


gRows, gCols = os.popen('stty size', 'r').read().split()

def outputPrinter():
	#os.system('clear')
	global gRows
	global gCols

	tmpRows, tmpCols = os.popen('stty size', 'r').read().split()
	
	if gRows == tmpRows and gCols == tmpCols:
		print("\033[%d;%dH" % (0,0))
	else:
		gRows = tmpRows
		gCols = tmpCols
		os.system('clear')
		print("\033[%d;%dH" % (0,0))

	iterminalCols = int(tmpCols)
	if iterminalCols <= 120:
		maxStats = 30
	else:
		maxStats = iterminalCols - 94

	statsSeparator = "-" * maxStats

	separator = "+-------------------------+------------------+-" + statsSeparator + "-+----------+----------+--------------+"
	printfFormat = "|%-25s|%-18s|%-" + str(maxStats + 2) + "s|%-10s|%-10s|%-14s|"

	print(separator)
	print(printfFormat % ("Location","IPv4","Stats", "N Probes", "N TimeOuts", "Packet Loss"))
	print(separator)

	for target in targetList:
		packetsLoss="0.0%"
		if target.failedPkts > 0:
			packetsLoss = str(percentage(target.failedPkts, target.totPkts)) + "%"

		#if the stats string is shorter than 270 chars print the maximum latest visible probes (based on maxstats) 
		#otherwise keep the maximum latest visible probes (based on max stats) and then print them
		outStats = ""
		if len(target.stats) < 270:
			outStats = target.getLastNstats(maxStats)
		else:
			target.keepLastNstats(maxStats)
			outStats = target.getLastNstats(maxStats)

		print(printfFormat % (target.location,target.ip,outStats,target.totPkts, target.failedPkts, packetsLoss))
		print(separator)
	return 0

def outputPrinterNoLocation():

	global gRows
	global gCols

	tmpRows, tmpCols = os.popen('stty size', 'r').read().split()
	
	if gRows == tmpRows and gCols == tmpCols:
		print("\033[%d;%dH" % (0,0))
	else:
		gRows = tmpRows
		gCols = tmpCols
		os.system('clear')
		print("\033[%d;%dH" % (0,0))

	iterminalCols = int(tmpCols)
	if iterminalCols <= 100:
		maxStats = 40
	else:
		maxStats = iterminalCols - 68

	statsSeparator = "-" * maxStats

	separator = "+------------------+-" + statsSeparator + "-+----------+----------+--------------+"
	printfFormat = "|%-18s|%-" + str(maxStats + 2) + "s|%-10s|%-10s|%-14s|"

	print(separator)
	print(printfFormat % ("IPv4","Stats", "N Probes", "N TimeOuts", "Packet Loss"))
	print(separator)

	for target in targetList:
		packetsLoss="0.0%"
		if target.failedPkts > 0:
			packetsLoss = str(percentage(target.failedPkts, target.totPkts)) + "%"

		outStats = ""
		if len(target.stats) < 270:
			outStats = target.getLastNstats(maxStats)
		else:
			target.keepLastNstats(maxStats)
			outStats = target.getLastNstats(maxStats)

		print(printfFormat % (target.ip,outStats,target.totPkts, target.failedPkts, packetsLoss))
		print(separator)
	return 0

def targetListChecker():
	ipAddressCheck = None

	for target in targetList:
		ipAddressCheck = re.search("([1-2]?[0-9]{1,2})\.([1-2]?[0-9]{1,2}\.){2}([1-2]?[0-9]{1,2})", target.ip)
		if ipAddressCheck == None:
			ipAddressCheck = None
			targetList.remove(target)
			print("[*] This is not an IPv4 Adrress: " + target.ip + " removed from target list")

def locationLookUp():
	db = []

	try:
		file = open("locations_net.json", "r")
		sfile = file.read()
		db = json.loads(sfile, strict=False)
	except Exception as e:
		print("[!] Failed loading Json DB exception: " + str(e))

	for target in targetList:
		matchcount = 0
		for site in db["sites"]:
			#print(site["site_name"])
			for net in site["networks"]:
				if IPAddress(target.ip) in IPNetwork(net):
					#print("Match " + site["site_name"] + " " + net)
					matchcount += 1 
					target.setLocation(site["site_name"])
					break
		if matchcount == 0:
			target.setLocation("404 Location not found")


def tableSizer():
	sizes = os.popen('stty size', 'r').read().split()
	nCols = sizes[1]
	return nCols


targetList = []
def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('-t', type=str, nargs='+', help="In line IPv4 Targets. EG: multiping -t 8.8.8.8 1.1.1.1")
	parser.add_argument('-f', type=str, nargs=1, help="Input file with target list line by line")
	parser.add_argument('-ll', action='store_true', help="enable location lookup")
	
	#print(sys.argv)
	if len(sys.argv) == 1:
		print("[*] NO valid argument, printing help")
		parser.print_help()
		quit()
	
	args = parser.parse_args()

	if args.t == None and args.f == None:
		print("[!] You must set at least 1 argument -f or -t. Use -h to see help.")
		quit()
	elif args.t != None:
		
		lTargets = args.t
		
		for arg in lTargets:
			targetList.append(TargetIPv4(arg,"", 0, 0))
	
	locationLookupEnable = False
	if '-ll' in sys.argv or '--location-lookup' in sys.argv:
		locationLookupEnable = True

	if args.f != None:
		filename = args.f[0]
		try:
			file = open(filename, 'r')
			for line in file:
				targetList.append(TargetIPv4(line.replace('\n', ''),"", 0, 0))
		except Exception as e:
			print("[!] Failed to open selected file Exception: " + str(e))
			if len(targetList) == 0:
				print("[*] No targets quitting...")
				quit()

	targetListChecker()
	locationLookUp()
	
	nWorkers = len(targetList)
	if nWorkers > 70:
		nWorkers = 70

	os.system('clear')

	while True:

		with concurrent.futures.ThreadPoolExecutor(max_workers=nWorkers) as executor:
			future_to_dev = {executor.submit(pinger, target.ip): target for target in targetList}
			for future in concurrent.futures.as_completed(future_to_dev):
				currTarget = future_to_dev[future]
				try:
					data = future.result()
					i = [target.ip for target in targetList].index(currTarget.ip)
					targetList[i].appendStat(str(data))
					targetList[i].addProbe()
					if str(data) == ".":
						targetList[i].addFailedProbe()

				except Exception as exc:
					print("Exception: " + exc)
		if locationLookupEnable:
			outputPrinter()
		else:
			outputPrinterNoLocation()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
