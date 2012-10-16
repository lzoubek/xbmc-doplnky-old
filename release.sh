#!/bin/bash
# taken grom xbmc-czech-sf.net

TOOLS=$(dirname "$0")

BUILD_DIR=repo
echo "Cleaning up *.pyc files.."
find . -name '*.pyc' | xargs rm -f

if [ -z $1 ];
then
	addons=$(ls -l | grep "^d" | gawk -F' ' '{print $9}')
else
	addons=$1
fi

for addonFile in $addons ; do
    dirname=$addonFile
    if [ ! -f $addonFile/addon.xml ] ; then
	echo "$addonFile/addon.xml does not exist, skipping"
	continue
    fi
    addon_id=$("$TOOLS/get_addon_attribute" "$addonFile/addon.xml" "id")
    addon_version=$("$TOOLS/get_addon_attribute" "$addonFile/addon.xml" "version")

    if [ -z "$addon_id" ] ; then
        echo "Addon id not found!" >&2
        exit 1
    fi

    if [ -z "$addon_version" ] ; then
        echo "Addon id not found!" >&2
        exit 2
    fi

    target_dir="$BUILD_DIR/$addon_id"
    if [ ! -d "$target_dir" ] ; then
        mkdir "$target_dir"
    fi

    echo "Packing $addon_id $addon_version"

    # make package
    package="$target_dir/$addon_id-$addon_version.zip"
    if [ -e "$package" ] ; then
        rm "$package"
    fi
    zip -FS -r "$package" "$dirname" -x "*.py[oc] *.sw[onp]" ".*"

    # copy changelog file
    changelog=$(ls "$dirname"/[Cc]hangelog.txt)
    if [ -f "$changelog" ] ; then
        cp "$changelog" "$target_dir"/changelog-$addon_version.txt
    fi

    # copy icon file
    icon="$dirname"/icon.png
    if [ -f "$icon" ] ; then
        cp "$icon" "$target_dir"/
    fi
    echo
done
echo "Regenerate addons.xml"
python addons_xml_generator.py
echo "Done"
