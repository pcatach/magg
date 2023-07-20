# change to base directory, no matter where you call this script from
cd "$(dirname "$0")/.."

rm -rf package/
pip3.10 install . -t package/
cd package
zip -r ../deploy/magg.zip .