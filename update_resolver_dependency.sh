find . -name 'addon.xml' | xargs sed -i 's;addon=\"script.module.stream.resolver.*$;addon="script.module.stream.resolver" version="1.4.0" />;'
