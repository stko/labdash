TEMPDIR=/media/ramdisk
cd ..
zip -x \*/.venv/\* -x \*/.git/\* -x \*/__pycache__/\* -r $TEMPDIR/development.zip  labdash
cp labdash/raspi/bootstrap.sh $TEMPDIR/bootstrap.sh
echo "Development files are now available at http://localhost:8000/development.zip"
echo "start the installation process with"
echo "bash <(curl -s http://localhost:8000/bootstrap.sh)"
( cd $TEMPDIR ; python3 -m http.server 8000 )
# remove the temporary file again
rm $TEMPDIR/development.zip
cd labdash
