#!/bin/sh


##############################################################
# Bash port of BTC's RAW BPI Certificate extraction tool for #
#   extracting certificates and keys from BPI binary blobs   #
#   using binwalk and openssl                                #
##############################################################


#=================# 
# Argument checks #
#=================#
dt=$(date '+%Y/%m/%d %R:%S');
if [ -z "$*" ]; then 
	echo "Usage: ./bpi-extract.sh FILE";
	exit 0;
fi;
if ! test -f $1; then
	echo "$dt File not found";
	exit 0;
fi;


#======================================#
# Check all tools needed are installed #
#======================================#
ps="binwalk openssl mktemp basename dirname awk tr cat test date grep dd stat mkdir cat rm echo mv"
for i in $ps; do
	if ! command -v $i 1>/dev/null; then
		echo "Command $i not installed";
		exit 0;
	fi;
done;


#=======================#
# Parse files from blob #
#=======================#
tf=$(mktemp /dev/shm/tmp.XXXXXXXXX);
ed=$(dirname $1)
fn=$(basename $1)
echo "Plastic's BCM Raw BPI Certificate extraction tool Ver 1.0";
echo "$dt Extracting $ed/$fn";
binwalk -e $1 -C $ed 1>$tf;
ko=$(cat $tf | awk '(NR==4){ print $2 }' | tr -d 0x);
kt=$(cat $tf | awk '(NR==5){ print $2 }' | tr -d 0x);
co=$(cat $tf | awk '(NR==6){ print $2 }' | tr -d 0x);
ct=$(cat $tf | awk '(NR==7){ print $2 }' | tr -d 0x);


#===========================================================#
# Check that the blob was valid and produced expected files #
#===========================================================#
cs="${ko}.key ${kt}.key ${co}.crt ${ct}.crt";
for i in $cs; do
	if ! test -f $ed/_$fn.extracted/$i; then
		rm $tf; rm -r _$1.extracted 2>/dev/null;
		echo "$dt Corrupted file";
		exit 0;
	fi;
done;


#=========================================#
# Unnecessary output (because BTC had it) #
#=========================================#
echo "$dt Read version: 1"
echo "$dt";


#================================================================#
# Extract MAC and create new directory, remove existing if found #
#================================================================#
ma=$(openssl x509 -inform der -in $ed/_$fn.extracted/$co.crt -noout -text | grep "CN = " | awk '(NR==2){ print $NF }' | tr -d :);
if test -d $ed/$ma; then
	rm -r $ed/$ma;
fi;
mkdir $ed/$ma;
echo "$dt $ed/$ma/";


#====================#
# Extract public key #
#====================#
openssl rsa -inform der -in $ed/_$fn.extracted/$ko.key -RSAPublicKey_out -outform der -out pub.key 2>/dev/null;
echo "$dt Writing pub.key, size: $(stat --format='%s' pub.key)";


#=====================#
# Extract private key #
#=====================#
openssl rsa -inform der -in $ed/_$fn.extracted/$ko.key -outform der -out private.key 2>/dev/null;
echo "$dt Writing private.key, size: $(stat --format='%s' private.key)";


#==================#
# Extract root key #
#==================#
rs=$(($(stat --format='%s' private.key) + 28));
dd if=$ed/_$fn.extracted/$ko.key of=root.key bs=1 skip=$rs count=270 2>/dev/null;
echo "$dt Writing root.key, size: $(stat --format='%s' root.key)";


#=================#
# Extract cm cert #
#=================#
openssl x509 -inform der -in $ed/_$fn.extracted/$co.crt -outform der -out cm.cer;
echo "$dt Writing cm.cer, size: $(stat --format='%s' cm.cer)";


#=================#
# Extract ca cert #
#=================#
openssl x509 -inform der -in $ed/_$fn.extracted/$ct.crt -outform der -out ca.cer;
echo "$dt Writing ca.cer, size: $(stat --format='%s' ca.cer)";


#=====================#
# Clean up temp files #
#=====================#
mv *.key $ed/$ma; mv *cer $ed/$ma;
rm -r $ed/_$fn.extracted; rm $tf;


#============================#
# Get combined size of files #
#============================#
sf=0;
for i in $ed/$ma/*; do sf=$(($sf + $(stat --format='%s' $i))); done;
echo "$dt Total size: $sf"
