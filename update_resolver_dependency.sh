find . -name 'addon.xml' | xargs sed -i 's;addon=\"script.module.stream.resolver.*$;addon="script.module.stream.resolver" version="1.6.5" />;'
#find . -name 'addon.xml' | xargs sed -i 's;addon=\"xbmc\.python.*$;addon="xbmc.python" version="2.0" />;'
