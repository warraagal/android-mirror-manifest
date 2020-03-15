The mirror manifest can be used to create a local mirror of official Android source repos using the following commands

```sh
$ mkdir -p /usr/local/aosp/mirror
$ cd /usr/local/aosp/mirror
$ repo init -u https://android.googlesource.com/mirror/manifest --mirror
$ repo sync
```

The local mirror can then be used like this

```sh
$ mkdir -p /usr/local/aosp/master
$ cd /usr/local/aosp/master
$ repo init -u /usr/local/aosp/mirror/platform/manifest.git
$ repo sync
```

The [official mirror manifest](https://android.googlesource.com/mirror/manifest) contains all the projects that have been part
of some Android release, even if they were removed in newer releases. This makes a complete mirror unnecessarily huge.

The downsized manifest file [default.xml](https://github.com/rounaka/android-mirror-manifest/blob/master/default.xml) only contains
projects used in **Android Oreo** (Android 8) and newer versions of Android. It was generated using the Python program
[prunemirrormanifest.py](https://github.com/warraagal/android-mirror-manifest/blob/master/prunemirrormanifest.py) like this
```sh
$ python3 prunemirrormanifest.py
The following Android releases are available.

['2.2.3', '2.3.6', '2.3.7', '4.0.1', '4.0.2', '4.0.3', '4.0.4', '4.1.1', '4.1.2', '4.3.1', '4.4.1', '4.4.2', '4.4.3', '4.4.4', '5.0.0', '5.0.1', '5.0.2', '5.1.0', '5.1.1', '6.0.0', '6.0.1', '7.0.0', '7.1.0', '7.1.1', '7.1.2', '8.0.0', '8.1.0', '9.0.0']
Enter the oldest desired release : 8.0.0
```

To use this smaller mirror manifest just replace the URL _https://android.googlesource.com/mirror/manifest_ with _https://github.com/warraagal/android-mirror-manifest_
in the mirroring step above

If you also want to build Android releases older than Oreo, then fork this repository, choose an older release when running _prunemirrormanifest.py_
