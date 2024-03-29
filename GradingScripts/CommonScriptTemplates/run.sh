echo "--------------------------------------------------"
echo "==> Compiling Your Code ..."
echo "--------------------------------------------------"

javac -d . *.java

if [ "$?" -ne "0" ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "==> FAILURE! Review error messages above."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	exit 1
fi

echo "--------------------------------------------------"
echo "==> Compile Complete"
echo "--------------------------------------------------"

echo "--------------------------------------------------"
echo "==> Running Your Code ..."
echo "--------------------------------------------------"

java Main

if [ "$?" -ne "0" ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "==> FAILURE! Review error messages above."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	exit 1
fi

echo "--------------------------------------------------"
echo "==> Run Complete"
echo "--------------------------------------------------"

