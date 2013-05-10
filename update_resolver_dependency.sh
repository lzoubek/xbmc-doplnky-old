find . -name 'addon.xml' | xargs sed -i 's;addon=\"script.module.stream.resolver.*$;addon="script.module.stream.resolver" version="1.5.6" />;'
#find . -name 'addon.xml' | xargs sed -i 's;addon=\"xbmc\.python.*$;addon="xbmc.python" version="2.0" />;'
