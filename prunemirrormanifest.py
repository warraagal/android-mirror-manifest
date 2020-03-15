import os
import requests
import xml.etree.ElementTree as ET
import sys
import base64
import subprocess
import re

try:
    subprocess.check_output("git --version", shell=True)
except subprocess.CalledProcessError as exc:
    print("git not found. Exiting")
    sys.exit(1)
try:
    manifestRepoRefs = subprocess.check_output("git ls-remote --refs https://android.googlesource.com/platform/manifest",
            universal_newlines=True, shell=True)
except subprocess.CalledProcessError as exc:
    print("Unable to fetch refs from the platform manifest repo. Exiting.")
    sys.exit(exc.returncode)

manifestRepoTags = []
androidReleases = set()
for line in manifestRepoRefs.splitlines():
    columnTwo = line.split()[1]
    if(re.match('refs/tags/.*', columnTwo)):
        manifestRepoTags.append(columnTwo.split('/')[2])
# print(manifestRepoTags)
for tag in manifestRepoTags:
    matchObj = re.match(r'android\-([1-9][0-9]{0,1}\.[0-9]\.[0-9])_r[1-9]+$', tag)
    if matchObj:
        androidReleases.add(matchObj.group(1))
androidReleases = list(androidReleases)
androidReleases.sort(key=lambda s: [int(u) for u in s.split('.')])
print("The following Android releases are available.\n")
print(androidReleases)
oldestRequiredRelease = input('Enter the oldest desired release : ')
if oldestRequiredRelease not in androidReleases:
    print("Invalid value entered. Exiting")
    sys.exit(1)
androidReleases = androidReleases[androidReleases.index(oldestRequiredRelease):]
revisionsToDownload = ['master']

for release in androidReleases:
    revisions = set()
    for tag in manifestRepoTags:
        matchObj = re.match(r'android\-' + release + '_r([1-9]+)', tag)
        if matchObj:
            revisions.add(int(matchObj.group(1)))
    revisions = list(revisions)
    revisions.sort()
    if len(revisions) >= 10:
        revisions = revisions[-10:]
    for revision in revisions:
        revisionsToDownload.append('android-' + release + '_r' + str(revision))
print(revisionsToDownload)

platformManifestURL = 'https://android.googlesource.com/platform/manifest/+/master/default.xml?format=TEXT'
mirrorManifestURL = 'https://android.googlesource.com/mirror/manifest/+/master/default.xml?format=TEXT'
manifestXMLFiles = []
mirrorManifestFileName = 'mirror.xml'

# Download manifest XMLs for releases and also master manifest
for release in revisionsToDownload:
    url = platformManifestURL.replace('master', release)
    print(url)
    response = requests.get(url)
    if response.status_code != 200:
        print("Unable to download ", url, " return code: ", response.status_code)
        sys.exit(1)
    with open(release + ".xml", 'wb') as xmlFile:
        xmlFile.write(base64.b64decode(response.content))
        manifestXMLFiles.append(release + ".xml")

setOfProjectNames = set()

with open(mirrorManifestFileName, 'wb') as mirrorFile:
    mirrorFile.write(base64.b64decode(requests.get(mirrorManifestURL).content))

for fileName in manifestXMLFiles:
    tree = ET.parse(fileName)
    print('Parsed XML file ', fileName)
    treeRoot = tree.getroot()
    for topChild in treeRoot:
        if topChild.tag == 'project':
            if topChild.attrib.get('name') is not None:
                name = topChild.attrib.get('name')
                if name not in setOfProjectNames:
                    setOfProjectNames.add(topChild.attrib.get('name'))

# All project names have been added. But "platform/manifest" needs to be added separately
setOfProjectNames.add("platform/manifest")

# Parse the official mirror manifest and remove unneeded project names
defaultTree = ET.parse(mirrorManifestFileName)
defaultTreeRoot = defaultTree.getroot()
for child in defaultTreeRoot.findall('project'):
    if child.tag == 'project':
        if child.attrib.get('name') is not None:
            name = child.attrib.get('name')
            if name not in setOfProjectNames:
                defaultTreeRoot.remove(child)

# Make the fetch url explicit
for child in defaultTreeRoot.findall('remote'):
    if child.attrib.get("fetch") == "..":
        child.attrib["fetch"] = "https://android.googlesource.com/"
defaultTree.write('default.xml', encoding='UTF-8', xml_declaration=True)

# delete release manifest files
for fileName in manifestXMLFiles:
    os.remove(fileName)
# delete mirror manifest file
os.remove(mirrorManifestFileName)
